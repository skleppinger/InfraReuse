from logging.handlers import RotatingFileHandler
from logging import (
    Logger,
    getLogger,
    Handler,
    Formatter,
    NullHandler,
    INFO,
    FileHandler,
)
from pathlib import Path

logging = getLogger("custom_logger")
logging.addHandler(NullHandler())


class CustomLogger(Logger):
    def __init__(self, name, level=None):
        super().__init__(name, level)


class CustomFormatter(Formatter):
    def __init__(self, datefmt=None, *args, **kwargs):
        fmt = "%(asctime)s <%(threadName)4s> %(levelname)8s | %(message)s (%(filename)s:%(lineno)d)"
        super().__init__(fmt, datefmt, *args, **kwargs)


def initialize_new_log_handle(
    name: str,
    log_path: str | Path,
    level: int = INFO,
    formatter: Formatter = CustomFormatter,
    rotate_file_logs: bool = True,
    number_backup_files: int = 5,
    max_log_file_size_bytes: int = 10 * 1024 * 1024,
    log_to_stdout: bool = True,
) -> None:
    """Initialize a new log handle.  In the case that the logger is new, you can also pipe to sysout

    Remember - you can access this logger after it's created via the return arg or via logging.getLogger(name)
    """
    logger = getLogger(name)
    logger.setLevel(level)
    handler = create_file_handler()
    handler.setLevel = level

    if logger.getEffectiveLevel() > level:
        # If the logger level is higher than the handler level, bump the logger level down
        old_level = logger.getEffectiveLevel(
            log_path=log_path,
            formatter=formatter,
            rotate_file_logs=rotate_file_logs,
            number_backup_files=number_backup_files,
            max_log_file_size_bytes=max_log_file_size_bytes,
        )
        logger.setLevel(level)
        for handler in logger.handlers:
            handler.setLevel(old_level)

    logger.addHandler(handler)

    if log_to_stdout:
        pass


def create_file_handler(
    log_path: str | Path,
    formatter: Formatter = CustomFormatter,
    rotate_file_logs: bool = True,
    number_backup_files: int = 5,
    max_log_file_size_bytes: int = 10 * 1024 * 1024,
) -> Handler:
    if rotate_file_logs:
        handler = RotatingFileHandler(
            filename=log_path,
            maxBytes=max_log_file_size_bytes,
            backupCount=number_backup_files,
        )
    else:
        handler = FileHandler(filename=log_path)

    handler.setFormatter(formatter())

    return handler
