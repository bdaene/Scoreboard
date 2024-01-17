import asyncio
import logging

from scoreboard import config, database, gui


def main():
    logging.basicConfig(level=logging.INFO)

    if config.DEFAULT_PATH.exists():
        config.load()

    try:
        asyncio.run(database.init())
        gui.start()
    finally:
        asyncio.run(database.close())


if __name__ in {"__main__", "__mp_main__"}:
    main()
