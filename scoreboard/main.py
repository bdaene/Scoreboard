import asyncio
import logging

from scoreboard import config


def main():
    logging.basicConfig(level=logging.INFO)

    if config.DEFAULT_PATH.exists():
        config.load()
    else:
        config.save()

    try:
        from scoreboard import database, gui  # Config must be loaded before the module models.Score
        asyncio.run(database.init())
        gui.start()
    finally:
        asyncio.run(database.close())


if __name__ in {"__main__", "__mp_main__"}:
    main()
