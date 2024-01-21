import logging
from importlib import resources
from pathlib import Path

import yaml
from attrs import field, define, evolve, asdict, Factory

_LOGGER = logging.getLogger(__name__)


def _get_converter(config_class):
    def convert(data):
        if isinstance(data, config_class):
            return data
        return config_class(**data)

    return convert


@define
class DatabaseConfig:
    url: str = field(default='sqlite://data/scoreboard.db')


@define
class ScoreFieldConfig:
    name: str = field()
    descending: bool = field(default=True)
    label: str = field(default=Factory(lambda self: self.name, takes_self=True))


@define
class TournamentConfig:
    table_size: int = field(default=2)
    score: tuple[ScoreFieldConfig] = field(
        default=(ScoreFieldConfig(name='tournament_points', label='TP'),),
        converter=lambda data: tuple(map(_get_converter(ScoreFieldConfig), data))
    )


@define
class GuiConfig:
    favicon: Path = field(default=resources.files('scoreboard') / 'emoji_events.ico', converter=Path)
    title: str = field(default='Score Board')
    dark: bool = field(default=True)
    native: bool = field(default=False)


@define
class Config:
    tournament: TournamentConfig = field(factory=dict, converter=_get_converter(TournamentConfig))
    database: DatabaseConfig = field(factory=dict, converter=_get_converter(DatabaseConfig))
    gui: GuiConfig = field(factory=dict, converter=_get_converter(GuiConfig))


_config: Config = Config()
DEFAULT_PATH = Path('data/config.yml')


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
        yaml.safe_dump(asdict(_config, filter=lambda _a, v: not isinstance(v, Path)), config_file, sort_keys=False)


def config() -> Config:
    return _config
