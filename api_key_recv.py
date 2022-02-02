import random
import requests
import json
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import numpy as np

from src.email_api import send_plaintext_email


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


for k, client_email in zip(keys, client_emails):
    send_plaintext_email(
        client_email, 
        password,
        "Your Access Code",
        f"Hello,\n\nYour access code is {k}\n\nCheers,\nHenry"
    )