import os
import pickle
import re

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dataclasses import dataclass
from typing import Any
from generic import RichText, RichTextDocument


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


def text_to_insert_request(text: str) -> dict:
    return {
        'insertText': {
            'location': {
                'index': 1
            },
            'text': text
        }
    }


def rt_to_style_request(rt: RichText, offset: int, requests: list[dict]) -> None:
    style_map: dict[str, dict] = {
        'italic': {'italic': True},
        'bold': {'bold': True}
    }

    for key, value in style_map.items():
        start, end = RichText.get_anchor_chars(key)
        pattern = re.compile(f'{re.escape(start)}(.*?){re.escape(end)}')

        while match := pattern.search(rt.text):
            sub: str = match.group(1)
            print(sub)

        # start = style.start + offset + 1
        # end = style.end + offset + 1

            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': start,
                        'endIndex': end
                    },
                    'textStyle': value,
                    'fields': key
                },
            })


def rt_to_paragraph_request(rt: RichText, offset: int, requests: list[dict]) -> None:
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
        'align-right': {'alignment': 'END'}
    }

    styles = rt.paragraph_styles

    for style in styles:
        rule: dict = para_map.get(style)

        if not rule:
            raise ValueError(f'{style} not recognised')

        start = offset + 1
        end = offset + len(rt.text) + 1

        requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': start,
                    'endIndex': end
                },
                'paragraphStyle': rule,
                'fields': ','.join([k for k in rule.keys()])
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


def build_requests(document: RichTextDocument) -> list[dict]:
    offset: int = 1
    text: str = ''
    style_requests: list[dict] = []
    paragraph_requests: list[dict] = []

    for rt in document.texts:
        if not rt.text:
            raise ValueError('RichText cannot be empty')

        rt_to_style_request(rt, offset, style_requests)
        rt_to_paragraph_request(rt, offset, paragraph_requests)

        text += '\n' + rt.text if text else rt.text
        offset = len(text) + 1

    text_request: dict = text_to_insert_request(text)
    setup_styles: list[dict] = build_setup_styles(offset)

    return [text_request] + setup_styles + style_requests + paragraph_requests


def to_docs(document: RichTextDocument, title: str = '', **kwargs) -> None:
    requests: list[dict] = build_requests(document)

    # document: Document = create_document(title)
    # send_requests_to_document(document, requests)
