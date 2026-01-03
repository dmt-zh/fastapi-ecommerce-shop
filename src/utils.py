import logging
import sys

##############################################################################################

def setup_logger(debug: bool = False) -> logging.Logger:
    """Настройки системы логирования в приложении."""

    logger = logging.getLogger(__name__)
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    if debug:
        handler.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt='%(asctime)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    return logger

##############################################################################################
