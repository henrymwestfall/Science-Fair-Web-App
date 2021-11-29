from math import inf
import random

from flask import Flask, render_template, request, json

from simulation import *


def api_key_generator(length=6):
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

app = Flask(__name__)
agents_by_key = {next(api_keys): agent for agent in sim.get_all_agents()}


def get_client_api_key():
    for key, agent in agents_by_key.items():
        if agent.awaiting_client:
            agent.awaiting_client = False
            return key


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/new-apikey", methods=["GET"])
def get_api_key():
    return json.dumps({"apiKey": get_client_api_key()})


@app.route("/state/<key>", methods=["GET"])
def get_state(key=None):
    agent = agents_by_key.get(key)
    if agent != None:
        return json.dumps({
            "error": None,
            "score": agent.score,
            "issues": sim.issues,
            "messages": agent.get_feed(),
            "outDegree": sim.get_out_degree(agent)
        })
    return json.dumps({"error": "keyNotFound"})


@app.route("/send-message/<key>", methods=["POST"])
def send_message(key=None):
    agent = agents_by_key.get(key)
    message = request.form.get("message")
    if agent != None and message != None:
        agent.express_belief_state(message)
    return json.dumps({"error": None})


@app.route("/unfollow-influencer/<key>", methods=["POST"])
def unfollow_influencer(key=None):
    agent = agents_by_key.get(key)
    influencer_id = request.form.get("influencer-id")
    if agent != None and influencer_id != None:
        agent.unfollow_influencer(influencer_id)
    return json.dumps({})