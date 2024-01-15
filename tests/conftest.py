from importlib import resources

import pytest

from scoreboard import config


@pytest.fixture(scope='session', autouse=True)
def init_config():
    with resources.files('tests') / 'test_config.yml' as config_path:
        config.load(config_path)
