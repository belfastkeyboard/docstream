from bs4 import BeautifulSoup
from bs4 import ResultSet, Tag
from bs4.element import PageElement
from send import DocNode
from dataclasses import dataclass


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


def nodes(soup: BeautifulSoup) -> list[DocNode]:
    @dataclass
    class Element:
        data: PageElement
        styles: set[str]

    def flatten(element: Element) -> None:
        style: str = element.data.name if isinstance(element.data, Tag) else 'p'
        element.styles.add(style)

        if isinstance(element.data, Tag) and len(element.data.contents) > 1:
            for content in element.data.contents:
                content = Element(content, element.styles.copy())
                flatten(content)
        else:
            node = DocNode.from_html(element.data, element.styles)
            result.append(node)

    result: list = []

    body: Tag = soup.find('body')

    for e in body:
        e = Element(e, set())
        flatten(e)

    return result


def marxists(soup: BeautifulSoup) -> None:
    to_decompose: list = [
        soup.find('p', class_='toplink'),
        soup.find('p', class_='link'),
        soup.find('p', class_='updat')

    ]

    for element in to_decompose:
        if element:
            element.decompose()
