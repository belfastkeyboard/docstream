from dataclasses import dataclass
from bs4 import Tag
from bs4.element import PageElement
import helper
from .style import marxists_style


@dataclass
class HTMLElement:
    data: PageElement
    styles: set[str]


class DocNode:
    def __init__(self, styles: set[str], text: str):
        self.text = text
        self.styles = styles

    def __str__(self):
        return f'DocNode({self.styles}, {self.text})'

    @staticmethod
    def get_additional_styles(transform: str) -> dict[str, str]:
        if not transform:
            return {}
        elif helper.source(transform) == 'marxists':
            return marxists_style()

        raise ValueError(f'{transform} not recognised')

    @staticmethod
    def get_styles_map() -> dict[str, str]:
        return {
            'b': 'bold',
            'strong': 'bold',
            'i': 'italic',
            'em': 'italic',
            'p': 'text',
            'a': 'text',
            'h1': 'HEADING_1',
            'h2': 'HEADING_2',
            'h3': 'HEADING_3',
            'h4': 'HEADING_4',
            'h5': 'HEADING_5',
            'h6': 'HEADING_6',
            'hr': 'separator',
            'br': 'break',
            'blockquote': 'blockquote'
        }

    @classmethod
    def from_html(cls, element: HTMLElement, transform: str = ''):
        styles_map = DocNode.get_styles_map()

        text: str = element.data.text if isinstance(element.data, Tag) else str(element.data)
        styles: set[str] = element.styles

        mapped_styles: set[str] = {styles_map[style] for style in styles}

        if transform and isinstance(element.data, Tag) and len(element.data.attrs):
            transform_styles: dict[str, str] = cls.get_additional_styles(transform)
            class_styles: set[str] = set(element.data.attrs.get('class', []))
            extra_styles = {transform_styles[style] for style in class_styles if style in transform_styles}
            mapped_styles.update(extra_styles)

        return cls(mapped_styles, text)
