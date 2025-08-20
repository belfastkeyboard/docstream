import requests
from bs4 import BeautifulSoup, Tag
from bs4.element import PageElement


def send_post_to_wordpress(url: str, data: dict, auth: tuple[str, str]) -> None:
    requests.post(url, json=data, auth=auth)


def stringify_content(tree: BeautifulSoup) -> str:
    stringified_content: str = ''

    for child in tree.children:
        if isinstance(child, Tag):
            stringified_content += child.prettify()  # remove pretty printing
        elif isinstance(child, PageElement):
            stringified_content += str(child)

    return stringified_content


def get_endpoint() -> str:
    return 'https://cartlann.org/wp-json/wp/v2/pages'


def generate_slug(title: str) -> str:
    table = str.maketrans(
        'áéíóúḃċḋḟġṁṗṡṫ',
        'aeioubcdfgmpst'
    )

    clean: str = title.translate(table)

    return '-'.join(clean.split(' ')).lower()


def generate_rest_api_data(title: str, slug: str, content: str) -> dict:
    return {
        'title': title,
        'slug': slug,
        'content': content,
        'status': 'draft'
    }


def to_wordpress(title: str, tree: BeautifulSoup) -> None:
    url: str = get_endpoint()
    content: str = stringify_content(tree)
    slug: str = generate_slug(title)
    data: dict = generate_rest_api_data(title, slug, content)

    # send_post_to_wordpress(url, data, )

    with open('new.txt', 'w') as f:
        f.write(content)
