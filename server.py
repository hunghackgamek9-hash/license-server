from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

def load_keys():
    with open("keys.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_keys(data):
    with open("keys.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

@app.route("/")
def home():
    return "License Server is running!"

@app.route("/check", methods=["POST"])
def check():

    data = request.json

    key = data.get("key")
    hwid = data.get("hwid")

    keys = load_keys()

    if key not in keys:
        return jsonify({
            "status": False,
            "message": "Key không tồn tại"
        })

    info = keys[key]

    expire = datetime.strptime(info["expire"], "%Y-%m-%d")

    if expire < datetime.now():
        return jsonify({
            "status": False,
            "message": "Key đã hết hạn"
        })

    if not info["used"]:
        info["used"] = True
        info["device"] = hwid
        save_keys(keys)

        return jsonify({
            "status": True,
            "message": "Kích hoạt thành công"
        })

    if info["device"] != hwid:
        return jsonify({
            "status": False,
            "message": "Key đã kích hoạt trên máy khác"
        })

    return jsonify({
        "status": True,
        "message": "Đăng nhập thành công"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000
