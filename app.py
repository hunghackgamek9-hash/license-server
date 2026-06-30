from flask import Flask, request, jsonify
import random
import string
import json
import time
import os

app = Flask(__name__)

KEY_FILE = "keys.json"

if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, "w") as f:
        json.dump({}, f)

def load():
    with open(KEY_FILE, "r") as f:
        return json.load(f)

def save(data):
    with open(KEY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def create_key():
    return "VB-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=12))

@app.route("/getkey")
def getkey():
    key = create_key()

    data = load()
    data[key] = {
        "expired": int(time.time()) + 86400
    }
    save(data)

    return jsonify({"key": key})

@app.route("/check", methods=["POST"])
def check():
    req = request.json
    key = req["key"]

    data = load()

    if key not in data:
        return jsonify({"status": "error"})

    if time.time() > data[key]["expired"]:
        del data[key]
        save(data)
        return jsonify({"status": "expired"})

    return jsonify({"status": "ok"})

app.run(host="0.0.0.0", port=5000)