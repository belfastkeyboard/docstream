from dataclasses import dataclass
from bs4 import Tag
from bs4.element import PageElement, NavigableString
from enum import Enum
from bs4 import Tag


class TextStyleType(Enum):
    ITALIC = 0
    BOLD = 1


class ParagraphStyleType(Enum):
    LEFT_ALIGNED = 0
    RIGHT_ALIGNED = 1
    CENTRE_ALIGNED = 2
    HEADING_1 = 3
    HEADING_2 = 4
    HEADING_3 = 5
    HEADING_4 = 6
    HEADING_5 = 7
    HEADING_6 = 8
    NORMAL = 9


@dataclass
class TextStyle:
    type: TextStyleType
    start: int
    end: int


class StructuredText:
    def __init__(self, text: str, styles: list[TextStyle], paragraph_styles: list[ParagraphStyleType]) -> None:
        self.text: str = text
        self.styles: list[TextStyle] = styles
        self.paragraph_styles: list[ParagraphStyleType] = paragraph_styles

    @staticmethod
    def text_from_html(element: PageElement) -> str:
        if isinstance(element, NavigableString):
            return str(element)
        elif isinstance(element, Tag):
            return element.text

        raise TypeError(f'{element} is wrong type')

    @staticmethod
    def paragraph_styles_from_html(element: PageElement) -> list[ParagraphStyleType]:
        if isinstance(element, NavigableString):
            return [ParagraphStyleType.NORMAL]
        elif isinstance(element, Tag):
            style_map: dict = {
                'p': ParagraphStyleType.NORMAL,
                'h1': ParagraphStyleType.HEADING_1,
                'h2': ParagraphStyleType.HEADING_2,
                'h3': ParagraphStyleType.HEADING_3,
                'h4': ParagraphStyleType.HEADING_4,
                'h5': ParagraphStyleType.HEADING_5,
                'h6': ParagraphStyleType.HEADING_6
            }

        raise TypeError(f'{element} is wrong type')

    @classmethod
    def from_html(cls, element: PageElement):
        text: str = cls.text_from_html(element)
        styles: list[TextStyle] = []
        paragraph_styles: list[ParagraphStyleType] = cls.paragraph_styles_from_html(element)

        return cls(text, styles, paragraph_styles)


class Body:
    def __init__(self, text: list[StructuredText]):
        self.texts = text

    # lazy getters
    def get(self, paragraph_style: str = '', text_style: str or list[str] = '' ) -> list[StructuredText]:
        pass

        # default values should return StructuredText


"""
    Consider using enums instead of text for safety
"""
