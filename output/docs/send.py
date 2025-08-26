import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dataclasses import dataclass
from typing import Any
from richtext import RichTextDocument
from docrun import adapt_from_rich_text, DocRun
from google.auth.exceptions import RefreshError


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
            try:
                creds.refresh(Request())
            except RefreshError:
                creds = None  # force re-auth

    if not creds:
        client_secrets_file = 'google.json'
        scopes = ['https://www.googleapis.com/auth/documents']
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
        creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('docs', 'v1', credentials=creds)
    document_id = service.documents().create(body={'title': title}).execute().get('documentId')

    return Document(service, document_id)


def send_requests_to_document(document: Document, requests: list[dict]) -> None:
    document.service.documents().batchUpdate(documentId=document.id, body={'requests': requests}).execute()


def text_to_insert_request(text: str) -> list[dict]:
    return [{
        'insertText': {
            'location': {
                'index': 1
            },
            'text': text
        }
    }]


def run_to_style_request(text_styles: set[str], start: int, end: int, requests: list[dict]) -> None:
    style_map: dict = {
        'italic': True,
        'bold': True
    }

    text_styles: dict = {k: v for k, v in style_map.items() if k in text_styles}

    if text_styles:
        requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': start,
                    'endIndex': end
                },
                'textStyle': text_styles,
                'fields': ','.join(text_styles.keys())
            },
        })


def run_to_paragraph_request(paragraph_styles: set[str], start: int, end: int, requests: list[dict]) -> None:
    para_map: dict[str, dict] = {
        'heading1': {'namedStyleType': 'HEADING_1'},
        'heading2': {'namedStyleType': 'HEADING_2'},
        'heading3': {'namedStyleType': 'HEADING_3'},
        'heading4': {'namedStyleType': 'HEADING_4'},
        'heading5': {'namedStyleType': 'HEADING_5'},
        'heading6': {'namedStyleType': 'HEADING_6'},
        'blockquote': {
            'indentStart': {'magnitude': 36, 'unit': 'PT'},
            'indentFirstLine': {'magnitude': 36, 'unit': 'PT'}
        },
        'align-right': {'alignment': 'END'},
        'align-centre': {'alignment': 'CENTER'}
    }

    paragraph_styles: dict = {
        ik: iv for ok, inner in para_map.items() if ok in paragraph_styles for ik, iv in inner.items()
    }

    if paragraph_styles:
        requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': start,
                    'endIndex': end
                },
                'paragraphStyle': paragraph_styles,
                'fields': ','.join([k for k in paragraph_styles.keys()])
            }
        })


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


def flatten_paragraph_requests(paragraph_requests: list[dict]) -> list[dict]:
    def styles_are_equal(a: dict, b: dict) -> bool:
        return a['updateParagraphStyle']['paragraphStyle'] == b['updateParagraphStyle']['paragraphStyle']

    def paragraphs_are_adjacent(a: dict, b: dict) -> bool:
        return a['updateParagraphStyle']['range']['endIndex'] == b['updateParagraphStyle']['range']['startIndex'] - 1

    def merge_indices(a: dict, b: dict) -> None:
        a['updateParagraphStyle']['range']['endIndex'] = b['updateParagraphStyle']['range']['endIndex']

    i: int = 0

    while i < len(paragraph_requests) - 1:
        req1: dict = paragraph_requests[i]
        req2: dict = paragraph_requests[i + 1]

        if styles_are_equal(req1, req2) and paragraphs_are_adjacent(req1, req2):
            merge_indices(req1, req2)
            paragraph_requests.pop(i + 1)
        else:
            i += 1

    return paragraph_requests


def build_requests(runs: list[DocRun]) -> list[dict]:
    google_reserved_index_offset: int = 1
    offset: int = google_reserved_index_offset + 0
    combined_text: str = ''
    style_requests: list[dict] = []
    paragraph_requests: list[dict] = []

    for run in runs:
        text: str = run.text

        if not text:
            raise ValueError('Run cannot be empty')

        length: int = len(text)
        start: int = offset
        end: int = offset + length

        run_to_style_request(run.text_styles, start, end, style_requests)
        run_to_paragraph_request(run.paragraph_styles, start, end, paragraph_requests)

        combined_text += text
        offset = google_reserved_index_offset + len(combined_text)

    text_request: list[dict] = text_to_insert_request(combined_text)
    setup_styles: list[dict] = build_setup_styles(offset)

    paragraph_requests = flatten_paragraph_requests(paragraph_requests)

    return text_request + setup_styles + style_requests + paragraph_requests


def to_docs(document: RichTextDocument, metadata: dict | None = None, **kwargs) -> None:
    title: str = metadata['title']
    publication: str = metadata['publication']
    date: str = metadata['date']

    runs: list[DocRun] = adapt_from_rich_text(document, add_newline=True)
    requests: list[dict] = build_requests(runs)

    document: Document = create_document(title)
    send_requests_to_document(document, requests)
