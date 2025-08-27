from typing import Callable
from richtext import RichTextDocument, RichText

"""
def remove_empty(tree: Tag) -> Tag:
    def recursive_removal(element: PageElement) -> None:
        if isinstance(element, NavigableString):
            return

        assert isinstance(element, Tag)

        for child in element.children:
            recursive_removal(child)

        if not element.text.strip() and not len(element.contents) > 1:
            element.decompose()

    recursive_removal(tree)

    return tree


def remove_newlines(tree: Tag) -> Tag:
    descendants: list[PageElement] = [d for d in tree.descendants]
    remove: list[NavigableString] = list(filter(lambda d: isinstance(d, NavigableString) and d == '\n', descendants))

    for a in remove:
        a.decompose()

    return tree


def clean(tree: Tag) -> Tag:
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

    for child in tree.descendants:
        if not isinstance(child, NavigableString):
            continue

        text: str = str(child)

        for old, new in table.items():
            text = text.replace(old, new)

        child.replace_with(NavigableString(text))

    return tree


def swap(tree: Tag, old: str, new: str) -> Tag:
    old_elements = tree.find_all(old)

    for old_element in old_elements:
        if not isinstance(old_element, Tag):
            continue

        old_element.name = new

    return tree


def remove_classes(tree: Tag) -> Tag:
    to_remove: set[str] = {'fst'}

    for descendant in tree.descendants:
        if not isinstance(descendant, Tag):
            continue

        if not descendant.attrs or 'class' not in descendant.attrs:
            continue

        classes: set[str] = set(descendant.attrs['class'])
        classes.difference_update(to_remove)
        classes: AttributeValueList[str] = AttributeValueList(classes)
        descendant['class'] = classes

        if not classes:
            del descendant['class']

    return tree


def strip_attributes(tree: Tag) -> Tag:
    tags = [tag for tag in tree.find_all(True) if tag.attrs]

    for tag in tags:
        tag.attrs = {k: v for k, v in tag.attrs.items() if k == "class"}

    return tree


def invert_quotes(tree: Tag) -> Tag:
    def find_child(index: int) -> int:
        assert isinstance(content, Tag)

        current: int = 0
        i = 0

        for i, c in enumerate(content.contents):
            if current < index:
                current = len(c.text)

        return i

    for content in tree.contents:
        assert isinstance(content, Tag)

        text: str = content.text
        matches = re.findall(r'(".*?(?:"|$))', text)

        if not matches:
            continue

        qi = [i for t in map(lambda m: (m.start(), m.end() - 1), map(lambda m: re.search(m, text), matches)) for i in t]

        for quote_index in qi:
            i = find_child(quote_index)
            element = content.contents[i]

            pre = text[:quote_index]
            post = text[quote_index + 1:]
            text = f'{pre}\'{post}'

            if isinstance(element, NavigableString):
                ns = NavigableString(text)
                element.replace_with(ns)
            elif isinstance(element, Tag):
                assert len(element.contents) == 1

                child = element.contents[0]
                ns = NavigableString(text)
                child.replace_with(ns)

    return tree


def marxists_normalisation() -> list[Callable]:
    return [remove_classes]


def get_source_normalisation(transform: str = '', **kwargs) -> list[Callable]:
    if not transform:
        return []

    transform = helper.source(transform)

    if transform == 'marxists':
        return marxists_normalisation()

    raise ValueError(f'{transform} not recognised')
"""


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
    bold_start, bold_end = RichText.get_anchor_chars('bold')
    italic_start, italic_end = RichText.get_anchor_chars('italic')
    translation = str.maketrans(bold_start + bold_end, italic_start + italic_end)

    for rt in document.get(t_style='bold'):
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


def normalisation_pipeline(**kwargs) -> list[Callable[[RichTextDocument], None]]:
    pipeline: list[Callable[[RichTextDocument], None]] = [
        strip_whitespace,
        remove_empty,
        clean,
        swap_italics_for_bold,
        invert_quotations,
        split_on_newlines
    ]

    return pipeline
