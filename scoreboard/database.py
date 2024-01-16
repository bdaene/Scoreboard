from tortoise import Tortoise, connections

from scoreboard.config import config

MODELS_MODULES = [
    'scoreboard.models.tournament',
    'scoreboard.models.player',
    'scoreboard.models.round',
    'scoreboard.models.table',
    'scoreboard.models.score',
]


async def init():
    await Tortoise.init(
        db_url=config().database.url,
        modules=dict(scoreboard=MODELS_MODULES))
    await Tortoise.generate_schemas()


async def close():
    await connections.close_all()
