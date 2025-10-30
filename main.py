from flask import Flask, request
import requests
import os
import base64

app = Flask(__name__)

# توکن بله از Environment متغیر
BALE_TOKEN = os.getenv("BALE_TOKEN")

# توکن Authorization از PowerShell یا Network Tab خودت
OKCS_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6ItmF2K3Zhdiv2K3Ys9mGINm-2YjYsdin2K3Zhdiv24wiLCJyb2xlIjoiT0tTQy5TVE9SRSIsIlN0b3JlSWQiOiJPS1MwNTI5MiIsIlN0b3JlUEFQIjoiMzY5Mi4xOTkiLCJVc2VyTmFtZSI6IjkyMDI5ODcxMiIsIlBBUENvZGUiOiIwIiwibmJmIjoxNzYxODQyNjI2LCJleHAiOjE3NjE4NDYyMjYsImlhdCI6MTc2MTg0MjYyNn0.2RzlJCTHhKUlDinOYOuoCr7HHrtEQkD0whtylFoqLRw"


@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        data = request.json
        if not data or 'message' not in data:
            return 'No message', 200

        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '').strip()

        if text == '/check':
            send_message(chat_id, "📦 لطفاً بارکد را وارد کنید:")
            user_states[chat_id] = 'waiting_barcode'
        elif user_states.get(chat_id) == 'waiting_barcode':
            send_message(chat_id, "⏳ در حال بررسی موجودی...")
            result = check_inventory(text)
            send_message(chat_id, result)
            user_states[chat_id] = None
        else:
            send_message(chat_id, "برای شروع بنویس /check")

        return 'OK', 200

    return 'Running', 200


user_states = {}


def check_inventory(barcode: str) -> str:
    """ارسال POST به API OKCS"""
    url = "https://sap.okcs.com/inventory/contradiction/api/ICS/displayInventory"

    # هدرهایی که مرورگر واقعی می‌فرستد:
    headers = {
        "Authorization": OKCS_TOKEN,
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36",
        "Origin": "https://webapp.okcs.com",
        "Referer": "https://webapp.okcs.com/",
        "Content-Type": "application/json",
        "Accept": "*/*",
        # این هدر از DevTools کپی شده، باید دقیق بفرستی:
        "x-okcs-timestamp": generate_timestamp()
    }

    payload = {"itemNumber": barcode}

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        if r.status_code == 200:
            data = r.json()
            return f"""
📦 موجودی کالا:
🔹 فیزیکی: {data.get('physicalInventory')}
🔹 قابل فروش: {data.get('availableInventory')}
"""
        else:
            return f"⚠️ خطا از سمت سرور ({r.status_code}): {r.text}"
    except requests.exceptions.ConnectTimeout:
        return "❌ ارتباط با سرور برقرار نشد (Timeout)"
    except Exception as e:
        return f"❌ خطا: {str(e)}"


def generate_timestamp():
    """
    شبیه‌سازی مقدار x-okcs-timestamp
    سرور احتمالاً بررسی خاصی رویش ندارد (base64 رمز شده تصادفی)
    ولی داشتنش ضروری است تا درخواست reject نشود.
    """
    random_bytes = os.urandom(256)
    ts = base64.b64encode(random_bytes).decode('utf-8')
    return ts


def send_message(chat_id, text):
    """ارسال پیام به Bot API بله"""
    try:
        url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        requests.post(url, json=data)
    except Exception as e:
        print("خطا در ارسال پاسخ:", e)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
