# this code is originated from:
# https://developers.google.com/gmail/api/quickstart/python?authuser=1

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os
from apiclient import errors
import json

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://mail.google.com/']

def connect():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

def build_message(to, sender, subject, message_text):
    message = MIMEText(message_text.encode("utf-8"))
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_string())}

def do_send(service, message):
    try:
        message = (service.users().messages().send(userId='me', body=message)
                .execute())
        print ('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print ('An error occurred: %s' % error)

def send_messages(subject, message_text):
    to_list_file = open("to_list.json", "r")
    to_list = json.load(to_list_file)
    service = connect()
    for to in to_list:
        message = build_message(to, "roghnin@gmail.com", subject, message_text)
        do_send(service, message)
    to_list_file.close()

if __name__ == '__main__':
    # test out connection.
    labels = connect().users().labels().list(userId='me').execute().get('labels', [])
    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])