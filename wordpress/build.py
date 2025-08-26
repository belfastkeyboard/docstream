import re
from richtext import RichText, RichTextDocument
from bs4 import BeautifulSoup
from bs4.element import Comment, Tag


def _get_child(tag_type: str, document: RichTextDocument) -> RichText | None:
    if not _get_wrapper_class(tag_type) or not document.texts:
        return None

    next_rt: RichText = document.texts[0]

    if tag_type not in next_rt.paragraph_styles:
        return None

    return document.pop()


def _get_wrapper_class(tag: str) -> list[str]:
    wrapper_blocks: dict[str, list[str]] = {'blockquote': ['wp-block-quote']}

    return wrapper_blocks.get(tag, [])


def _apply_style_classes(tag: Tag, paragraph_styles: set[str]) -> None:
    style_map = {
        'align-right': 'has-text-align-right',
        'align-centre': 'has-text-align-center'
    }

    classes = [v for k, v in style_map.items() if k in paragraph_styles]

    if classes:
        _add_class(tag, classes)


def _add_class(tag: Tag, cls: str | list[str]) -> None:
    classes = tag.attrs.get('class', [])

    if isinstance(cls, str):
        classes.append(cls)
    else:
        classes.extend(cls)

    tag['class'] = classes


def _get_tag_type(paragraph_styles: set[str]) -> str:
    paragraph_style_to_html_name_map: dict[str, str] = {
        'heading1': 'h1',
        'heading2': 'h2',
        'heading3': 'h3',
        'heading4': 'h4',
        'heading5': 'h5',
        'heading6': 'h6',
        'blockquote': 'blockquote'
    }

    name: str = 'p'

    for ps in paragraph_styles:
        name = paragraph_style_to_html_name_map.get(ps, 'p')

        if name != 'p':
            break

    return name


def _get_block_name(tag: str) -> str:
    block_map: dict[str, str] = {
        'p': 'paragraph',
        'h1': 'heading',
        'h2': 'heading',
        'h3': 'heading',
        'h4': 'heading',
        'h5': 'heading',
        'h6': 'heading',
        'blockquote': 'quote',
        # 'ul': 'list {"ordered":false}',
        # 'ol': 'list {"ordered":true}',
        # 'li': 'list-item',
        # 'pre': 'code',
        # 'code': 'code',
        # 'img': 'image',
        # 'table': 'table'
    }

    return block_map[tag]


def _get_block_attribute(paragraph_styles: set[str]) -> str:
    attr_map: dict[str, str] = {
        'heading1': '"level":1',
        'heading2': '"level":2',
        'heading3': '"level":3',
        'heading4': '"level":4',
        'heading5': '"level":5',
        'heading6': '"level":6',
        'align-centre': '"align":"centre"',
        'align-right': '"align":"right"'
    }

    attributes = [v for k, v in attr_map.items() if k in paragraph_styles]
    result: str = f' {{{",".join(attributes)}}}' if attributes else ''

    return result


def _build_container_class(
    soup: BeautifulSoup,
    document: RichTextDocument,
    tag: Tag,
    tag_type: str,
    rt: RichText
) -> Tag:
    rt.paragraph_styles.remove(tag_type)
    _build_tag(soup, tag, document, rt)

    while child := _get_child(tag_type, document):
        child.paragraph_styles.remove(tag_type)
        _build_tag(soup, tag, document, child)

    return tag


def _replace_anchors_with_tags(text: str) -> str:
    anchors_to_tags = {
        '\uE000': '<em>',
        '\uE001': '</em>',
        '\uE002': '<strong>',
        '\uE003': '</strong>'
    }

    for old, new in anchors_to_tags.items():
        text = text.replace(old, new)

    pattern = re.compile(r"[\uE000-\uF8FF]")
    matches = pattern.findall(text)

    assert not matches

    return text


def _build_tag_text(tag: Tag, text: str) -> None:
    text = _replace_anchors_with_tags(text)
    soup = BeautifulSoup(text, 'html.parser')

    for child in list(soup.children):
        tag.append(child.extract())


def _insert_tag(tag: Tag, parent: Tag, tag_type: str, paragraph_styles: set[str]) -> None:
    block_name: str = _get_block_name(tag_type)
    block_attribute: str = _get_block_attribute(paragraph_styles)

    parent.append(tag)
    tag.insert_before(Comment(f' wp:{block_name}{block_attribute} '))
    tag.insert_after(Comment(f' /wp:{block_name} '))


def _build_tag(soup: BeautifulSoup, parent: Tag, document: RichTextDocument, rt: RichText) -> None:
    tag_type: str = _get_tag_type(rt.paragraph_styles)
    tag = soup.new_tag(tag_type)

    if wrapper_class := _get_wrapper_class(tag_type):
        tag = _build_container_class(soup, document, tag, tag_type, rt)
        _add_class(tag, wrapper_class)
    else:
        _build_tag_text(tag, rt.text)

    _insert_tag(tag, parent, tag_type, rt.paragraph_styles)
    _apply_style_classes(tag, rt.paragraph_styles)


def _build_body(soup: BeautifulSoup, document: RichTextDocument) -> None:
    while rt := document.pop():
        _build_tag(soup, soup, document, rt)


def build_html_from_document(document: RichTextDocument) -> BeautifulSoup:
    soup = BeautifulSoup()

    _build_body(soup, document)

    return soup
