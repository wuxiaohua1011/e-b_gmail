import pickle
import os.path
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import Resource
from pathlib import Path
from typing import List, Dict
from models import *
import json
from email.mime.text import MIMEText
from urllib3.exceptions import HTTPError


class Gmail(object):
    def __init__(self, credential_file_path: Path = Path("./assets/credentials.json"), scope=None):
        if scope is None:
            scope = ['https://mail.google.com/']
        self.google_service: Resource = build('gmail', 'v1', credentials=self.login(scopes=scope,
                                                                                    cred_file_path=credential_file_path))

    @classmethod
    def login(cls, scopes: List[str], cred_file_path: Path = Path("./assets/credentials.json")):
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        creds = None
        pickle_file_path = cred_file_path.parent / "token.pickle"
        if os.path.exists(pickle_file_path.as_posix()):
            with open(pickle_file_path.as_posix(), 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    cred_file_path.as_posix(), scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(pickle_file_path.as_posix(), 'wb') as token:
                pickle.dump(creds, token)
        return creds

    def get_emails(self,
                   includeSpamTrash: bool = True,
                   labelIds: str = None,
                   maxResults: int = 10,
                   pageToken: str = "",
                   q: str = "from: submissions@formspree.io",
                   format: str = "full",
                   metadataHeaders: str = None) -> List[Email]:
        """
        This is a combined function of the Google Gmail API

        http://googleapis.github.io/google-api-python-client/docs/dyn/gmail_v1.users.messages.html#list
        http://googleapis.github.io/google-api-python-client/docs/dyn/gmail_v1.users.messages.html#get

        Args:
          userId: string, The user's email address. The special value me can be used to indicate the authenticated user. (required)
          includeSpamTrash: boolean, Include messages from SPAM and TRASH in the results.
          labelIds: string, Only return messages with labels that match all of the specified label IDs. (repeated)
          maxResults: integer, Maximum number of messages to return.
          pageToken: string, Page token to retrieve a specific page of results in the list.
          q: string, Only return messages matching the specified query. Supports the same query format as the Gmail search box. For example, "from:someuser@example.com rfc822msgid:<somemsgid@example.com> is:unread". Parameter cannot be used when accessing the api using the gmail.metadata scope.
          format: string, The format to return the message in.
                Allowed values
                  full -
                  metadata -
                  minimal -
                  raw -
          metadataHeaders: string, When given and format is METADATA, only include headers specified. (repeated)
        Returns:

        """
        messages_resource = self.google_service.users().messages()
        formspree_data: Dict[str, list] = messages_resource.list(userId="me",
                                                                 includeSpamTrash=includeSpamTrash,
                                                                 labelIds=labelIds,
                                                                 maxResults=maxResults,
                                                                 pageToken=pageToken,
                                                                 q=q).execute()
        formspree_data: List[EmailMeta] = [EmailMeta.parse_obj(d) for d in formspree_data["messages"]]
        result: List[Email] = []
        for d in formspree_data:
            email = messages_resource.get(userId="me", id=d.id, format=format).execute()
            email: Email = Email.parse_obj(email)
            email.decode_email()
            result.append(email)
            # email.payload.body.data = email.decodeMessage(email.payload.body.data)
            # print(json.dumps(email.payload.dict(), indent=4))
            # print(json.dumps(email.dict(), indent=4))

        return result

    def send_message(self, message):
        """Send an email message.

        Args:
          can be used to indicate the authenticated user.
          message: Message to be sent.

        Returns:
          Sent Message.
        """
        try:
            message = (self.google_service.users().messages().send(userId="wuxiaohua1011@berkeley.edu", body=message).execute())
            print('Message Id: %s' % message['id'])
            return message
        except HTTPError or Exception as e:
            print('An error occurred: %s' % e)

    @classmethod
    def prettyPrintEmails(cls, emails: List[Email]):
        for email in emails:
            print(json.dumps(email.dict(include={"id", "snippet"}), indent=2))

    @classmethod
    def create_message(cls, to, subject, message_text, sender="wuxiaohua1011@berkeley.edu", ):
        """Create a message for an email.

        Args:
          sender: Email address of the sender.
          to: Email address of the receiver.
          subject: The subject of the email message.
          message_text: The text of the email message.

        Returns:
          An object containing a base64url encoded email object.
        """
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
