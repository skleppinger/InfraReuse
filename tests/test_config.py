from pathlib import Path
import pytest

CONFIG_PATH = Path("tests/test_resources/test_config.yaml")

@pytest.fixture
def application():
    return CONFIG_PATH
