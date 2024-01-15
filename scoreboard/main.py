import logging

from scoreboard import config


def main():
    logging.basicConfig(level=logging.INFO)
    if config.DEFAULT_PATH.exists():
        config.load()
    # TODO init Database
    # TODO launch GUI
    ...


if __name__ == "__main__":
    main()
