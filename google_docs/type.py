from dataclasses import dataclass
from bs4 import Tag
from bs4.element import PageElement
import helper
from .style import marxists_style
from generic import RichText, RichTextDocument


@dataclass
class DocRun:
    text: str
    text_styles: set[str]
    paragraph_styles: set[str]


def adapt_from_rich_text(document: RichTextDocument) -> list[DocRun]:
    def get_anchor_meta() -> tuple[dict, dict, list]:
        anchors_map = RichText.get_style_to_anchors_map()
        items = anchors_map.items()

        start_lookup = {start: style for style, (start, _) in items}
        end_lookup = {end: style for style, (_, end) in items}
        anchors = [a for pair in anchors_map.values() for a in pair]

        return start_lookup, end_lookup, anchors

    def can_split_on_style(text: str, anchors: list[str]) -> str:
        i: int = 0
        found: str = ''

        while i < len(text):
            char: str = text[i]

            if char not in anchors:
                i += 1
                continue

            found = char
            break

        return found

    def create_run(t: str, ts: set, ps: set) -> None:
        results.append(DocRun(t, ts, ps))

    def create_runs(texts: list[RichText]):
        start_lookup, end_lookup, anchors = get_anchor_meta()

        for rt in texts:
            paragraph_styles: set[str] = rt.paragraph_styles
            styles: set[str] = set()
            text: str = rt.text

            while anchor := can_split_on_style(text, anchors):
                pre, post = text.split(anchor, 1)

                if pre:
                    create_run(pre, styles.copy(), paragraph_styles)

                if anchor in start_lookup:
                    name: str = start_lookup[anchor]
                    styles.add(name)
                elif anchor in end_lookup:
                    name: str = end_lookup[anchor]
                    styles.remove(name)
                else:
                    raise ValueError(f'Unknown anchor: {anchor}')

                text = post

            if text:
                create_run(text + '\n', styles.copy(), paragraph_styles)

    results: list[DocRun] = []

    create_runs(document.texts)

    return results
