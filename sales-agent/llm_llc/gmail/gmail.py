import base64
from email.message import EmailMessage
import os
from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define the scopes needed for the Gmail API
SCOPES = [
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]


def get_credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def process_unread_emails():
    creds = get_credentials()
    global gmail_service
    gmail_service = build("gmail", "v1", credentials=creds)

    # Get a list of unread emails
    results = (
        gmail_service.users().messages().list(userId="me", q="is:unread").execute()
    )
    messages = results.get("messages", [])

    if not messages:
        print("No unread emails found.")
        return

    print(f"Number of unread emails: {len(messages)}")
    msgs = []
    for msg in messages:
        # Get the message from its id
        txt = gmail_service.users().messages().get(userId="me", id=msg["id"]).execute()
        # Use try-except to avoid any Errors
        try:
            # Get value of 'payload' from dictionary 'txt'
            payload = txt["payload"]
            headers = payload["headers"]

            # Look for Subject and Sender Email in the headers
            for d in headers:
                if d["name"] == "Subject":
                    subject = d["value"]
                if d["name"] == "From":
                    sender = d["value"]

            # The Body of the message is in Encrypted format. So, we have to decode it.
            # Get the data and decode it with base 64 decoder.
            parts = payload.get("parts")[0]
            data = parts["body"]["data"]
            data = data.replace("-", "+").replace("_", "/")
            decoded_data = base64.b64decode(data)

            # Now, the data obtained is in lxml. So, we will parse
            # it with BeautifulSoup library
            soup = BeautifulSoup(decoded_data, "lxml")
            body = soup.body()

            msgs.append(
                {"sender": sender, "subject": subject, "body": body, "msg": msg}
            )
        except Exception as e:
            print(e)
            pass
        return msgs


def mark_email_as_read(email_id):
    gmail_service.users().messages().modify(
        userId="me", id=email_id, body={"removeLabelIds": ["UNREAD"]}
    ).execute()


def reply(reply_message, original_email_id):
    try:
        original_email = (
            gmail_service.users()
            .messages()
            .get(userId="me", id=original_email_id)
            .execute()
        )
    except HttpError as error:
        print(f"An error occurred while fetching the original email: {error}")
        original_email = None

    if original_email:
        headers = original_email["payload"]["headers"]

        subject = [i["value"] for i in headers if i["name"] == "Subject"][0]
        to = [i["value"] for i in headers if i["name"] == "Delivered-To"][0]
        sender = [i["value"] for i in headers if i["name"] == "From"][0]
        message_id = [i["value"] for i in headers if i["name"] == "Message-ID"][0]

        gmail_reply_message = {
            "raw": base64.urlsafe_b64encode(
                f"From: {to}\n"
                f"To: {sender}\n"
                f"Subject: Re: {subject}\n"
                f"References: {message_id}\n"
                f"In-Reply-To: {message_id}\n\n"
                f"{reply_message}\n".encode("utf-8")
            ).decode("utf-8")
        }

        try:
            reply = (
                gmail_service.users()
                .messages()
                .send(userId="me", body=gmail_reply_message)
                .execute()
            )
            print(f'Reply sent! Message Id: {reply["id"]}')
        except HttpError as error:
            print(f"An error occurred: {error}")


def add_label_to_email(thread_id, label_name):
    thread = gmail_service.users().threads().get(userId="me", id=thread_id).execute()
    existing_labels = thread.get("labels", [])

    label_id = None
    for label in existing_labels:
        if label["name"] == label_name:
            label_id = label["id"]
            break

    if label_id:
        gmail_service.users().threads().modify(
            userId="me", id=thread_id, body={"addLabelIds": [label_id]}
        ).execute()


def get_label_id(label_name):
    labels = gmail_service.users().labels().list(userId="me").execute()
    label_list = labels.get("labels", [])

    for label in label_list:
        if label["name"] == label_name:
            return label["id"]

    return None
