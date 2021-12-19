from logging.handlers import RotatingFileHandler

import sys

import logging

def init_logger(logger):
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    file_handler = RotatingFileHandler('contract_event.log', maxBytes=10000, backupCount=1)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.debug("Logger initialized.")
