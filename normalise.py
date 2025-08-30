from typing import Callable
from richtext import RichTextDocument, RichText
from anchors import get_style_anchors


def remove_empty(document: RichTextDocument) -> None:
    document.texts = list(filter(lambda rt: rt.text, document.texts))


def strip_whitespace(document: RichTextDocument) -> None:
    for rt in document.texts:
        rt.text = rt.text.strip()


def clean(document: RichTextDocument) -> None:
    table: dict[str, str] = {
        '\r': '',
        '“': '"',
        '”': '"',
        '’': '\'',
        '‘': '\'',
        '–': '—',
        ' —': '—',
        '— ': '—'
    }

    for rt in document.texts:
        for old, new in table.items():
            rt.text = rt.text.replace(old, new)


def swap_italics_for_bold(document: RichTextDocument) -> None:
    bold_start, bold_end = get_style_anchors('bold')
    italic_start, italic_end = get_style_anchors('italic')
    translation = str.maketrans(bold_start + bold_end, italic_start + italic_end)

    for rt in document.get(text_style='bold'):
        rt.text = rt.text.translate(translation)


def invert_quotations(document: RichTextDocument) -> None:
    for rt in document.get(substr='"'):
        rt.text = rt.text.replace('"', "'")


def split_on_newlines(document: RichTextDocument) -> None:
    new_texts: list[RichText] = []

    for rt in document.texts:
        if '\n' not in rt.text:
            new_texts.append(rt)
        else:
            split: list[str] = rt.text.split('\n')

            for s in split:
                new_texts.append(RichText(rt.src, s, rt.paragraph_styles))

    document.texts = new_texts


def normalisation_pipeline() -> list[Callable[[RichTextDocument], None]]:
    pipeline: list[Callable[[RichTextDocument], None]] = [
        strip_whitespace,
        remove_empty,
        clean,
        swap_italics_for_bold,
        invert_quotations,
        split_on_newlines
    ]

    return pipeline
