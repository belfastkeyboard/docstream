from richtext import RichTextDocument
from anchors import remove_anchors
from pathlib import Path
from input import Metadata


def build_text(document: RichTextDocument) -> str:
    stripped_text: list[str] = []

    for rt in document.texts:
        st: str = remove_anchors(rt.text)
        stripped_text.append(st)

    return '\n'.join(stripped_text)


def to_txt(document: RichTextDocument, metadata: Metadata) -> None:
    title: str = metadata['title']
    publication: str = metadata['publication']
    date: str = metadata['date']

    text: str = build_text(document)

    directory = Path('export')
    fn = Path(directory, f'{title}.txt')
    directory.mkdir(exist_ok=True)

    with open(fn, 'w') as file:
        file.write(text)
