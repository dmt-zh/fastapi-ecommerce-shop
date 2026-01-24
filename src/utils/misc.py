import logging
import sys


def setup_logger(debug: bool = False) -> logging.Logger:
    """Настройки системы логирования в приложении."""
    level = logging.DEBUG if debug else logging.INFO
    spaces = 4 if debug else 5

    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler(sys.stdout)

    logger.setLevel(level)
    handler.setLevel(level)
    formatter = logging.Formatter(
        fmt=f'%(levelname)s:{" " * spaces}%(asctime)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    return logger
