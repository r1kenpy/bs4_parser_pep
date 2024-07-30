from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import ParserFindTagException

TEXT_EXCEPTION = 'Возникла ошибка при загрузке страницы {url} {e}'
ERROR_MESSAGE = 'Не найден тег {tag} {attrs}'


def get_response(session, url, encoding='utf-8'):
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException as e:
        raise ConnectionError(TEXT_EXCEPTION.format(url=url, e=e))


def get_soup(session, url, parser='lxml'):
    return BeautifulSoup(get_response(session, url).text, parser)


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs if attrs is not None else {}))
    if searched_tag is None:
        raise ParserFindTagException(
            ERROR_MESSAGE.format(tag=tag, attrs=attrs)
        )
    return searched_tag
