import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
from .build import build_html_from_document
import json
from string import punctuation
from generic import RichTextDocument


def send_post_to_wordpress(url: str, data: dict, auth: HTTPBasicAuth) -> int:
    response = requests.post(url, json=data, auth=auth)
    return response.status_code


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


def to_wordpress(document: RichTextDocument, title: str = '', **kwargs) -> None:
    url: str = get_endpoint()
    content: BeautifulSoup = build_html_from_document(document)
    slug: str = generate_slug(title)
    data: dict = generate_rest_api_data(title, slug, str(content))
    auth: HTTPBasicAuth = get_auth_data()

    with open('file.txt', 'w') as f:
        json.dump(data, f, indent=4)

    # status_code = send_post_to_wordpress(url, data, auth)
    # print(f'{"Success" if status_code == 201 else "Failure"}')
