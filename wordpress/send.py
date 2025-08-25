import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
from .build import build_html_from_document
import json
from string import punctuation
from generic import RichTextDocument


def send_post_to_wordpress(url: str, author: int, data: dict, auth: HTTPBasicAuth) -> int:
    response = requests.post(url, json=data, auth=auth)
    return response.status_code


def get_endpoint() -> str:
    with open('wordpress.json', 'r') as f:
        data = json.load(f)

    return data['endpoint']


def get_author() -> int:
    with open('wordpress.json', 'r') as f:
        data = json.load(f)

    return data['author']


def generate_slug(title: str) -> str:
    table = str.maketrans(
        'áéíóúḃċḋḟġṁṗṡṫ',
        'aeioubcdfgmpst',
        punctuation
    )

    clean: str = title.translate(table)

    return '-'.join(clean.split(' ')).lower()


def generate_rest_api_data(title: str, slug: str, content: BeautifulSoup) -> dict:
    text: str = content.text
    index = min(len(text), 180)

    return {
        'title': title,
        'slug': slug,
        'content': str(content),
        'status': 'draft',
        'excerpt': f'{content.text[:index]}...',
        'author': 6
    }


def get_auth_data() -> HTTPBasicAuth:
    with open('wordpress.json', 'r') as f:
        credentials = json.load(f)

    name: str = credentials['name']
    pw: str = credentials['password'].replace(' ', '')

    return HTTPBasicAuth(name, pw)


def to_wordpress(document: RichTextDocument, metadata: dict | None = None, **kwargs) -> None:
    title: str = metadata['title']
    publication: str = metadata['publication']
    date: str = metadata['date']

    url: str = get_endpoint()
    author: int = get_author()
    content: BeautifulSoup = build_html_from_document(document)
    slug: str = generate_slug(title)
    data: dict = generate_rest_api_data(title, slug, content)
    auth: HTTPBasicAuth = get_auth_data()

    with open('file.txt', 'w') as f:
        json.dump(data, f, indent=4)

    status_code = send_post_to_wordpress(url, author, data, auth)
    print(f'{"Success" if status_code == 201 else "Failure"}')
