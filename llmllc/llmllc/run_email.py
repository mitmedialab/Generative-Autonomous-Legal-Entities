from typing import List
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


class Gmail:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.server = smtplib.SMTP("smtp.gmail.com", 587)
        self.server.starttls()
        self.server.login(self.email, self.password)

    def send_email(self, subject, message, to_email):
        msg = MIMEMultipart()
        msg["From"] = self.email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        self.server.sendmail(self.email, to_email, msg.as_string())
        print("Email sent successfully!")


def send_email(recipients: List[str], subject: str, body: str):
    gmail = Gmail(email="inquiries@llm.llc", password=os.environ.get("LLM_LLC_EMAIL_PASSWORD"))
    for recipient in recipients:
        gmail.send_email(to_email=recipient, subject=subject, message=body)
        print(f"[send_email] e-mail sent to {recipient}")


if __name__ == "__main__":
    send_email(["jesse@llm.llc"], "yeehaw", "yeehaw")
