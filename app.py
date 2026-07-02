from flask import Flask, request, jsonify
import sqlite3
import random
import string
import time

app = Flask(__name__)

DB = "database.db"
KEY_EXPIRE = 86400  # 24 giờ


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS keys(
        device_id TEXT PRIMARY KEY,
        key TEXT NOT NULL,
        expires_at INTEGER NOT NULL
    )
    """)

    conn.commit()
    conn.close()


init_db()


def generate_key():
    chars = string.ascii_uppercase + string.digits
    return "NVB-" + "".join(random.choice(chars) for _ in range(16))


@app.route("/")
def home():
    return "NVB KEY SERVER ONLINE"


@app.post("/issue-key")
def issue_key():

    data = request.get_json()

    device_id = data.get("device_id")

    if not device_id:
        return jsonify({
            "status": False,
            "message": "Thiếu device_id"
        }), 400

    conn = get_db()

    row = conn.execute(
        "SELECT * FROM keys WHERE device_id=?",
        (device_id,)
    ).fetchone()

    now = int(time.time())

    if row and row["expires_at"] > now:
        conn.close()

        return jsonify({
            "status": True,
            "key": row["key"],
            "expires_at": row["expires_at"]
        })

    new_key = generate_key()
    expires = now + KEY_EXPIRE

    conn.execute("""
    INSERT OR REPLACE INTO keys(device_id,key,expires_at)
    VALUES(?,?,?)
    """, (
        device_id,
        new_key,
        expires
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "status": True,
        "key": new_key,
        "expires_at": expires
    })


@app.post("/verify-key")
def verify_key():

    data = request.get_json()

    device_id = data.get("device_id")
    key = data.get("key")

    conn = get_db()

    row = conn.execute(
        "SELECT * FROM keys WHERE device_id=?",
        (device_id,)
    ).fetchone()

    conn.close()

    if row is None:
        return jsonify({
            "status": False,
            "message": "Thiết bị chưa có key"
        })

    if row["key"] != key:
        return jsonify({
            "status": False,
            "message": "Sai key"
        })

    if row["expires_at"] < int(time.time()):
        return jsonify({
            "status": False,
            "message": "Key đã hết hạn"
        })

    return jsonify({
        "status": True,
        "message": "Key hợp lệ"
    })


if __name__ == "__main__":
    app.run(debug=True)