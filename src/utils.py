from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException
from constants import UTF_8
import requests

TEXT_EXCEPTION = 'Возникла ошибка при загрузке страницы {url}'
ERROR_MESSAGE = 'Не найден тег {tag} {attrs}'

res = requests.get(
    'https://en.wikipedia.org/wiki/List_of_pages',
)


def get_response(session, url, utf_8=UTF_8):
    try:
        response = session.get(url)
        response.encoding = utf_8
        return response
    except RequestException:
        raise RequestException(TEXT_EXCEPTION.format(url=url))


def get_soup(session, url):
    response = get_response(session, url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs if attrs is not None else {}))
    if searched_tag is None:
        raise ParserFindTagException(
            ERROR_MESSAGE.format(tag=tag, attrs=attrs)
        )
    return searched_tag


def find_all_tags(soup, tag, attrs=None):
    searched_tags = soup.find_all(tag, attrs=(attrs or {}))
    if not searched_tags:
        raise ParserFindTagException(
            ERROR_MESSAGE.format(tag=tag, attrs=attrs)
        )
    return searched_tags
