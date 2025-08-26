from richtext import RichTextDocument
from docx import Document


"""
    .docx
        iv.     create doc run (share with google docs?)
        v.      formatted doc file
"""


def to_blob(document: RichTextDocument, doc: Document) -> None:
    for rt in document.texts:
        st: str = rt.remove_anchors()
        doc.add_paragraph(st)


def to_docx(document: RichTextDocument, metadata: dict | None = None, **kwargs) -> None:
    title: str = metadata['title']
    publication: str = metadata['publication']
    date: str = metadata['date']

    fn: str = f'{title}.docx'

    doc = Document()

    to_blob(document, doc)

    doc.save(fn)
