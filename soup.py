from bs4 import BeautifulSoup
from bs4 import ResultSet, Tag
from send import DocNode
from helper import HTMLElement


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


def nodes(soup: BeautifulSoup, transform: str = '') -> list[DocNode]:
    def flatten(element: HTMLElement) -> None:
        style: str = element.data.name if isinstance(element.data, Tag) else 'p'
        element.styles.add(style)

        if isinstance(element.data, Tag) and len(element.data.contents) > 1:
            for content in element.data.contents:
                content = HTMLElement(content, element.styles.copy())
                flatten(content)
        else:
            node = DocNode.from_html(element, transform)
            result.append(node)

    result: list = []

    body: Tag = soup.find('body')

    for e in body:
        e = HTMLElement(e, set())
        flatten(e)

    return result
