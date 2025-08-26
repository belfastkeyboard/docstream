import fetch
import soup
from yarl import URL
from typing import Any, Callable
from bs4 import BeautifulSoup, Tag
import helper
from output import to_docs, to_docx, to_txt, to_wordpress
from normalise import normalisation_pipeline
from richtext import RichTextDocument, RichText
from typing import TypedDict


class PipelineData(TypedDict):
    source: Any
    document: RichTextDocument
    metadata: dict[str, str]


def _is_source_a_url(source) -> bool:
    try:
        url = URL(source)
        return url.scheme in ['http', 'https'] and url.host is not None
    except ValueError:
        return False


def _get_source_type(source) -> str:
    checkers: list[Callable] = [_is_source_a_url]
    types: list[str] = ['url']

    for func, st in zip(checkers, types):
        if not func(source):
            continue

        return st

    raise TypeError(f'source type: {type(source)} is not valid')


def _get_body_generic(content, **kwargs) -> Tag:
    if isinstance(content, BeautifulSoup):
        return soup.tree(content, **kwargs)

    raise TypeError(f'Unhandled type: {type(content)}')


def _modify_source(content, plugins: dict | None = None, **kwargs) -> Any:
    if not plugins or not plugins.get('modify-source'):
        return content
    else:
        _modify = plugins.get('modify-source')[0]
        content = _modify(content, **kwargs)

    return content


def _do_get_data(source) -> Any:
    src_type: str = _get_source_type(source)

    if src_type == 'url':
        return fetch.url_content(source)
    else:
        raise ValueError(f'{src_type} not recognised')


def _get_metadata_generic(content, **kwargs) -> tuple[str, str, str]:
    return '', '', ''


def _get_metadata(content: Any, plugins: dict | None = None, **kwargs) -> dict[str, str]:
    if not plugins or not plugins.get('meta'):
        title, publication, date = _get_metadata_generic(content, **kwargs)
    else:
        _get_meta = plugins.get('meta')[0]
        title, publication, date = _get_meta(content, **kwargs)

    return {
        'title': title,
        'publication': publication,
        'date': date
    }


def _get_data(source, **kwargs) -> PipelineData:
    source = _do_get_data(source)
    content = _modify_source(source, **kwargs)
    body: Any = _get_body_generic(content, **kwargs)
    document: RichTextDocument = _adaptor(body, **kwargs)
    metadata: dict[str, str] = _get_metadata(content, **kwargs)

    return {
        'document': document,
        'source': source,
        'metadata': metadata
    }


def _get_normalisation(**kwargs) -> list[Callable[[RichTextDocument], None]]:
    return normalisation_pipeline(**kwargs)


def _get_sender(output: str = 'docs', **kwargs) -> Callable[[...], None]:
    output = helper.destination(output)

    if output == 'docs':
        return to_docs
    elif output == 'docx':
        return to_docx
    elif output == 'wordpress':
        return to_wordpress
    elif output == 'txt':
        return to_txt

    raise ValueError(f'{output} not recognised')


def _adaptor(content: Any, plugins: dict or None = None, **kwargs) -> RichTextDocument:
    if isinstance(content, Tag):
        doc = RichTextDocument.from_html(content)
    else:
        raise TypeError(f'{content} unhandled')

    adaptor_plugins: list[Callable[[RichText], None]] = plugins.get('adaptor', []) if plugins else []

    for rt in doc.texts:
        for f in adaptor_plugins:
            f(rt)

    return doc


def _run_pipeline(data: PipelineData, normalise: list[Callable[[RichTextDocument], None]]) -> None:
    document: RichTextDocument = data['document']

    for func in normalise:
        func(document)


def pipeline(source, **kwargs) -> None:
    """
    WIP

    Simple way to chain together all the operations required to send to the output

    :param source: url
    :return: None
    """

    sender: Callable[[...], None] = _get_sender(**kwargs)
    normalise: list[Callable[[RichTextDocument], None]] = _get_normalisation(**kwargs)
    data: PipelineData = _get_data(source, **kwargs)

    _run_pipeline(data, normalise)

    sender(**data)
