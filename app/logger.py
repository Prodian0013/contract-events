import logging
import sys
from logging import Logger
from logging.handlers import RotatingFileHandler


def init_logger(logger: Logger):
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    file_handler = RotatingFileHandler('contract_event.log', maxBytes=10000, backupCount=1)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.debug("Logger initialized.")
