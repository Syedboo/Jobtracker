from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os.path
import pickle
from datetime import datetime
import base64
import email

# Define your scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def extract_metadata(msg_data):
    headers = msg_data['payload'].get('headers', [])
    metadata = {
        'from': next((h['value'] for h in headers if h['name'].lower() == 'from'), ''),
        'subject': next((h['value'] for h in headers if h['name'].lower() == 'subject'), ''),
        'date': next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
    }

    # Format date
    try:
        parsed_date = email.utils.parsedate_to_datetime(metadata['date'])
        metadata['date'] = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
    except:
        pass

    return metadata


def main():
    creds = None

    # Load existing token
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid creds, run auth
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=8080)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Gmail search query for employer acknowledgment emails
    query = '"Thank you for submitting your application" OR "Thank you for your application" OR "thank you for your application" OR "Your application was sent to" OR "Thank you for applying" OR "received your application" OR "will review your application" newer_than:30d'
    #query = '"Your application was sent to" newer_than:30d'
    results = service.users().messages().list(userId='me', q=query, maxResults=10).execute()
    messages = results.get('messages', [])

    print("\n--- Employer Acknowledgment Emails ---")
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        metadata = extract_metadata(msg_data)
        print(f"From:    {metadata['from']}")
        print(f"Subject: {metadata['subject']}")
        print(f"Date:    {metadata['date']}")
        print("-" * 40)


if __name__ == '__main__':
    main()
