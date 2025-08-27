from typing import Any, Callable
from yarl import URL
from bs4 import BeautifulSoup, Tag
from .fetch import fetch_url_content
from .html import get_html_body
from richtext import RichText, RichTextDocument
from typing import TypedDict


class PipelineData(TypedDict):
    source: Any
    document: RichTextDocument
    metadata: dict[str, str]


def is_source_a_url(source) -> bool:
    try:
        url = URL(source)
        return url.scheme in ['http', 'https'] and url.host is not None
    except ValueError:
        return False


def get_source_type(source) -> str:
    checkers: list[Callable] = [is_source_a_url]
    types: list[str] = ['url']

    for func, st in zip(checkers, types):
        if not func(source):
            continue

        return st

    raise TypeError(f'source type: {type(source)} is not valid')


def do_get_data(source) -> Any:
    src_type: str = get_source_type(source)

    if src_type == 'url':
        return fetch_url_content(source)
    else:
        raise ValueError(f'{src_type} not recognised')


def modify_source(content, plugins: dict | None = None, **kwargs) -> Any:
    if not plugins or not plugins.get('modify-source'):
        return content
    else:
        _modify = plugins.get('modify-source')[0]
        content = _modify(content, **kwargs)

    return content


def get_body_generic(content, **kwargs) -> Tag:
    if isinstance(content, BeautifulSoup):
        return get_html_body(content, **kwargs)

    raise TypeError(f'Unhandled type: {type(content)}')


def adaptor(content: Any, plugins: dict or None = None, **kwargs) -> RichTextDocument:
    if isinstance(content, Tag):
        doc = RichTextDocument.from_html(content)
    else:
        raise TypeError(f'{content} unhandled')

    adaptor_plugins: list[Callable[[RichText], None]] = plugins.get('adaptor', []) if plugins else []

    for rt in doc.texts:
        for f in adaptor_plugins:
            f(rt)

    return doc


def get_metadata_generic(content, **kwargs) -> tuple[str, str, str]:
    return '', '', ''


def get_metadata(content: Any, plugins: dict | None = None, **kwargs) -> dict[str, str]:
    if not plugins or not plugins.get('meta'):
        title, publication, date = get_metadata_generic(content, **kwargs)
    else:
        _get_meta = plugins.get('meta')[0]
        title, publication, date = _get_meta(content, **kwargs)

    return {
        'title': title,
        'publication': publication,
        'date': date
    }


def get_pipeline_data(source, **kwargs) -> PipelineData:
    source = do_get_data(source)
    content = modify_source(source, **kwargs)
    body: Any = get_body_generic(content, **kwargs)
    document: RichTextDocument = adaptor(body, **kwargs)
    metadata: dict[str, str] = get_metadata(content, **kwargs)

    return {
        'document': document,
        'source': source,
        'metadata': metadata
    }
