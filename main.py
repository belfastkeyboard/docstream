import re
from bs4 import BeautifulSoup
from get import get_content
from bs4 import ResultSet, Tag
from bs4.element import NavigableString, PageElement
from send import send_to_docs, DocNode


class Ripper:
    def __init__(self, html: bytes) -> None:
        self.soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')

    def meta(self) -> dict[str, str]:
        meta: ResultSet = self.soup.find_all('meta')

        result: dict[str, str] = {}

        for data in meta:
            try:
                if data.attrs['name'] in ['description', 'keywords', 'author']:
                    key: str = data.attrs['name']
                    value: str = data.attrs['content']
                    result[key] = value
            except KeyError:
                continue

        return result

    def title(self) -> str:
        title: Tag = self.soup.find('title')
        return title.text if title else ''

    def body(self) -> Tag | None:
        body: Tag = self.soup.find('body')
        return body

    def _flatten(self, result: list, element: PageElement, parent: list = None) -> None:
        if parent:
            styles = parent
            styles.append(element.name if isinstance(element, Tag) else 'p')
        else:
            styles = [element.name if isinstance(element, Tag) else 'p']

        if isinstance(element, NavigableString):
            # if element == '\n':
            #     return

            result.append(DocNode(styles, element))
        elif isinstance(element, Tag):
            if len(element.contents) > 1:
                if not parent:
                    parent = []

                if element.name == 'blockquote':
                    parent.append('blockquote')

                for content in element.contents:
                    self._flatten(result, content, parent)
            else:
                result.append(DocNode(styles, element.text))

    @staticmethod
    def _merge(nodes: list[DocNode]) -> None:
        i: int = 0

        while i < len(nodes) - 1:
            node: DocNode = nodes[i]
            next_node: DocNode = nodes[i + 1]

            if node.styles == next_node.styles:
                node.text = node.text + next_node.text
                nodes.pop(i + 1)
            else:
                i += 1

    def page(self) -> list[DocNode]:
        result: list = []

        body: Tag = self.body()

        for element in body:
            self._flatten(result, element)

        self._merge(result)

        return result


class Cleaner:
    def __init__(self, text: list[DocNode]) -> None:
        self.text: list[DocNode] = text

    def clean(self) -> None:
        replacements: dict[str, str] = {
            '\r': '',
            '“': '"',
            '”': '"',
            '‘': '\'',
            '’': '\'',
            '–': '—',
            ' —': '—',
            '— ': '—',
            '\u00A0': ' '
        }

        for node in self.text:
            for old, new in replacements.items():
                node.text = node.text.replace(old, new)

    def invert_quotes(self) -> None:
        def sub_quotes(match) -> str:
            text: str = match.group(1)
            nested = list(re.finditer(r'(?<!\w)\'([^\']+)\'(?!\w)', text))

            text = text.replace('"', '\'')

            for match in nested:
                start, end = match.span(1)
                pre: str = text[:start - 1]
                post: str = text[end + 1:]
                quote: str = text[start:end]
                text = f'{pre}"{quote}"{post}'

            return text

        for node in self.text:
            node.text = re.sub(r'(".*?")', sub_quotes, node.text)

    def join(self) -> str:
        return ''.join(node.text for node in self.text)

    def swap(self, old: str, new: str) -> None:
        for element in self.text:
            if old in element.styles:
                i = element.styles.index(old)
                element.styles[i] = new


def main() -> None:
    url: str = 'https://www.marxists.org/archive/connolly/1908/06/harpb.htm'
    content: bytes = get_content(url)
    ripper = Ripper(content)
    cleaner = Cleaner(ripper.page())
    cleaner.clean()
    cleaner.invert_quotes()
    cleaner.swap('strong', 'em')

    send_to_docs(cleaner.text)


if __name__ == '__main__':
    main()
