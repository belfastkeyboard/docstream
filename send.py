from __future__ import print_function
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class DocNode:
    def __init__(self, styles: list[str], text: str = ''):
        self.text = text
        self.styles = styles

    def __str__(self):
        return f'DocNode({self.styles}, {self.text})'


class Docs:
    def __init__(self, title: str):
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

        self.service = build('docs', 'v1', credentials=creds)
        self.doc = self.service.documents().create(body={'title': title}).execute()
        self.document_id = self.doc.get('documentId')

        self.text: list[dict] = []
        self.style: list[dict] = []
        self.para: list[dict] = []
        self.setup: list[dict] = []

        self.start: int = 1
        self.end: int = 1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.setup_styles()

        texts: list[dict] = self.text
        setup: list[dict] = self.setup
        style: list[dict] = self.style
        para: list[dict] = self.para

        # the batched list must be delivered in this order to comply with Google's API
        # 1. insert all text [texts]
        # 2. apply document-scope styles [setup]
        # 3. apply ranged-scope styles [style, para]
        batched = texts + setup + style + para

        # self.service.documents().batchUpdate(documentId=self.document_id, body={'requests': batched}).execute()

        self.service.documents().batchUpdate(documentId=self.document_id, body={'requests': texts}).execute()
        self.service.documents().batchUpdate(documentId=self.document_id, body={'requests': setup}).execute()
        self.service.documents().batchUpdate(documentId=self.document_id, body={'requests': style}).execute()
        self.service.documents().batchUpdate(documentId=self.document_id, body={'requests': para}).execute()

    def setup_styles(self) -> None:
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
                    'endIndex': self.end
                },
                'paragraphStyle': para_style,
                'fields': ','.join(para_style.keys())
            }
        }

        text: dict = {
            'updateTextStyle': {
                'range': {
                    'startIndex': 1,
                    'endIndex': self.end
                },
                'textStyle': text_style,
                'fields': ','.join(text_style.keys())
            }
        }

        self.setup = [para, text]

    def tag_to_text(self, node: DocNode) -> None:
        start: int = self.end
        end: int = start + len(node.text)

        data: dict = {
            'insertText': {
                'location': {
                    'index': start
                },
                'text': node.text
            }
        }

        self.text.append(data)

        self.start = start
        self.end = end

    def tag_to_style(self, node: DocNode) -> None:
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
            return

        data: dict = {
            'updateTextStyle': {
                'range': {
                    'startIndex': self.start,
                    'endIndex': self.end
                },
                'textStyle': rules,
                'fields': ','.join([k for k in rules.keys()])
            },
        }

        self.style.append(data)

    def tag_to_paragraph(self, node: DocNode) -> None:
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
            return

        data: dict = {
            'updateParagraphStyle': {
                'range': {
                    'startIndex': self.start,
                    'endIndex': self.end
                },
                'paragraphStyle': rules,
                'fields': ','.join([k for k in rules.keys()])
            }
        }

        self.para.append(data)


class Dummy(Docs):
    def __init__(self, title: str):
        self.title = title
        self.text: list[dict] = []
        self.style: list[dict] = []
        self.para: list[dict] = []
        self.setup: list[dict] = []

        self.start: int = 1
        self.end: int = 1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.setup_styles()

        texts: list[dict] = self.text
        setup: list[dict] = self.setup
        style: list[dict] = self.style
        para: list[dict] = self.para

        # the batched list must be delivered in this order to comply with Google's API
        # 1. insert all text [texts]
        # 2. apply document-scope styles [setup]
        # 3. apply ranged-scope styles [style, para]
        batched = texts + setup + style + para


def send_to_docs(tags: list[DocNode]) -> None:
    with Docs('Docs Test') as doc:
        for tag in tags:
            if not tag.text:
                continue

            doc.tag_to_text(tag)
            doc.tag_to_style(tag)
            doc.tag_to_paragraph(tag)

    print()

    # requests = [d for d in requests if d]

    # for request in requests:
    #     print(request)
