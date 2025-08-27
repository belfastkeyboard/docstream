from richtext import RichTextDocument
from anchors import remove_anchors


def build_text(document: RichTextDocument) -> str:
    stripped_text: list[str] = []

    for rt in document.texts:
        st: str = remove_anchors(rt.text)
        stripped_text.append(st)

    return '\n'.join(stripped_text)


def to_txt(document: RichTextDocument, metadata: dict | None = None, **kwargs) -> None:
    title: str = metadata['title']
    publication: str = metadata['publication']
    date: str = metadata['date']

    text: str = build_text(document)
    fn: str = f'{title}.txt'

    with open(fn, 'w') as file:
        file.write(text)
