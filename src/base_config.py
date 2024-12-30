from pydantic import BaseModel
from typing import Any, Generator
from typing_extensions import ClassVar
import warnings


class Config(BaseModel):
    """Base class for configuration models.

    This class provides a prefix for configuration keys and a method to scan a configuration for keys with that prefix.

    This is an extension of the pydantic BaseModel class.
    """

    PREFIX: ClassVar[str | None] = None

    @classmethod
    def scan_config_for_prefix(
        cls, config: dict, prefix: str | None = None, surpress_warnings: bool = False
    ) -> dict:
        """Scans a configuration for keys with the given prefix.

        Args:
            config (dict): The configuration to scan.
            prefix (str | None): The prefix to scan for. If None, the class prefix is used. Allow Parent.Child.Component.Key
            surpress_warnings (bool): Whether to surpress warnings.

        Returns:
            dict: A dictionary of keys and values with the given prefix.
        """
        prefix = cls.PREFIX if prefix is None else prefix
        assert isinstance(prefix, str), "Prefix must be a string"

        def scan_config_for_prefix_recursive(
            config: dict, prefix: list[str]
        ) -> Generator[tuple[str, Any], None, None]:
            if len(prefix) == 0:
                yield from config.items()
            else:
                key = prefix[0]
                if key in config:
                    yield from scan_config_for_prefix_recursive(config[key], prefix[1:])
                else:
                    if not surpress_warnings:
                        warnings.warn(f"Key {prefix[0]} not found in config")
                    return

        key_chain = prefix.split(".")
        return dict(scan_config_for_prefix_recursive(config, key_chain))
