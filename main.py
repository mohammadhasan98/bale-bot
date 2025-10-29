from flask import Flask, request
import requests
import os

app = Flask(__name__)

BALE_TOKEN = os.getenv("BALE_TOKEN")  # بگیری از متغیر محیطی Render

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "POST":
        data = request.json
        if data and "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"]["text"]

            # پاسخ تستی
            reply = f"سلام! گفتی: {text}"
            
            url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendMessage"
            payload = {"chat_id": chat_id, "text": reply}
            requests.post(url, json=payload)
    return "Bale bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
