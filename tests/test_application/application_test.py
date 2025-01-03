from src.application_container import CustomApplication
from src.components.application_component import (
    ApplicationComponent,
    ConfigurableApplicationComponent,
)
from src.dependency_resolver import DependencyResolver, ResolveByNameAndType
from typing import Any
from pathlib import Path
import src.factory as factory
from src.base_config import Config
from src.logging.custom_logger import logger
import tempfile
from src.logging.logging_helpers import create_file_handler, add_handler_to_logger


class FailingConfig(Config):
    foo: int
    bar: str
    baz: bool
    PREFIX = "test_component"


class PassingConfig(Config):
    foo: int
    bar: int
    baz: int
    PREFIX = "test_component"


class TestComponent(ConfigurableApplicationComponent):
    CONFIG = PassingConfig

    def __init__(
        self, **kwargs: dict[str, Any]
    ) -> None:  # TODO fix, the config isn't showing up in the required kwargs
        super().__init__(**kwargs)
        self.params = self.CONFIG.model_validate(kwargs)
        print(self.params)

        # Make sure logging is working for the application, repeat of custom logger test
        self._logger = logger
        temp_dir = tempfile.gettempdir()
        temp_file = Path(temp_dir + "/test.log")
        handle = create_file_handler(temp_file)
        add_handler_to_logger(self._logger, handle)
        self._logger.info("TestComponent initialized")
        self._logger.info(f"TestComponent params: {self.params}")
        assert Path(temp_file.name).exists()
        assert Path(temp_file.name).stat().st_size > 0


class TestManager(ApplicationComponent):
    PREFIX = "TestManager"

    def __init__(
        self,
        resolver: DependencyResolver,
        **kwargs: dict[str, Any],
    ) -> None:
        super().__init__(**kwargs)
        self.resolver = resolver
        self.local_config = self._global_config.get(self.PREFIX, {})
        self.components = self.load_components()

    def load_components(self) -> list[ApplicationComponent]:
        components = []
        for component_name, component_config in self.local_config.items():
            component_class = factory.load_classes([component_config])[0]
            additional_config = component_config.copy()
            additional_config.pop("module", None)
            additional_config.pop("enabled", None)
            required_kwargs = self.resolver.resolve_object_kwargs(
                component_class,
                policy=ResolveByNameAndType,
                additional_objects=additional_config,
            )
            if issubclass(component_class, ConfigurableApplicationComponent):
                component_class.validate_config(
                    required_kwargs, surpress_warnings=False
                )
            component = component_class(**required_kwargs)
            self.resolver.add_object(component, component_name)
            components.append(component)
        return components

    def configure(self) -> None:
        super().configure()

    def pre_run(self) -> None:
        pass

    def start(self) -> None:
        print("Starting TestManager")


class TestApplication(CustomApplication):
    def __init__(self) -> None:
        super().__init__()
        self.manager: ApplicationComponent | None = None

    def configure(self, config_path: Path | str | None = None) -> None:
        super().configure(config_path, additional_objects=[DependencyResolver()])

    def pre_run(self) -> None:
        for manager in self.managers:
            manager.pre_run()

    def run(self) -> None:
        for manager in self.managers:
            manager.start()


def test_application_container():
    app = TestApplication()
    app.configure(Path("tests/test_application/application_config.yaml"))
    app.pre_run()
    app.run()
    assert True
