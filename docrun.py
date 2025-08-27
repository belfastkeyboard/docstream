from dataclasses import dataclass
from richtext import RichText, RichTextDocument
from anchors import split_on_style, is_open_anchor, is_close_anchor, get_style_from_anchor


@dataclass
class DocRun:
    text: str
    text_styles: set[str]
    paragraph_styles: set[str]


@dataclass
class DocPara:
    runs: list[DocRun]
    styles: set[str]


def adapt_from_rich_text(document: RichTextDocument) -> list[DocRun]:
    def create_runs(texts: list[RichText]):
        for rt in texts:
            paragraph_styles: set[str] = rt.paragraph_styles
            styles: set[str] = set()
            text: str = rt.text

            while split := split_on_style(text):
                style, pre, post = split

                if pre:
                    results.append(DocRun(pre, styles.copy(), paragraph_styles))

                if is_open_anchor(style):
                    styles.add(get_style_from_anchor(style))
                elif is_close_anchor(style):
                    styles.remove(get_style_from_anchor(style))

                text = post

            if text:
                text = text + '\n'
                results.append(DocRun(text, styles.copy(), paragraph_styles))

    results: list[DocRun] = []

    create_runs(document.texts)

    return results


def adapt_into_paragraphs_from_rich_text(document: RichTextDocument) -> list[DocPara]:
    results: list[DocPara] = []

    for rt in document.texts:
        runs: list[DocRun] = []
        styles: set[str] = set()
        paragraph_styles: set[str] = rt.paragraph_styles
        text: str = rt.text

        while split := split_on_style(text):
            style, pre, post = split

            if pre:
                runs.append(DocRun(pre, styles.copy(), paragraph_styles))

            if is_open_anchor(style):
                styles.add(get_style_from_anchor(style))
            elif is_close_anchor(style):
                styles.remove(get_style_from_anchor(style))

            text = post

        if text:
            runs.append(DocRun(text, styles.copy(), paragraph_styles))

        results.append(DocPara(runs, paragraph_styles))

    return results
