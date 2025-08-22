import fetch
import soup
from yarl import URL
from typing import Any, Callable
from bs4 import BeautifulSoup
from transform import marxists_html, marxists_title, marxists_publication, marxists_date
import helper
from google_docs import docs_normalisation, to_docs
from wordpress import wp_normalisation, to_wordpress


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


def _get_body_generic(content, output: str = 'docs', **kwargs) -> Any:
    output = helper.destination(output)
    is_soup: bool = isinstance(content, BeautifulSoup)

    if is_soup and output == 'docs':
        return soup.nodes(content, **kwargs)
    elif is_soup and output == 'wordpress':
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


def _get_normalisation(output: str = 'docs', **kwargs) -> list[Callable]:
    output = helper.destination(output)

    if output == 'docs':
        return docs_normalisation()
    elif output == 'wordpress':
        return wp_normalisation(**kwargs)

    raise ValueError(f'{output} not recognised')


def _get_sender(output: str = 'docs', **kwargs) -> Callable[[str, Any], None]:
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

    _run_pipeline(content, normalise)

    sender(**data)
