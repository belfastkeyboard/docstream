import fetch
import soup
from yarl import URL
from typing import Any, Callable
from bs4 import BeautifulSoup, Tag
from transform import marxists_html, marxists_title, marxists_publication, marxists_date
import helper
from google_docs import to_docs
from wordpress import to_wordpress
from normalise import normalisation_pipeline
from generic import StructuredText


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


def _get_soup_title(content, transform: str = '', **kwargs) -> str:
    transform = helper.source(transform)

    if transform == 'marxists':
        return marxists_title(content)

    return soup.title(content)


def _get_title_generic(content, **kwargs) -> str:
    if isinstance(content, BeautifulSoup):
        return _get_soup_title(content, **kwargs)
    else:
        raise TypeError(f'Unhandled type: {type(content)}')


def _get_body_generic(content, **kwargs) -> Any:
    if isinstance(content, BeautifulSoup):
        return soup.tree(content, **kwargs)

    raise TypeError(f'Unhandled type: {type(content)}')


def _transform_data(content, transform: str = '', **kwargs) -> Any:
    if helper.source(transform) == 'marxists':
        marxists_html(content)

    return content


def _do_get_data(source) -> Any:
    src_type: str = _get_source_type(source)

    if src_type == 'url':
        return fetch.url_content(source)
    else:
        raise ValueError(f'{src_type} not recognised')


def _get_publication_generic(content, transform: str = '', **kwargs) -> str:
    transform = helper.source(transform)

    if transform == 'marxists':
        return marxists_publication(content)
    else:
        raise ValueError(f'{transform} not recognised')


def _get_date_generic(content, transform: str = '', **kwargs) -> str:
    transform = helper.source(transform)

    if transform == 'marxists':
        return marxists_date(content)
    else:
        raise ValueError(f'{transform} not recognised')


def _get_data(source, **kwargs) -> dict:
    content = _do_get_data(source)
    content = _transform_data(content, **kwargs)

    title: str = _get_title_generic(content)
    content: Any = _get_body_generic(content, **kwargs)
    publication: str = _get_publication_generic(content, **kwargs)
    date: str = _get_date_generic(content, **kwargs)

    return {
        'title': title,
        'content': content,
        'publication': publication,
        'date': date
    }


def _get_normalisation(**kwargs) -> list[Callable]:
    return normalisation_pipeline(**kwargs)


def _get_sender(output: str = 'docs', **kwargs) -> Callable:
    output = helper.destination(output)

    if output == 'docs':
        return to_docs
    elif output == 'wordpress':
        return to_wordpress

    raise ValueError(f'{output} not recognised')


def _run_pipeline(content: Any, normalise: list[Callable]) -> None:
    for func in normalise:
        content = func(content)


def pipeline(source, **kwargs) -> None:
    """
    WIP

    Simple way to chain together all the operations required to send to Google Docs

    :param source: url
    :return: None
    """

    sender: Callable[[str, list], None] = _get_sender(**kwargs)
    normalise: list[Callable] = _get_normalisation(**kwargs)
    data: dict = _get_data(source, **kwargs)
    content: Any = data.get('content', None)

    lol = []
    for x in content:
        lol.append(StructuredText.from_html(x))

    assert isinstance(content, Tag)

    _run_pipeline(content, normalise)

    sender(**data)
