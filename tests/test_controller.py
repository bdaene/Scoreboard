import asyncio

from tortoise import run_async

from scoreboard import database
from scoreboard.controller import create_round
from scoreboard.models import Tournament, Player, Score


async def run():
    await database.init()

    tournament = await Tournament.create(name="Test tournament")

    players = await asyncio.gather(
        Player.create(name="Canaan Lee"),
        Player.create(name="Daphne Larson"),
        Player.create(name="Damon Meyers"),
        Player.create(name="Kian Zavala"),
        Player.create(name="Wesley Alvarado"),
        Player.create(name="Abner McCall"),
        Player.create(name="Ivanna Morris"),
        Player.create(name="Julianna Potts"),
        Player.create(name="Macy Park"),
        Player.create(name="Frank Terry"),
    )
    await tournament.players.add(*players[:5])

    round_1 = await create_round(tournament)
    await round_1.fetch_related('tables__seats', 'scores')

    assert [len(table.seats) for table in round_1.tables] == [3, 2]

    await Score.create(round=round_1, player=players[0], tournament_points=5, malus_points=6)
    await Score.create(round=round_1, player=players[1], tournament_points=3, malus_points=10)
    await Score.create(round=round_1, player=players[2], tournament_points=0, malus_points=11)
    await Score.create(round=round_1, player=players[3], tournament_points=3, malus_points=8)
    await Score.create(round=round_1, player=players[4], tournament_points=5, malus_points=8)

    await tournament.players.add(*players[5:7])

    round_2 = await create_round(tournament)
    await round_2.fetch_related('tables__seats__player', 'scores')

    assert [len(table.seats) for table in round_2.tables] == [3, 2, 2]

    assert set(seat.player for seat in round_2.tables[0].seats) == {players[0], players[4], players[3]}
    assert players[1] in set(seat.player for seat in round_2.tables[1].seats)
    assert players[2] in set(seat.player for seat in round_2.tables[2].seats)
    assert players[6] in set(seat.player for table in round_2.tables for seat in table.seats)

    await Score.create(round=round_1, player=players[0], tournament_points=5, malus_points=8)
    await Score.create(round=round_1, player=players[4], tournament_points=3, malus_points=3)
    await Score.create(round=round_1, player=players[3], tournament_points=0, malus_points=1)
    await Score.create(round=round_1, player=players[1], tournament_points=3, malus_points=2)
    await Score.create(round=round_1, player=players[5], tournament_points=5, malus_points=7)
    await Score.create(round=round_1, player=players[6], tournament_points=5, malus_points=9)
    await Score.create(round=round_1, player=players[2], tournament_points=3, malus_points=3)

    await tournament.players.remove(players[3], players[2], players[1])

    round_3 = await create_round(tournament)
    await round_3.fetch_related('tables__seats')

    assert [len(table.seats) for table in round_3.tables] == [2, 2]

    await tournament.players.remove(players[4], players[5], players[6])
    round_4 = await create_round(tournament)
    await round_4.fetch_related('tables__seats')

    assert [len(table.seats) for table in round_4.tables] == [1]

    await database.close()


def test_run():
    run_async(run())
