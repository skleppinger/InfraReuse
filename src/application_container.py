from abc import ABC, abstractmethod
from pathlib import Path
from logging import Logger
from dependency_resolver import DependencyResolver
import signal
import typer
import pydantic
import yaml
from src.custom_exceptions import DependencyInjectionError

class CustomApplication(ABC):
    """
    Default application container for a general app.  Uses some standardized config parsing, command line parsing, and run methods.
    """
    _application_arguments: typer.Typer
    _application_config: pydantic.BaseModel
    app = typer.Typer()

    def __init__(self, **kwargs):
        self._injector = DependencyResolver()
        self._global_config = None
        self._local_config = None

        self.configured = False

    def parse_arguments(self):
        pass

    @app.command()
    def configure(self, config_path: Path):
        """Read in the command line, then read in the denoted config and validate with pydantic model"""
        self._global_config = yaml.safe_load(config_path.read_text())
        

    def get_object(self, requested_class: type, missing_ok: bool):
        if self.injector is None:
            raise AttributeError("Injector not initialized")
        try:
            return self.injector.get(requested_class)
        except DependencyInjectionError as e:
            if missing_ok:
                return None
            else:
                raise e

    @app.command()
    @abstractmethod
    def pre_run(self):
        pass

    @app.command()
    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def pre_stop(self):
        pass

    @abstractmethod
    def stop(self):
        pass
