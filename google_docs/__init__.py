from .normalise import docs_normalisation
from .send import to_docs
from .type import DocNode, HTMLElement

__all__ = [
    'DocNode', 'HTMLElement',
    'docs_normalisation', 'to_docs'
]
