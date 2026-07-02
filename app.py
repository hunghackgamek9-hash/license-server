from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "VB TOOL KEY SERVER ONLINE"

@app.route("/verify-key", methods=["POST"])
def verify_key():
    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "No data"
        }), 400

    key = data.get("key")

    # Tạm thời chỉ để test
    if key == "TEST-KEY":
        return jsonify({
            "status": "success"
        })

    return jsonify({
        "status": "invalid"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
