from prettytable import PrettyTable
from constants import (
    BASE_DIR,
    DATETIME_FORMAT,
    OUTPUT_FILE,
    OUTPUT_PRETTY,
    RESULTS_DIR,
    FILE_PATH,
)
import datetime as dt
import csv
import logging

FILE_SAVE_LOG = 'Файл с результатами был сохранён: {file_path_str}'


def control_output(results, cli_args):
    output = cli_args.output
    if output == OUTPUT_PRETTY:
        pretty_output(results)
    elif output == OUTPUT_FILE:
        file_output(results, cli_args)
    else:
        default_output(results)


def file_output(results, cli_args):

    RESULTS_DIR.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_path_str = str(FILE_PATH).format(
        parser_mode=parser_mode, now_formatted=now_formatted
    )
    with open(
        file_path_str,
        'w',
        encoding='utf-8',
    ) as csvfile:
        writer = csv.writer(csvfile, dialect='unix')
        writer.writerows(results)
    logging.info(FILE_SAVE_LOG.format(file_path_str=file_path_str))


def default_output(results):
    for row in results:
        print(*row)


def pretty_output(results):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)
