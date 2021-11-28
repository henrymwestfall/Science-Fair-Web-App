import requests
import pandas as pd

surname_html = requests.get("https://namecensus.com/last-names/").text
firstname_html = requests.get("https://namecensus.com/first-names/common-male-first-names/").text
surname_df = pd.read_html(surname_html)[0]
firstname_df = pd.read_html(firstname_html)[0]

with open("surnames.txt", "w") as f:
    for surname in list(surname_df["Name"]):
        f.write(surname.lower().capitalize() + "\n")

with open("firstnames.txt", "w") as f:
    for firstname in list(firstname_df["Name"]):
        f.write(firstname.lower().capitalize() + "\n")