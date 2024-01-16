import asyncio

from tortoise import run_async

from scoreboard import database
from scoreboard.models import Tournament, Player, Round, Table, Seat, Score


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
        Player.create(name="Clayton Maldonado"),
    )

    assert await Player.all() == players

    await tournament.players.add(*players)

    round_1 = await Round.create(number=1, tournament=tournament)
    tables = await asyncio.gather(*(Table.create(number=i + 1, round=round_1) for i in range(len(players) // 4 + 1)))
    seats = await asyncio.gather(*(Seat.create(table=tables[i // 4], number=i % 4 + 1, player=player)
                                   for i, player in enumerate(players)))

    assert await round_1.tables.all() == tables
    assert await tables[0].seats.all() == seats[:4]
    assert (await Seat.filter(player=players[5]).first()).number == 2

    scores = await asyncio.gather(
        Score.create(round=round_1, player=players[0], tournament_points=3, victory_points=10),
        Score.create(round=round_1, player=players[1], tournament_points=0, victory_points=7),
        Score.create(round=round_1, player=players[2], tournament_points=5, victory_points=13),
        Score.create(round=round_1, player=players[3], tournament_points=1, victory_points=8),
        Score.create(round=round_1, player=players[4], tournament_points=3, victory_points=10),
        Score.create(round=round_1, player=players[5], tournament_points=1, victory_points=6),
        Score.create(round=round_1, player=players[6], tournament_points=5, victory_points=14),
    )

    assert await Score.all() == sorted(scores)

    await database.close()


def test_run():
    run_async(run())


def test_score_order():
    from scoreboard.models.score import ORDER

    assert ORDER == ((True, 'tournament_points'), (False, 'victory_points'))
