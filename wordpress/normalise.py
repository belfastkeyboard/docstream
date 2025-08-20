from typing import Callable
from bs4 import Tag
from bs4.element import NavigableString, PageElement, AttributeValueList
import helper


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


def remove_link(tree: Tag) -> Tag:
    links = tree.find_all('a')

    for link in links:
        if not isinstance(link, Tag):
            continue

        link.name = 'p'

        if 'href' in link.attrs:
            del link.attrs['href']

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


def marxists_normalisation() -> list[Callable]:
    return [remove_classes]


def get_source_normalisation(transform: str = '', **kwargs) -> list[Callable]:
    if not transform:
        return []

    transform = helper.source(transform)

    if transform == 'marxists':
        return marxists_normalisation()

    raise ValueError(f'{transform} not recognised')


def wp_normalisation(**kwargs) -> list[Callable]:
    generic = [
        remove_link,
        remove_newlines,
        strip_attributes,
        lambda c: swap(c, 'strong', 'em'),
        remove_empty,
        clean
    ]

    extra = get_source_normalisation(**kwargs)

    return generic + extra
