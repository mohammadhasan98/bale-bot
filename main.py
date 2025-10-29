from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "POST":
        data = request.json
        if data and "message" in data:
            msg = data["message"]["text"]
            chat_id = data["message"]["chat"]["id"]
            # پاسخ تست برای پیام
            return {"ok": True}
    return "Bale bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
