import logging
from pathlib import Path

import yaml
from attr import field, define, evolve, asdict

_LOGGER = logging.getLogger(__name__)


def _get_converter(config_class):
    def convert(data):
        if isinstance(data, config_class):
            return data
        return config_class(**data)

    return convert


@define
class DatabaseConfig:
    url: str = field(default='sqlite://scoreboard.db')


@define
class ScoreConfig:
    order: tuple[str] = field(default=('-tournament_points',), converter=tuple)


@define
class Config:
    database: DatabaseConfig = field(factory=dict, converter=_get_converter(DatabaseConfig))
    score: ScoreConfig = field(factory=dict, converter=_get_converter(ScoreConfig))


_config: Config = Config()
DEFAULT_PATH = Path('config.yml')


def load(url: Path = DEFAULT_PATH) -> Config:
    _LOGGER.info(f"Loading config from {url}.")
    with open(url) as config_file:
        new_config = yaml.safe_load(config_file)

    global _config
    _config = evolve(_config, **new_config)
    return _config


def save(url: Path = DEFAULT_PATH):
    url.parent.mkdir(parents=True, exist_ok=True)
    with open(url, 'w') as config_file:
        yaml.safe_dump(asdict(_config), config_file)


def config():
    return _config
