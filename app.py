import time

from flask import Flask, render_template, redirect, request, json

from simulation import *
from server import Server

server = Server()
print(server.admin_key)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/new-apikey", methods=["GET"])
def get_api_key():
    return json.dumps({"apiKey": server.get_client_api_key()})


@app.route("/state/<key>", methods=["GET"])
def get_state(key=None):
    return server.get_state(key)


@app.route("/send-message/<key>", methods=["POST"])
def send_message(key=None):
    data = json.loads(request.form.get("data"))
    message = data.get("message")
    return server.send_message(key, message)


@app.route("/unfollow-influencer/<key>", methods=["POST"])
def unfollow_influencer(key=None):
    influencer_id = request.data.get("influencer-id")
    return server.unfollow_influencer(key, influencer_id)


# admin routes
@app.route("/admin/<key>")
def admin(key=None):
    if key == server.admin_key:
        return render_template("admin.html", apiKey=key)
    else:
        return redirect("/")


@app.route("/simulation-setup/<key>")
def simulation_setup(key=None):
    if key == server.admin_key:
        return render_template("simulation_setup.html", apiKey=key)
    else:
        return redirect("/")


@app.route("/simulation-state/<key>", methods=["GET"])
def get_admin_view(key=None):
    if key == server.admin_key:
        return server.get_simulation_state()
    return json.dumps({"error": "Permission denied"})


@app.route("/create-simulation/<key>", methods=["POST"])
def create_simulation(key=None):
    if key == server.admin_key:
        data = json.loads(request.form.get("data"))
        params = data.get("params")
        server.start_simulation(params)
        return json.dumps({"error": None})
    else:
        return json.dumps({"error": "Permission denied"})


@app.route("/get-default-parameters/<key>", methods=["GET"])
def get_default_parameters(key=None):
    if key == server.admin_key:
        return json.dumps(server.default_parameters)
    else:
        return json.dumps({"error": "Permission denied"})