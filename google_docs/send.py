import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dataclasses import dataclass
from typing import Any
from .type import DocNode
from bs4 import Tag
import soup


@dataclass
class Document:
    service: Any
    id: str


def create_document(title: str) -> Document:
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
                'google.json', ['https://www.googleapis.com/auth/documents'])
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('docs', 'v1', credentials=creds)
    document_id = service.documents().create(body={'title': title}).execute().get('documentId')

    return Document(service, document_id)


def send_requests_to_document(document: Document, requests: list[dict]) -> None:
    document.service.documents().batchUpdate(documentId=document.id, body={'requests': requests}).execute()


def nodes_to_text_request(nodes: list[DocNode]) -> dict:
    text: str = ''.join([node.text for node in nodes])

    return {
        'insertText': {
            'location': {
                'index': 1
            },
            'text': text
        }
    }


def node_to_style_request(node: DocNode, start: int, end: int) -> dict:
    style_map: dict[str, dict] = {
        'italic': {'italic': True},
        'bold': {'bold': True}
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


def node_to_paragraph_request(node: DocNode, start: int, end: int) -> dict:
    para_map: dict[str, dict] = {
        'HEADING_1': {'namedStyleType': 'HEADING_1'},
        'HEADING_2': {'namedStyleType': 'HEADING_2'},
        'HEADING_3': {'namedStyleType': 'HEADING_3'},
        'HEADING_4': {'namedStyleType': 'HEADING_4'},
        'HEADING_5': {'namedStyleType': 'HEADING_5'},
        'HEADING_6': {'namedStyleType': 'HEADING_6'},
        'blockquote': {
            'indentStart': {'magnitude': 36, 'unit': 'PT'},
            'indentFirstLine': {'magnitude': 36, 'unit': 'PT'}
        },
        'align-right': {'alignment': 'END'}
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


def build_setup_styles(end: int) -> list[dict]:
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


def build_requests(nodes: list[DocNode]) -> list[dict]:
    start = 1
    end = start

    style_requests: list[dict] = []
    paragraph_requests: list[dict] = []

    for node in nodes:
        if not node.text:
            continue

        end = start + len(node.text)

        style_request: dict = node_to_style_request(node, start, end)
        paragraph_request: dict = node_to_paragraph_request(node, start, end)

        start = end

        if style_request:
            style_requests.append(style_request)

        if paragraph_request:
            paragraph_requests.append(paragraph_request)

    text_request: dict = nodes_to_text_request(nodes)
    setup_styles: list[dict] = build_setup_styles(end)

    return [text_request] + setup_styles + style_requests + paragraph_requests


def to_docs(content: Tag, title: str = '', **kwargs) -> None:
    nodes: list[DocNode] = soup.nodes(content)
    requests: list[dict] = build_requests(nodes)
    document: Document = create_document(title)

    with open('file.txt', 'w') as f:
        for node in nodes:
            f.write(node.text)

    # send_requests_to_document(document, requests)
