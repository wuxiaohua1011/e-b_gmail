import pickle
import os.path
from googleapiclient.discovery import build, Resource
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from utility import *
from models import *

SCOPES = ["https://mail.google.com/"]#'https://www.googleapis.com/auth/gmail.readonly', "https://www.googleapis.com/auth/gmail.send"]


def main():
    gmail = Gmail(scope=SCOPES)
    # emails = gmail.get_emails(maxResults=1)
    # gmail.prettyPrintEmails(emails=emails)
    message = gmail.create_message(to="wuxiaohua1011@berkeley.edu",
                                   subject="TEST EMAIL",
                                   message_text="test_email")
    print(message)
    return_message = gmail.send_message(message)
    print("return_message = ", return_message)


if __name__ == '__main__':
    main()
