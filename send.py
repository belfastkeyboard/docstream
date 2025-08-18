from __future__ import print_function
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/documents']


def send_to_docs(text: str) -> None:
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
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the creds for next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Build the service
    service = build('docs', 'v1', credentials=creds)

    # Create a new blank doc
    doc = service.documents().create(body={'title': 'My First Doc'}).execute()
    document_id = doc.get('documentId')
    print(f'Created document with ID: {document_id}')

    # Insert text into the doc
    requests = [
        {
            'insertText': {
                'location': {'index': 1},
                'text': 'Hello from Python! 🚀\n'
            }
        }
    ]
    service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    print("Text inserted.")
