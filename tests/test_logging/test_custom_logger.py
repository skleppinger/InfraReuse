from src.logging.custom_logger import (
    create_file_handler,
    configure_logger_to_sysout,
    add_handler_to_logger,
)
import logging
import tempfile
from pathlib import Path


def test_create_file_handler() -> None:
    handler = create_file_handler("test.log")
    assert handler is not None

    handler = create_file_handler("test.log", rotate_file_logs=True)
    assert handler is not None


def test_add_handler_to_logger() -> None:
    logger = logging.getLogger("test")
    handler = create_file_handler("test.log")
    logger.addHandler(handler)
    assert handler in logger.handlers


def test_file_logging() -> None:
    logger = logging.getLogger("test2")
    with tempfile.NamedTemporaryFile() as temp_file:
        handler = create_file_handler(temp_file.name, level=logging.INFO)
        add_handler_to_logger(logger, handler)

        logger.addHandler(handler)
        logger.info("Test message")
        assert Path(temp_file.name).exists()
        assert Path(temp_file.name).stat().st_size > 0


def test_configure_logger_to_sysout() -> None:
    logger = logging.getLogger("test3")
    configure_logger_to_sysout(logger)
    logger.info("Test message")
    logger.error("Test error message")
    # TODO do a check here
