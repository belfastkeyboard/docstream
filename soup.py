from bs4 import BeautifulSoup
from bs4 import ResultSet, Tag
from google_docs import DocNode, HTMLElement


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


def nodes(tag: Tag, transform: str = '') -> list[DocNode]:
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

    def merge(node_list: list[DocNode]) -> list[DocNode]:
        i = 0

        while i < len(node_list) - 1:
            node: DocNode = node_list[i]
            next_node: DocNode = node_list[i + 1]

            if node.styles == next_node.styles:
                node.text += '\n' + next_node.text
                node_list.pop(i + 1)
            else:
                i += 1

        return node_list

    result: list = []

    for e in tag:
        e = HTMLElement(e, set())
        flatten(e)

    return merge(result)


def tree(soup: BeautifulSoup, **kwargs) -> BeautifulSoup:
    return soup.find('body')
