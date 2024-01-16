import logging

import tortoise

from scoreboard import config, database


async def main():
    logging.basicConfig(level=logging.INFO)

    if config.DEFAULT_PATH.exists():
        config.load()

    await database.init()

    # TODO launch GUI
    ...


if __name__ == "__main__":
    tortoise.run_async(main())
