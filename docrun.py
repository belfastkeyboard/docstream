from dataclasses import dataclass
from richtext import RichText, RichTextDocument
from anchors import split_on_style, is_open_anchor, is_close_anchor, get_style_from_anchor
import re


@dataclass
class DocRun:
    text: str
    text_styles: set[str]
    paragraph_styles: set[str]


@dataclass
class DocPara:
    runs: list[DocRun]
    styles: set[str]


def make_quotes_curved(text: str) -> str:
    # Leading apostrophe contractions e.g. ['tis] -> [’tis]
    text = re.sub(r"(?<![a-zA-Z])'(?=" + '|'.join(['tis', 'twas', 'twere', 'em', 'cause']) + r")", '’', text)

    # Contractions and singular possessives e.g [isn't] -> [isn’t]
    text = re.sub(r"(?<=\w)'(?=\w)", "’", text)

    # Apostrophes before numbers ['98] -> [’98]
    text = re.sub(r"'(?=\d)", "’", text)

    # Opening single quotes e.g. ['quote] -> [‘quote]
    text = re.sub(r"(^|[\s(\[{])'(?=\w)", r"\1‘", text)

    # Closing single quotes and plural possessives e.g. [plurals'] -> [plurals’]
    text = text.replace("'", "’")

    # Opening double quotes e.g. ["quote] -> [“quote]
    text = re.sub(r'(^|[\s(\[{])"(?=\S)', r'\1“', text)

    # Closing double quotes e.g. [quote"] -> [quote”]
    text = text.replace('"', '”')

    return text


def create_run(results: list[DocRun], text: str, styles: set[str], p_styles: set[str], quotes: bool) -> None:
    if quotes:
        text = make_quotes_curved(text)

    results.append(DocRun(text, styles.copy(), p_styles))


def adapt_from_rich_text(document: RichTextDocument, curved_quotes: bool = False) -> list[DocRun]:
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
                create_run(results, text + '\n', styles, paragraph_styles, curved_quotes)

    results: list[DocRun] = []

    create_runs(document.texts)

    return results


def adapt_into_paragraphs_from_rich_text(document: RichTextDocument, curved_quotes: bool = False) -> list[DocPara]:
    results: list[DocPara] = []

    for rt in document.texts:
        runs: list[DocRun] = []
        styles: set[str] = set()
        paragraph_styles: set[str] = rt.paragraph_styles
        text: str = rt.text

        while split := split_on_style(text):
            style, pre, post = split

            if pre:
                create_run(runs, pre, styles, paragraph_styles, curved_quotes)

            if is_open_anchor(style):
                styles.add(get_style_from_anchor(style))
            elif is_close_anchor(style):
                styles.remove(get_style_from_anchor(style))

            text = post

        if text:
            create_run(runs, text, styles, paragraph_styles, curved_quotes)

        results.append(DocPara(runs, paragraph_styles))

    return results
