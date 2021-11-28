from math import inf
import random

from flask import Flask, render_template, request, json

from simulation import *


app = Flask(__name__)
agents_by_key = {}


def api_key_generator(length=20):
    used = set()
    while True:
        key = ""
        for i in range(length):
            key += chr(random.randint(97, 122))

        if not (key in used):
            used.add(key)
            yield key
            
api_keys = api_key_generator()
admin_key = next(api_keys)
print("Admin key:", admin_key)


with open("parameters.json") as f:
    params = json.load(f)

sim = Simulation(params)
sim.start()


@app.route("/get-client-api-key", methods=["GET"])
def get_client_api_key():
    for key, agent in agents_by_key.items():
        if agent.awaiting_client:
            agent.awaiting_client = False
            return json.dumps({"key": key})


@app.route("/get-feed/<key>", methods=["GET"])
def get_feed(key=None):
    agent = agents_by_key.get(key)
    if agent != None:
        return json.dumps({"messages": agent.get_feed()})


@app.route("/get-score/<key>", methods=["GET"])
def get_score(key=None):
    agent = agents_by_key.get(key)
    if agent != None:
        return json.dumps({"score": agent.score})


@app.route("/send-message/<key>", methods=["POST"])
def send_message(key=None):
    agent = agents_by_key.get(key)
    message = request.form.get("message")
    if agent != None and message != None:
        agent.set_messages(message)


@app.route("/unfollow-influencer/<key>", methods=["POST"])
def unfollow_influencer(key=None):
    agent = agents_by_key.get(key)
    influencer_id = request.form.get("influencer-id")
    if agent != None and influencer_id != None:
        agent.unfollow_influencer(influencer_id)