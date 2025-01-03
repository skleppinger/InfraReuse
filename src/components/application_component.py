from abc import ABC
from pydantic import BaseModel
from src.base_config import Config
from typing import Any


class ApplicationComponent(ABC):

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)


class ConfigurableApplicationComponent(ApplicationComponent):
    CONFIG: Config

    def __init__(self, **kwargs: dict[str, Any]) -> None:  # TODO global or local?
        super().__init__(**kwargs)  # TODO fix args
        self.CONFIG.model_validate(kwargs)  # TODO validate config

    # @classmethod
    # def register_config(cls, config: dict) -> None:
    #     pass

    @classmethod
    def validate_config(cls, config: dict, surpress_warnings: bool) -> None:
        cls.CONFIG.model_validate(config, strict=not surpress_warnings)

    def apply_config(self, config: dict) -> BaseModel:
        self.params = self.CONFIG.model_validate(config)
        return self.params
