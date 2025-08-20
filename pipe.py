import fetch
import soup
from yarl import URL
from typing import Any, Callable
from bs4 import BeautifulSoup
from transform import marxists_html
import helper
from google_docs import docs_normalisation, to_docs, make_style_docs_compliant
from wordpress import wp_normalisation, to_wordpress, make_style_wordpress_compliant


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


def _get_url_content(source: str) -> Any:
    return fetch.url_content(source)


def _getter_from_type(get_type: str) -> Callable:
    if get_type == 'url':
        return _get_url_content

    raise LookupError(f'could not find getter for {get_type} type')


def _get_title_generic(content) -> str:
    if isinstance(content, BeautifulSoup):
        return soup.title(content)
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


def _transform_content(content, transform: str = '', **kwargs) -> Any:
    if helper.source(transform) == 'marxists':
        marxists_html(content)

    return content


def _get_content(source, **kwargs) -> tuple[str, Any]:
    source_type: str = _get_source_type(source)
    getter: Callable = _getter_from_type(source_type)

    content = getter(source)
    content = _transform_content(content, **kwargs)

    title: str = _get_title_generic(content)
    content: Any = _get_body_generic(content, **kwargs)

    return title, content


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


def _get_style(output: str = 'docs', **kwargs) -> Callable or None:
    output = helper.destination(output)

    if output == 'docs':
        return make_style_docs_compliant
    elif output == 'wordpress':
        return make_style_wordpress_compliant

    raise ValueError(f'{output} not recognised')


def _run_normalisation_pipeline(content: Any, normalise: list[Callable]) -> None:
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
    title, content = _get_content(source, **kwargs)
    stylise: Callable = _get_style(**kwargs)

    _run_normalisation_pipeline(content, normalise)

    stylise(content, **kwargs)
    sender(title, content)
