import fetch
import get
import normalise
import send
from yarl import URL
from typing import Callable
from send import DocNode


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


def _get_url_content(source: str) -> tuple[str, list]:
    content = fetch.url_content(source)

    title: str = get.title(content)
    nodes: list = get.nodes(content)

    return title, nodes


def _getter_from_type(get_type: str) -> Callable:
    if get_type == 'url':
        return _get_url_content

    raise LookupError(f'could not find getter for {get_type} type')


def _get_content(source) -> tuple[str, list]:
    source_type: str = _get_source_type(source)
    getter: Callable = _getter_from_type(source_type)

    return getter(source)


def _get_default_transform() -> list[Callable]:
    return [
        normalise.merge,
        normalise.clean,
        normalise.invert_quotes,
        lambda c: normalise.swap(c, 'strong', 'em'),
        normalise.remove_empty,
        normalise.collapse_newlines
    ]


def _run_pipeline(nodes: list[DocNode], transforms: list[Callable]) -> list[DocNode]:
    for transform in transforms:
        nodes = transform(nodes)

    return nodes


def pipeline(source) -> None:
    """
    WIP

    Simple way to chain together all the operations required to send to Google Docs

    :param source: url
    :return: None
    """

    title, nodes = _get_content(source)
    transform = _get_default_transform()
    nodes = _run_pipeline(nodes, transform)
    send.to_docs(title, nodes)
