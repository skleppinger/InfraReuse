from src.components.application_component import ConfigurableApplicationComponent
from pydantic import BaseModel, ValidationError, field_validator
from typing import Any
from enum import Enum
import pytest


class TestEnum(Enum):
    FOO = "foo"
    BAR = "bar"


class TestConfig(BaseModel):
    # TODO add prefix?
    foo: int
    bar: str
    baz: bool


class TestNestedConfig(BaseModel):
    qux: int
    quux: str
    baz2: TestConfig


class DoubleNestedConfig(BaseModel):
    qux2: int
    quux2: str
    baz3: TestNestedConfig


class TestCustomEnumConfig(BaseModel):
    foo: TestEnum
    bar: list[TestEnum]


class TestOptionalListConfig(BaseModel):
    foo: list[int] | None
    bar: list[str] | None = None
    baz: list[bool] | None


class TestCustomModelValidationConfig(BaseModel):
    foo: int
    bar: str

    @field_validator("foo")
    @classmethod
    def validate_foo(cls, foo: int) -> int:
        assert foo < 10, "foo must be less than 10"
        return foo


class TestComponent(ConfigurableApplicationComponent):
    CONFIG = TestConfig

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self.apply_config(config)


class TestNestedComponent(TestComponent):
    CONFIG = TestNestedConfig


class DoubleNestedComponent(TestNestedComponent):
    CONFIG = DoubleNestedConfig


def test_component():
    config = {"foo": 1, "bar": "baz", "baz": True}
    component = TestComponent(config)
    assert component.params.foo == 1
    assert component.params.bar == "baz"
    assert component.params.baz is True


def test_nested_component():
    config = {
        "qux": 2,
        "quux": "quuz",
        "baz2": {"foo": 3, "bar": "quuz2", "baz": False},
    }
    component = TestNestedComponent(config)
    assert component.params.qux == 2
    assert component.params.quux == "quuz"
    assert component.params.baz2.foo == 3
    assert component.params.baz2.bar == "quuz2"
    assert component.params.baz2.baz is False


def test_double_nested_component():
    config = {
        "qux2": 4,
        "quux2": "quuz3",
        "baz3": {
            "qux": 5,
            "quux": "quuz4",
            "baz2": {"foo": 6, "bar": "quuz5", "baz": False},
        },
    }
    component = DoubleNestedComponent(config)
    assert component.params.qux2 == 4
    assert component.params.quux2 == "quuz3"
    assert component.params.baz3.qux == 5
    assert component.params.baz3.quux == "quuz4"
    assert component.params.baz3.baz2.foo == 6
    assert component.params.baz3.baz2.bar == "quuz5"
    assert component.params.baz3.baz2.baz is False


def test_optional_list_config_entry():

    class TestOptionalListComponent(TestComponent):
        CONFIG = TestOptionalListConfig

    config = {"foo": [1, 2, 3], "baz": [True, False, True]}
    component = TestOptionalListComponent(config)
    assert component.params.foo == [1, 2, 3]
    assert component.params.baz == [True, False, True]
    assert component.params.bar is None

    # Test if we don't have a default arg
    config2 = {"foo": [1, 2, 3], "baz": None, "bar": None}
    component2 = TestOptionalListComponent(config2)
    assert component2.params.foo == [1, 2, 3]
    assert component2.params.baz is None
    assert component2.params.bar is None

    # Test failure is reported if no value is provided
    config3 = {"foo": [1, 2, 3]}
    with pytest.raises(ValidationError):
        TestOptionalListComponent(config3)


def test_with_custom_enum_config_entry():

    class TestCustomEnumComponent(TestComponent):
        CONFIG = TestCustomEnumConfig

    config = {"foo": TestEnum.FOO, "bar": [TestEnum.BAR, TestEnum.FOO]}
    component = TestCustomEnumComponent(config)
    assert component.params.foo == TestEnum.FOO
    assert component.params.bar == [TestEnum.BAR, TestEnum.FOO]

    # Test failure is reported if an invalid value is provided
    config2 = {"foo": "invalid", "bar": [TestEnum.BAR, TestEnum.FOO]}
    with pytest.raises(ValidationError):
        TestCustomEnumComponent(config2)


def test_with_custom_model_validation():
    class TestCustomModelValidationComponent(TestComponent):
        CONFIG = TestCustomModelValidationConfig

    config = {"foo": 11, "bar": "baz"}
    with pytest.raises(ValidationError):
        TestCustomModelValidationComponent(config)

    config2 = {"foo": 9, "bar": "baz"}
    component = TestCustomModelValidationComponent(config2)
    assert component.params.foo == 9
    assert component.params.bar == "baz"
