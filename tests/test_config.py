from unittest import mock

import pytest

from scoreboard.config import Config, DatabaseConfig, save, load, config


@pytest.mark.parametrize("expected_config", [
    Config(database=DatabaseConfig(url="test url"))
])
def test_save_and_load(tmp_path, expected_config):
    config_url = tmp_path / 'config.yml'
    with mock.patch('scoreboard.config._config', expected_config):
        save(config_url)
        result = load(config_url)

        assert result == expected_config
        assert config() == expected_config
