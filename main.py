import re
from bs4 import BeautifulSoup
from get import get_content
from bs4 import ResultSet, Tag
from bs4.element import NavigableString, PageElement
from send import send_to_docs


class Ripper:
    def __init__(self, html: bytes) -> None:
        self.html: BeautifulSoup = BeautifulSoup(html, 'html.parser')

    def meta(self) -> dict[str, str]:
        meta: ResultSet = self.html.find_all('meta')

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
        title: Tag = self.html.find('title')
        return title.text if title else ''

    def page(self) -> list[PageElement]:
        body: Tag = self.html.find('body')
        return [tag for tag in body.children]


class Cleaner:
    def __init__(self, text: list[PageElement]) -> None:
        self.text = text

    def clean(self) -> None:
        replacements: dict[str, str] = {
            '“': '"',
            '”': '"',
            '‘': '\'',
            '’': '\'',
            '–': '—',
            ' —': '—',
            '— ': '—'
        }

        for element in self.text:
            for old, new in replacements.items():
                if isinstance(element, Tag):
                    element.string = element.text.replace(old, new)

    def invert_quotes(self):
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

        for element in self.text:
            if isinstance(element, Tag):
                element.string = re.sub(r'(".*?")', sub_quotes, element.text)

    def join(self) -> str:
        return ''.join(element.text for element in self.text)


def main() -> None:
    # url: str = 'https://www.marxists.org/archive/connolly/1908/06/harpb.htm'
    # content: bytes = get_content(url)
    # ripper = Ripper(content)
    # cleaner = Cleaner(ripper.page())
    # cleaner.clean()
    # cleaner.invert_quotes()
    #
    # print(cleaner.join())

    send_to_docs('hello')


if __name__ == '__main__':
    main()
