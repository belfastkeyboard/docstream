import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup, Tag
import json
from string import punctuation
from .type import WPNode


def send_post_to_wordpress(url: str, data: dict, auth: HTTPBasicAuth) -> int:
    response = requests.post(url, json=data, auth=auth)
    return response.status_code


def stringify_content(nodes: list[WPNode]) -> str:
    return '\n\n'.join([str(node) for node in nodes])


def get_endpoint() -> str:
    with open('wordpress.json', 'r') as f:
        data = json.load(f)

    return data['endpoint']


def generate_slug(title: str) -> str:
    table = str.maketrans(
        'áéíóúḃċḋḟġṁṗṡṫ',
        'aeioubcdfgmpst',
        punctuation
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


def get_auth_data() -> HTTPBasicAuth:
    with open('wordpress.json', 'r') as f:
        credentials = json.load(f)

    name: str = credentials['name']
    pw: str = credentials['password'].replace(' ', '')

    return HTTPBasicAuth(name, pw)


def generate_nodes_from_tree(tree: Tag) -> list[WPNode]:
    return [WPNode(tag) for tag in tree.contents]


def to_wordpress(title: str, tree: BeautifulSoup) -> None:
    url: str = get_endpoint()
    nodes: list[WPNode] = generate_nodes_from_tree(tree)
    content: str = stringify_content(nodes)
    slug: str = generate_slug(title)
    data: dict = generate_rest_api_data(title, slug, content)
    auth: HTTPBasicAuth = get_auth_data()

    with open("file.txt", "w") as f:
        f.write(content)

    status_code = send_post_to_wordpress(url, data, auth)
    print(f'{"Success" if status_code == 201 else "Failure"}')
