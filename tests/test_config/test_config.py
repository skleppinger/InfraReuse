from pathlib import Path
from src.base_config import Config
from yaml import safe_load
import pytest

CONFIG_PATH = Path("tests/test_resources/test_config.yaml")


@pytest.fixture
def config_model() -> Config:
    class config(Config):
        foo: int
        bar: str
        baz: bool

    config.PREFIX = "TestManager.test_component.config"
    return config


@pytest.fixture
def config() -> Config:
    with open(CONFIG_PATH, "r") as f:
        config = safe_load(f)
    return config


def test_config(config: dict, config_model: Config):
    component_config = config_model.scan_config_for_prefix(
        config, surpress_warnings=False
    )
    assert component_config == {"foo": 1, "bar": "tt", "baz": True}
