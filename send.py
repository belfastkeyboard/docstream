from __future__ import print_function
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4.element import PageElement
from bs4 import Tag
from dataclasses import dataclass
from typing import Any


class DocNode:
    def __init__(self, styles: set[str], text: str):
        self.text = text
        self.styles = styles

    def __str__(self):
        return f'DocNode({self.styles}, {self.text})'

    @classmethod
    def from_html(cls, element: PageElement, styles: set[str]):
        text: str = element.text if isinstance(element, Tag) else str(element)

        return cls(styles, text)


@dataclass
class Document:
    service: Any
    id: str


def _create_document(title: str) -> Document:
    creds = None

    # token.pickle stores your access/refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid creds, do login flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', ['https://www.googleapis.com/auth/documents'])
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('docs', 'v1', credentials=creds)
    document_id = service.documents().create(body={'title': title}).execute().get('documentId')

    return Document(service, document_id)


def _send_requests_to_document(document: Document, requests: list[dict]) -> None:
    document.service.documents().batchUpdate(documentId=document.id, body={'requests': requests}).execute()


def _tag_to_text_request(node: DocNode, start: int) -> dict:
    return {
        'insertText': {
            'location': {
                'index': start
            },
            'text': node.text
        }
    }


def _tag_to_style_request(node: DocNode, start: int, end: int) -> dict:
    style_map: dict[str, dict] = {
        'em': {'italic': True},
        'i': {'italic': True},
        'strong': {'bold': True},
        'b': {'bold': True}
    }

    styles = set(node.styles)
    rules = {}

    for style in styles:
        if style in style_map:
            rules.update(style_map[style])

    if not rules:
        return {}
    else:
        return {
            'updateTextStyle': {
                'range': {
                    'startIndex': start,
                    'endIndex': end
                },
                'textStyle': rules,
                'fields': ','.join([k for k in rules.keys()])
            },
        }


def _tag_to_paragraph_request(node: DocNode, start: int, end: int) -> dict:
    para_map: dict[str, dict] = {
        'h1': {'namedStyleType': 'HEADING_1'},
        'h2': {'namedStyleType': 'HEADING_2'},
        'h3': {'namedStyleType': 'HEADING_3'},
        'h4': {'namedStyleType': 'HEADING_4'},
        'h5': {'namedStyleType': 'HEADING_5'},
        'h6': {'namedStyleType': 'HEADING_6'},
        'blockquote': {
            'indentStart': {'magnitude': 36, 'unit': 'PT'},
            'indentFirstLine': {'magnitude': 36, 'unit': 'PT'}
        }
    }

    styles = set(node.styles)
    rules = {}

    for style in styles:
        if style in para_map:
            rules.update(para_map[style])

    if not rules:
        return {}
    else:
        return {
            'updateParagraphStyle': {
                'range': {
                    'startIndex': start,
                    'endIndex': end
                },
                'paragraphStyle': rules,
                'fields': ','.join([k for k in rules.keys()])
            }
        }


def _build_setup_styles(end: int) -> list[dict]:
    para_style: dict = {
        'namedStyleType': 'NORMAL_TEXT',
        'alignment': 'JUSTIFIED',
        'lineSpacing': 115,
        'spaceBelow': {'magnitude': 12, 'unit': 'PT'}
    }

    text_style: dict = {
        'fontSize': {'magnitude': 12, 'unit': 'PT'}
    }

    para: dict = {
        'updateParagraphStyle': {
            'range': {
                'startIndex': 1,
                'endIndex': end
            },
            'paragraphStyle': para_style,
            'fields': ','.join(para_style.keys())
        }
    }

    text: dict = {
        'updateTextStyle': {
            'range': {
                'startIndex': 1,
                'endIndex': end
            },
            'textStyle': text_style,
            'fields': ','.join(text_style.keys())
        }
    }

    return [para, text]


def _build_requests(nodes: list[DocNode]) -> list[dict]:
    start = 1
    end = start

    text_requests: list[dict] = []
    style_requests: list[dict] = []
    paragraph_requests: list[dict] = []

    for node in nodes:
        if not node.text:
            continue

        end = start + len(node.text)

        text_request: dict = _tag_to_text_request(node, start)
        style_request: dict = _tag_to_style_request(node, start, end)
        paragraph_request: dict = _tag_to_paragraph_request(node, start, end)

        start = end

        text_requests.append(text_request)

        if style_request:
            style_requests.append(style_request)

        if paragraph_request:
            paragraph_requests.append(paragraph_request)

    setup_styles: list[dict] = _build_setup_styles(end)

    return text_requests + setup_styles + style_requests + paragraph_requests


def to_docs(title: str, nodes: list[DocNode]) -> None:
    document: Document = _create_document(title)
    requests: list[dict] = _build_requests(nodes)
    _send_requests_to_document(document, requests)
