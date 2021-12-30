import time

from flask import Flask, render_template, redirect, request, json

from simulation import *
from server import Server

server = Server()

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin/<key>")
def admin(key=None):
    if key == server.admin_key:
        return render_template("admin.html", apiKey=key)
    else:
        return redirect("/")


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
@app.route("/admin-view/<key>", methods=["GET"])
def get_admin_view(key=None):
    if key == server.admin_key:
        return server.get_admin_view()
    return json.dumps({"error": "Permission denied"})