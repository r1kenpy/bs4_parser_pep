from prettytable import PrettyTable
from constants import (
    DATETIME_FORMAT,
    OUTPUT_FILE,
    OUTPUT_PRETTY,
    BASE_DIR,
    FOLDER_RESULTS,
)
import datetime as dt
import csv
import logging

FILE_SAVE_LOG = 'Файл с результатами был сохранён: {file_path}'


def file_output(results, cli_args):
    results_dir = BASE_DIR / FOLDER_RESULTS
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    file_path = (
        results_dir
        / f'{parser_mode}_{dt.datetime.now().strftime(DATETIME_FORMAT)}.csv'
    )

    with open(
        file_path,
        'w',
        encoding='utf-8',
    ) as csvfile:
        csv.writer(csvfile, dialect=csv.unix_dialect).writerows(results)
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


METHODS_OUTPUTS = {
    OUTPUT_PRETTY: pretty_output,
    OUTPUT_FILE: file_output,
    None: default_output,
}


def control_output(results, cli_args):
    return METHODS_OUTPUTS[cli_args.output](results, cli_args)
