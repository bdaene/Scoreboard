from importlib import resources

from scoreboard import config

# The score config must be loaded before loading the module scoreboard.models.Scores
with resources.files('tests') / 'test_config.yml' as config_path:
    config.load(config_path)
