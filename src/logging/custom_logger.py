import sys
import logging
from pathlib import Path

logger = logging.getLogger("custom_logger")
# logger.addHandler(NullHandler())


class CustomLogger(logging.Logger):
    def __init__(self, name, level=None):
        super().__init__(name, level)


class CustomFormatter(logging.Formatter):
    def __init__(self, datefmt=None, *args, **kwargs):
        fmt = "%(asctime)s <%(threadName)4s> %(levelname)8s | %(message)s (%(filename)s:%(lineno)d)"
        super().__init__(fmt, datefmt, *args, **kwargs)


class CustomFormatterWithColor(CustomFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_color = True

    def format(self, record: logging.LogRecord) -> str:
        if record.levelno >= logging.ERROR:
            record.levelname = f"\033[31m{record.levelname}\033[0m"
        elif record.levelno >= logging.WARNING:
            record.levelname = f"\033[33m{record.levelname}\033[0m"
        else:
            record.levelname = f"\033[32m{record.levelname}\033[0m"
        return super().format(record)


def initialize_new_logger(
    name: str,
    log_path: str | Path,
    level: int = logging.INFO,
    formatter: logging.Formatter = CustomFormatter,
    rotate_file_logs: bool = True,
    number_backup_files: int = 5,
    max_log_file_size_bytes: int = 10 * 1024 * 1024,
    log_to_stdout: bool = True,
) -> logging.Logger:
    """Initialize a new log instance.  In the case that the logger is new, you can also pipe to sysout

    Remember - you can access this logger after it's created via the return arg or via logging.getLogger(name)
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = create_file_handler(
        log_path,
        formatter,
        rotate_file_logs,
        number_backup_files,
        max_log_file_size_bytes,
        level,
    )

    add_handler_to_logger(logger, handler)

    if log_to_stdout:
        configure_logger_to_sysout(logger)

    return logger


def add_handler_to_logger(
    logger: logging.Logger,
    handler: logging.Handler,
    level: int = logging.INFO,
    formatter: logging.Formatter = CustomFormatter,
) -> None:

    if logger.getEffectiveLevel() > level:
        # If the logger level is higher than the handler level, bump the logger level down
        logger.setLevel(level)
        for handler in logger.handlers:
            handler.setLevel(level)
    logger.addHandler(handler)


def configure_logger_to_sysout(logger: logging.Logger, level: int = logging.INFO):
    # TODO first check if logger already has two stream handlers
    # if it does skip this function
    formatter = CustomFormatterWithColor()  # TODO add args

    stderr_handler = logging.StreamHandler(stream=sys.stderr)

    # only log errors to stderr
    class ErrorFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            return record.levelno >= logging.ERROR

    # log everything less than ERROR to stdout
    class LessThanErrorFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            return record.levelno < logging.ERROR

    stderr_handler.addFilter(ErrorFilter())

    stdout_handler = logging.handlers(stream=sys.stdout)
    stdout_handler.addFilter(LessThanErrorFilter())

    add_handler_to_logger(logger, stderr_handler, logging.ERROR, formatter)
    add_handler_to_logger(logger, stdout_handler, logging.INFO, formatter)


def create_file_handler(
    log_path: str | Path,
    formatter: logging.Formatter = CustomFormatter,
    rotate_file_logs: bool = False,
    number_backup_files: int = 5,
    max_log_file_size_bytes: int = 10 * 1024 * 1024,
    level: int = logging.INFO,
) -> logging.Handler:
    if rotate_file_logs:
        handler = logging.handlers.RotatingFileHandler(
            filename=log_path,
            maxBytes=max_log_file_size_bytes,
            backupCount=number_backup_files,
        )
    else:
        handler = logging.FileHandler(filename=log_path)

    handler.setFormatter(formatter())
    handler.setLevel(level)

    return handler
