from .normalise import docs_normalisation
from .send import to_docs
from .type import DocNode, HTMLElement
from .style import make_style_docs_compliant

__all__ = [
    'DocNode', 'HTMLElement',
    'docs_normalisation', 'to_docs', 'make_style_docs_compliant'
]
