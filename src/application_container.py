from abc import ABC, abstractmethod
from pathlib import Path
from logging import Logger
from src.dependency_resolver import DependencyResolver, ResolveByNameAndType
import signal
import src.factory as factory
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
        self._resolver = DependencyResolver()
        self._global_config = None
        self._local_config = None
        self.managers = []

        self.configured = False

    def parse_arguments(self):
        pass

    def load_managers(self) -> None:
        if "Managers" not in self._global_config:
            return

        for manager_name, manager_class in self._global_config["Managers"].items():
            manager_class = factory.load_classes([{"module": manager_class}])[0]
            required_args = self._resolver.resolve_object_kwargs(manager_class, policy=ResolveByNameAndType)
            manager = manager_class(**required_args, _global_config=self._global_config)
            self._resolver.add_object(manager, manager_name)
            self.managers.append(manager)

    @app.command()
    def configure(self, config_path: Path | str | None = None, **kwargs):
        """Read in the command line, then read in the denoted config and validate with pydantic model"""
        if config_path is None:
            self._global_config = {}
        else:
            self._global_config = yaml.safe_load(Path(config_path).read_text())

        # Apply config to the application - logging, etc.

        # Read Manager section of config, build all the managers via dependency resolver
        self.load_managers()

        # Get all the component classes denoted in the config

        # bind everything in the resolver

        # 

        # TODO validate the individual config elements?

        self.configured = True
        

    def get_object(self, requested_class: type, missing_ok: bool=True):
        if self.injector is None:
            raise AttributeError("Injector not initialized")
        try:
            return self.injector.get(requested_class)
        except DependencyInjectionError as e:
            if missing_ok:
                return None
            else:
                raise e
            
    def validate_config(self, config: dict, surpress_warnings: bool) -> None:
        pass

    @app.command()
    # @abstractmethod
    def pre_run(self):
        pass

    @app.command()
    # @abstractmethod
    def run(self):
        pass

    # @abstractmethod
    def pre_stop(self):
        pass

    # @abstractmethod
    def stop(self):
        pass
