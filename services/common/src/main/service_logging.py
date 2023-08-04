"""Logging utility class for Valytics."""
import inspect
import logging
import sys


FILE_LOG_HANDLER_NAME = "file"
STDOUT_LOG_HANDLER_NAME = "stdout"
STDERR_LOG_HANDLER_NAME = "stderr"


def init_logging() -> None:
    """Initializes a logger for the process."""
    file_handler = logging.FileHandler(filename="/tmp/valytics-service.log")
    file_handler.set_name(FILE_LOG_HANDLER_NAME)
    file_handler.setLevel(logging.INFO)

    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.set_name(STDOUT_LOG_HANDLER_NAME)
    stdout_handler.setLevel(logging.DEBUG)

    stderr_handler = logging.StreamHandler(stream=sys.stderr)
    stderr_handler.set_name(STDERR_LOG_HANDLER_NAME)
    stderr_handler.setLevel(logging.ERROR)

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[file_handler, stdout_handler, stderr_handler],
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def log_and_flush(level: int, message: str) -> None:
    """Logs a message and flushes output to stdout.

    Arguments:
        level (int): The log level.
        logger_name (str): The name of the logger to output to.
        message (str): The message to log.
    """
    logger = logging.getLogger()
    logger.log(level, f"[{inspect.stack()[1].filename}:{inspect.stack()[1].lineno}] -> {message}")

    flush_logging_streams(logger)


def flush_logging_streams(logger: logging.Logger) -> None:
    """Flushes output to stdout and stderr streams.

    Arguments:
        logger (Logger): Logger with stdout and stderr handlers to flush.
    """
    for handler in logger.handlers:
        if handler.name in [STDOUT_LOG_HANDLER_NAME, STDERR_LOG_HANDLER_NAME]:
            handler.flush()
