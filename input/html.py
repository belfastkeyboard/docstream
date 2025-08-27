from bs4 import BeautifulSoup
from bs4 import ResultSet, Tag


def title(soup: BeautifulSoup) -> str:
    result: str = ''

    element: Tag = soup.find('title')

    if element:
        result = element.text

    return result


def metadata(soup: BeautifulSoup) -> dict[str, str]:
    result: dict[str, str] = {}

    meta: ResultSet = soup.find_all('meta')

    for data in meta:
        try:
            if data.attrs['name'] in ['description', 'keywords', 'author']:
                key: str = data.attrs['name']
                value: str = data.attrs['content']
                result[key] = value
        except KeyError:
            continue

    return result


def get_html_body(soup: BeautifulSoup, **kwargs) -> BeautifulSoup:
    return soup.find('body')
