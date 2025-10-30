from flask import Flask, request
import requests
import os

app = Flask(__name__)

BALE_TOKEN = os.getenv("BALE_TOKEN")

# در این متغیر وضعیت کاربر نگه‌داری می‌شود تا بدانیم در چه مرحله‌ای است
user_state = {}

# توکن Authorization از فایل PowerShell شما
OKCS_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6ItmF2K3Zhdiv2K3Ys9mGINm-2YjYsdin2K3Zhdiv24wiLCJyb2xlIjoiT0tTQy5TVE9SRSIsIlN0b3JlSWQiOiJPS1MwNTI5MiIsIlN0b3JlUEFQIjoiMzY5Mi4xOTkiLCJVc2VyTmFtZSI6IjkyMDI5ODcxMiIsIlBBUENvZGUiOiIwIiwibmJmIjoxNzU2MjMyMDU2LCJleHAiOjE3NTYyMzU2NTYsImlhdCI6MTc1NjIzMjA1Nn0.L6_f4cZ9Zd56rJkyEK8JXZKxJ-4S1nkm8EJdGT9OQWo"  # 👈 کل توکن PowerShell خودت را اینجا بگذار

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        data = request.json
        print(data)
        if not data or 'message' not in data:
            return 'No message', 200

        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')

        # حالت 1: کاربر دستور /check فرستاده
        if text.strip() == '/check':
            user_state[chat_id] = 'waiting_barcode'
            send_message(chat_id, "📦 لطفاً بارکد کالا را وارد کنید:")
            return 'OK', 200

        # حالت 2: منتظر بارکد هستیم
        elif user_state.get(chat_id) == 'waiting_barcode':
            barcode = text.strip()
            send_message(chat_id, "⏳ در حال بررسی موجودی...")

            # تماس با API مورد نظر
            result_text = check_inventory(barcode)

            send_message(chat_id, f"✅ پاسخ از سرور:\n{result_text}")

            # بازگشت به حالت عادی
            user_state[chat_id] = None
            return 'OK', 200

        # دستور دیگر
        else:
            send_message(chat_id, "دستور ناشناخته است. برای شروع بنویسید /check")
            return 'OK', 200

    return 'Bale bot running!', 200


def check_inventory(barcode):
    """ارسال درخواست به API نمایش موجودی OKCS"""
    url = "https://sap.okcs.com/inventory/contradiction/api/ICS/displayInventory"

    headers = {
        "Authorization": OKCS_TOKEN,
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://webapp.okcs.com",
        "Referer": "https://webapp.okcs.com/",
        "Content-Type": "application/json",
        "Accept": "*/*"
    }

    body = {"itemNumber": barcode}

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=15)
        data = resp.json()
        return str(data)
    except Exception as e:
        return f"❌ خطا در ارتباط با سرور: {e}"


def send_message(chat_id, text):
    """ارسال پیام به بله"""
    url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending message: {e}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
