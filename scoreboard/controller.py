import random
from itertools import chain, repeat
from typing import Iterable

from scoreboard import models
from scoreboard.config import config


async def create_round(tournament: models.Tournament) -> models.Round:
    number = 1 + await tournament.rounds.all().count()
    round = await models.Round.create(tournament=tournament, number=number)
    players = await tournament.players.all()
    # TODO sort players
    await create_tables(players, round)
    return round


def get_tables_sizes(players: int, max_table_size: int) -> Iterable[int]:
    # x*max_table_size + y*(max_table_size-1) = players
    while max_table_size > 0:
        y = (-players) % max_table_size
        x = (players - y * (max_table_size - 1)) // max_table_size
        if x >= 0:
            return chain(repeat(max_table_size, x), repeat(max_table_size - 1, y))
        max_table_size -= 1


async def create_tables(players: list[models.Player], round: models.Round):
    offset = 0
    tables_sizes = get_tables_sizes(len(players), config().tournament.table_size)
    for table_number, table_size in enumerate(tables_sizes, 1):
        table = await models.Table.create(round=round, number=table_number)
        await create_seats(players[offset:offset + table_size], table)
        offset += table_size


async def create_seats(players: list[models.Player], table: models.Table):
    random.shuffle(players)
    # TODO check previous seats
    for seat_number, player in enumerate(players, 1):
        await models.Seat.create(table=table, number=seat_number, player=player)
