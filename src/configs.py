import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import (DT_FORMAT, LOG_DIR, LOG_FILE, LOG_FORMAT, OUTPUT_FILE,
                       OUTPUT_PRETTY)

DOCUMENTATION_PARSER = 'Парсер документации Python'
PARSER_MODES = 'Режимы работы парсера'
CLEAR_CACHE = 'Очистка кеша'
ADDITIONAL_DATA_OUTPUT_METHODS = 'Дополнительные способы вывода данных'


def configure_argument_parser(available_modes):
    parser = argparse.ArgumentParser(description=DOCUMENTATION_PARSER)
    parser.add_argument('mode', choices=available_modes, help=PARSER_MODES)
    parser.add_argument(
        '-c', '--clear-cache', action='store_true', help=CLEAR_CACHE
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=(OUTPUT_PRETTY, OUTPUT_FILE),
        help=ADDITIONAL_DATA_OUTPUT_METHODS,
    )
    return parser


def configure_logging():
    LOG_DIR.mkdir(exist_ok=True)
    rotation_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=10**6, backupCount=5
    )
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=[rotation_handler, logging.StreamHandler()],
    )
