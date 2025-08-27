from bs4.element import PageElement, NavigableString
from bs4 import Tag
from typing import Any
from anchors import wrap_text_in_style, remove_anchors, has_style


class RichText:
    def __init__(self, src: Any, text: str, paragraph_styles: set[str]) -> None:
        self.src = src
        self.text: str = text
        self.paragraph_styles: set[str] = paragraph_styles

    def __str__(self):
        text: str = self.text if len(self.text) < 60 else f'{self.text[:58]}...'
        p_style: str = f'[{", ".join([style for style in self.paragraph_styles])}]'
        return f'Text: "{text}" Paragraph Styles: {p_style}'

    @classmethod
    def styled_text_from_html(cls, element: PageElement) -> str:
        style_map: dict[str, str] = {
            'em': 'italic',
            'i': 'italic',
            'strong': 'bold',
            'b': 'bold'
        }

        text: str = ''

        if isinstance(element, Tag):
            for child in element.contents:
                if isinstance(child, Tag) and child.name in style_map:
                    type_name: str = style_map[child.name]
                    run = wrap_text_in_style(child.text, type_name)
                else:
                    run = child.text

                text += run

        return text

    @staticmethod
    def paragraph_styles_from_html(element: PageElement, parent_styles: set[str] | None) -> set[str]:
        if not isinstance(element, Tag) and not isinstance(element, NavigableString):
            raise TypeError(element)

        styles: set[str] = set()

        if isinstance(element, Tag):
            style_map: dict[str, str] = {
                'h1': 'heading1',
                'h2': 'heading2',
                'h3': 'heading3',
                'h4': 'heading4',
                'h5': 'heading5',
                'h6': 'heading6',
                'blockquote': 'blockquote'
            }

            ignore: set[str] = {'body', 'p'}

            if element.name not in ignore:
                styles.add(style_map[element.name])

        if parent_styles:
            styles = styles.union(parent_styles)

        return styles

    @classmethod
    def from_html(cls, element: PageElement, parent_styles: set[str] | None = None):
        text = cls.styled_text_from_html(element)
        paragraph_styles: set[str] = cls.paragraph_styles_from_html(element, parent_styles)

        return cls(element, text, paragraph_styles)

    def has_text_style(self, style: str) -> bool:
        return has_style(self.text, style)

    def has_paragraph_style(self, style: str) -> bool:
        return style in self.paragraph_styles

    def has_text(self, text: str) -> bool:
        return text in remove_anchors(self.text)


class RichTextDocument:
    def __init__(self, text: list[RichText]):
        self.texts = text

    def __str__(self):
        return ' '.join(list(map(lambda rt: rt.text, self.texts)))

    @classmethod
    def from_html(cls, tag: Tag):
        def is_container(element: Tag) -> bool:
            return element.name in {
                'body',
                'div',
                'blockquote'
            }

        def recursive_travel(element: PageElement, parent: set[str] | None = None) -> None:
            if not isinstance(element, Tag) and not isinstance(element, NavigableString):
                raise TypeError(element)

            if isinstance(element, Tag) and is_container(element):
                container = RichText.from_html(element, parent)

                for child in element:
                    recursive_travel(child, container.paragraph_styles)
            else:
                rt = RichText.from_html(element, parent)
                results.append(rt)

        results: list[RichText] = []

        recursive_travel(tag)

        return cls(results)

    def get(self, p_style: str | list[str] = '', t_style: str | list[str] = '', substr: str = '') -> list[RichText]:
        texts: list[RichText] = self.texts
        to_remove: list[RichText] = []

        if p_style:
            if isinstance(p_style, str):
                p_style = [p_style]

            for ps in p_style:
                not_found = list(filter(lambda rt: not rt.has_paragraph_style(ps), texts))
                to_remove.extend(not_found)

        if t_style:
            if isinstance(t_style, str):
                t_style = [t_style]

            for ts in t_style:
                not_found = list(filter(lambda rt: not rt.has_text_style(ts), texts))
                to_remove.extend(not_found)

        if substr:
            not_found = list(filter(lambda rt: not rt.has_text(substr), texts))
            to_remove.extend(not_found)

        return [rt for rt in texts if rt not in to_remove]

    def pop(self) -> RichText | None:
        if not self.texts:
            return None

        return self.texts.pop(0)

    def front(self) -> RichText | None:
        if not self.texts:
            return None

        return self.texts[0]

