from prettytable import PrettyTable
from constants import (
    DATETIME_FORMAT,
    OUTPUT_FILE,
    OUTPUT_PRETTY,
    BASE_DIR,
)
import datetime as dt
import csv
import logging

FILE_SAVE_LOG = 'Файл с результатами был сохранён: {file_path}'


def file_output(results, cli_args):
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_path = results_dir / f'{parser_mode}_{now_formatted}.csv'

    with open(
        file_path,
        'w',
        encoding='utf-8',
    ) as csvfile:
        writer = csv.writer(csvfile, dialect=csv.unix_dialect)
        writer.writerows(results)
    logging.info(FILE_SAVE_LOG.format(file_path=file_path))


def default_output(results, cli_args):
    for row in results:
        print(*row)


def pretty_output(results, cli_args):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


OUTPUT_OPTIONS = {
    OUTPUT_PRETTY: pretty_output,
    OUTPUT_FILE: file_output,
    None: default_output,
}


def control_output(results, cli_args):
    return OUTPUT_OPTIONS[cli_args.output](results, cli_args)
