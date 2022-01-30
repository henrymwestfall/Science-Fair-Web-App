import random
import requests
import json
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import numpy as np


url = input("URL: ")
api_key = input("API key: ")

agent_data = json.loads(
    requests.get(f"{url}/simulation-state/{api_key}").text
)["agentData"]

keys = [data[0] for data in agent_data]
random.shuffle(keys)

with open("apikeys.txt", "w") as f:
    for k in keys[:-1]:
        f.write(k + "\n")
    f.write(keys[-1])

with open("client_emails.txt", "r") as f:
    client_emails = f.readlines()


with open("password.txt", "r") as f:
    password = f.read()


def send_plaintext_email(receiver_address, access_code):
    sender_address = 'henrywestfall.sciencefair@gmail.com'

    message = MIMEMultipart()
    message["From"] = sender_address
    message["To"] = receiver_address
    message["Subject"] = "Your Access Code"
    mail_content = f"Hello,\n\nYour access code is {access_code}\n\nCheers,\nHenry"
    message.attach(MIMEText(mail_content, 'plain'))

    session = smtplib.SMTP("smtp.gmail.com", 587)
    session.starttls()
    session.login(sender_address, password)
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)


for k, client_email in zip(keys, client_emails):
    send_plaintext_email(client_email, k)