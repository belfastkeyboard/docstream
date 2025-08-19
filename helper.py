from dataclasses import dataclass
from bs4.element import PageElement


@dataclass
class HTMLElement:
    data: PageElement
    styles: set[str]
