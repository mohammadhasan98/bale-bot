from flask import Flask, request
import requests
import os

app = Flask(__name__)

BALE_TOKEN = os.getenv("BALE_TOKEN")

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        data = request.json

        if not data:
            return 'No data received', 400

        # اگر پیام متن داشت جواب بده
        if 'message' in data and 'text' in data['message']:
            chat_id = data['message']['chat']['id']
            text = data['message']['text']  # متن کاربر

            reply = f"✅ دریافت شد!\nمتن: {text}"

            url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendMessage"
            payload = {'chat_id': chat_id, 'text': reply}
            headers = {'Content-Type': 'application/json'}

            try:
                r = requests.post(url, json=payload, headers=headers)
                print("Send response:", r.text)
            except Exception as e:
                print("Error sending message:", e)

        return 'OK', 200

    return 'Bale bot running!', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
