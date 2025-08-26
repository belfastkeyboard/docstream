from dataclasses import dataclass
from richtext import RichText, RichTextDocument


@dataclass
class DocRun:
    text: str
    text_styles: set[str]
    paragraph_styles: set[str]


@dataclass
class DocPara:
    runs: list[DocRun]
    styles: set[str]


def _can_split_on_style(text: str, anchors: list[str]) -> str:
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


def _get_anchor_meta() -> tuple[dict, dict, list]:
    anchors_map = RichText.get_style_to_anchors_map()
    items = anchors_map.items()

    start_lookup = {start: style for style, (start, _) in items}
    end_lookup = {end: style for style, (_, end) in items}
    anchors = [a for pair in anchors_map.values() for a in pair]

    return start_lookup, end_lookup, anchors


def adapt_from_rich_text(document: RichTextDocument) -> list[DocRun]:
    def create_runs(texts: list[RichText]):
        start_lookup, end_lookup, anchors = _get_anchor_meta()

        for rt in texts:
            paragraph_styles: set[str] = rt.paragraph_styles
            styles: set[str] = set()
            text: str = rt.text

            while anchor := _can_split_on_style(text, anchors):
                pre, post = text.split(anchor, 1)

                if pre:
                    results.append(DocRun(pre, styles.copy(), paragraph_styles))

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
                text = text + '\n'
                results.append(DocRun(text, styles.copy(), paragraph_styles))

    results: list[DocRun] = []

    create_runs(document.texts)

    return results


def adapt_into_paragraphs_from_rich_text(document: RichTextDocument) -> list[DocPara]:
    results: list[DocPara] = []
    start_lookup, end_lookup, anchors = _get_anchor_meta()

    for rt in document.texts:
        runs: list[DocRun] = []
        styles: set[str] = set()
        paragraph_styles: set[str] = rt.paragraph_styles
        text: str = rt.text

        while anchor := _can_split_on_style(text, anchors):
            pre, post = text.split(anchor, 1)

            if pre:
                runs.append(DocRun(pre, styles.copy(), paragraph_styles))

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
            runs.append(DocRun(text, styles.copy(), paragraph_styles))

        results.append(DocPara(runs, paragraph_styles))

    return results
