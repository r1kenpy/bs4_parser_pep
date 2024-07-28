import csv
import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_URL
from outputs import control_output
from utils import find_all_tags, find_tag, get_response


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for section in tqdm(sections_by_python):
        version_link = urljoin(whats_new_url, find_tag(section, 'a')['href'])
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
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'html.parser')
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise Exception('Ничего не нашлось')
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
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)

    if response is None:
        return

    soup = BeautifulSoup(response.text, 'lxml')
    table_tag = find_tag(soup, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    archive_url = urljoin(downloads_url, pdf_a4_tag['href'])
    filename = archive_url.split('/')[-1]
    download_dir = BASE_DIR / 'downloads'
    download_dir.mkdir(exist_ok=True)
    archive_path = download_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as f:
        f.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    response = get_response(session, PEP_URL)
    soup = BeautifulSoup(response.text, 'lxml')
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
    quantity_pep_in_each_status = {}
    for result in tqdm(results_link):
        expected_status = EXPECTED_STATUS[result[0]]
        url_pep = result[1]
        response = session.get(url_pep)
        soup = BeautifulSoup(response.text, 'lxml')
        status_on_page_pep = (
            soup.find(string='Status').find_parent().find_next_sibling().text
        )
        if status_on_page_pep not in expected_status:
            logging.info(
                f'\nНесовпадающие статусы у: [{url_pep}];\n'
                f'Статус в карточке: {status_on_page_pep};\n'
                f'Ожидаемые статусы: {list(expected_status)}'
            )
        quantity_pep_in_each_status[status_on_page_pep] = (
            quantity_pep_in_each_status.setdefault(status_on_page_pep, 0) + 1
        )
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    with open(
        results_dir / 'pep_status.csv', 'w', encoding='utf-8'
    ) as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Статус', 'Количество'])
        for key, value in quantity_pep_in_each_status.items():
            csv_writer.writerow([key, value])
        csv.writer(csv_file).writerow(
            ['Total', sum(quantity_pep_in_each_status.values())]
        )


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
