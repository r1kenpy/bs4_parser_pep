import logging
import re
from urllib.parse import urljoin

from collections import defaultdict

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    EXPECTED_STATUS,
    MAIN_DOC_URL,
    PEP_URL,
    DOWNLOADS_URL,
    WHATS_NEW_URL,
    BASE_DIR,
)
from outputs import control_output
from utils import find_all_tags, find_tag, get_response, get_soup


PARSE_DONE = 'Парсер завершил работу'
LOGGING_EXCEPTION = 'Возникла ошибка'
EXCEPTION_NOTHING_FOUND = 'Ничего не нашлось'
LOGGING_DOWNLOAD_SUCCES = 'Архив был загружен и сохранён: {archive_path}'
LOGGING_MESSAGE_DIFFERENT_STATUSES = (
    'Несовпадающие статусы: {with_different_statuses}'
)
TEXT_WITH_DIFFERENT_STATUSES = (
    'Pep: [{url_pep}];'
    'Статус в карточке: {status_on_page_pep};'
    'Ожидаемые статусы: {expected_status}'
)
LOGGING_COMMAND_LINE_ARGUMENTS = 'Аргументы командной строки: {args}'


def whats_new(session):

    soup = get_soup(session, WHATS_NEW_URL)
    soup1 = get_soup(session, WHATS_NEW_URL)
    sections_by_python = soup1.select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1'
    )
    # dd = soup1.select(
    #     '#what-s-new-in-python div.toctree-wrapper li.toctree-l1'
    # )

    # main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    # div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    # sections_by_python = div_with_ul.find_all(
    #     'li', attrs={'class': 'toctree-l1'}
    # )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for section in tqdm(sections_by_python):
        version_link = urljoin(
            WHATS_NEW_URL,
            find_tag(
                section, 'a', attrs={'href': re.compile(r'\d\.\d+\.html')}
            )['href'],
        )
        session = requests_cache.CachedSession()
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        results.append(
            (
                version_link,
                find_tag(soup, 'h1').text,
                find_tag(soup, 'dl').text.replace('\n', ' '),
            )
        )

    return results


def latest_versions(session):
    soup = get_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise KeyError(EXCEPTION_NOTHING_FOUND)
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    for a_tag in a_tags:
        text_match = re.match(
            r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)', a_tag.text
        )
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((a_tag.get('href', None), version, status))

    return results


def download(session):
    soup = get_soup(session, DOWNLOADS_URL)
    table_tag = find_tag(soup, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    archive_url = urljoin(DOWNLOADS_URL, pdf_a4_tag['href'])
    filename = archive_url.split('/')[-1]
    download_dir = BASE_DIR / 'downloads'
    download_dir.mkdir(exist_ok=True)
    archive_path = download_dir / filename
    response = get_response(session, archive_url)
    with open(archive_path, 'wb') as f:
        f.write(response.content)
    logging.info(LOGGING_DOWNLOAD_SUCCES.format(archive_path=archive_path))


def pep(session):
    soup = get_soup(session, PEP_URL)
    section_tag = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    tag_tbody = find_tag(section_tag, 'tbody')
    tr_tags = find_all_tags(tag_tbody, 'tr')
    results_link = []
    for row in tqdm(tr_tags):
        results_link.append(
            (
                find_tag(row, 'abbr').text[1:],
                urljoin(PEP_URL, find_tag(row, 'a').get('href')),
            )
        )
    with_different_statuses = []
    quantity_pep_in_each_status = defaultdict(int)
    for result in tqdm(results_link):
        expected_status = EXPECTED_STATUS[result[0]]
        url_pep = result[1]
        response = get_response(session, url_pep)
        soup = BeautifulSoup(response.text, 'lxml')
        status_on_page_pep = (
            soup.find(string='Status').find_parent().find_next_sibling().text
        )
        if status_on_page_pep not in expected_status:
            with_different_statuses.append(
                TEXT_WITH_DIFFERENT_STATUSES.format(
                    url_pep=url_pep,
                    status_on_page_pep=status_on_page_pep,
                    expected_status=list(expected_status),
                )
            )

        quantity_pep_in_each_status[status_on_page_pep] += 1

    if with_different_statuses:
        logging.info(
            LOGGING_MESSAGE_DIFFERENT_STATUSES.format(
                with_different_statuses=with_different_statuses
            )
        )
    result = [('Статус', 'Количество')]
    for status, amount in quantity_pep_in_each_status.items():
        result.append((status, amount))
    result.append(('Total', sum(quantity_pep_in_each_status.values())))
    return result


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    try:
        configure_logging()
        arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
        args = arg_parser.parse_args()
        logging.info(LOGGING_COMMAND_LINE_ARGUMENTS.format(args=args))
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results is not None:
            control_output(results, args)
    except Exception:
        logging.exception(LOGGING_EXCEPTION, stack_info=True)
    finally:
        logging.info(PARSE_DONE)


if __name__ == '__main__':
    main()
