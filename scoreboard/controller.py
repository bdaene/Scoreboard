import random
from itertools import chain, repeat, permutations
from typing import Iterable

from scoreboard import models
from scoreboard.config import config

DEFAULT_SCORE = (0,) * len(config().tournament.score)


def get_total(scores):
    return tuple(map(sum, zip(DEFAULT_SCORE, *scores)))


async def _get_players_info(tournament: models.Tournament):
    player_scores = {}
    player_seats = {}
    await tournament.fetch_related('players', 'rounds__scores__player', 'rounds__tables__seats__player')
    for round in tournament.rounds:
        for score in round.scores:
            player_scores.setdefault(score.player, []).append(score.get_sort_key())
        for table in round.tables:
            for seat in table.seats:
                player_seats.setdefault(seat.player, set()).add(seat.number)

    players = set(tournament.players)
    players_total_score = {player: get_total(player_scores.get(player, [])) for player in players}
    players_previous_seats = {player: player_seats.get(player, set()) for player in players}

    return players, players_total_score, players_previous_seats


async def create_round(tournament: models.Tournament) -> models.Round:
    number = 1 + await tournament.rounds.all().count()
    round = await models.Round.create(tournament=tournament, number=number)
    await create_tables(round)
    return round


def get_tables_sizes(players: int, max_table_size: int) -> Iterable[int]:
    # x*max_table_size + y*(max_table_size-1) = players
    while max_table_size > 0:
        y = (-players) % max_table_size
        x = (players - y * (max_table_size - 1)) // max_table_size
        if x >= 0:
            return chain(repeat(max_table_size, x), repeat(max_table_size - 1, y))
        max_table_size -= 1


async def create_tables(round: models.Round):
    players, players_total_score, players_previous_seats = await _get_players_info(round.tournament)
    players = sorted(players, key=players_total_score.get)

    offset = 0
    tables_sizes = get_tables_sizes(len(players), config().tournament.table_size)
    for table_number, table_size in enumerate(tables_sizes, 1):
        table = await models.Table.create(round=round, number=table_number)
        await create_seats(players[offset:offset + table_size], table, players_previous_seats)
        offset += table_size


async def create_seats(players: list[models.Player], table: models.Table, players_previous_seats):
    random.shuffle(players)

    for players_ in permutations(players):
        if all(s not in players_previous_seats[p] for s, p in enumerate(players_, 1)):
            players = players_
            break

    for seat_number, player in enumerate(players, 1):
        await models.Seat.create(table=table, number=seat_number, player=player)
