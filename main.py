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
        "x-okcs-timestamp": "cu95hsA1UPZunXejIpp8hgoQVJDa5BH1Mn218mkwFqK12QC8HNroeQLvDrSvlUC08vtYpmLSEvfpaIWZsvmPZx2Cu5sS5M6daiiCugz+R3kVwFgDAAMUX6b1IdLiYcqm+kmWhkGEWBLIX8bmzVd4byth+SJtUhBdsIkxtsVRjD2QV7cmPJtwZepFjl1AqgiMAL8Vf4pDpCrlkvruENck0FGbq1sHFO7g8pYNUt75Q62WFuo865nLniSZXKX0cPd2gY4rt7pz6hasIkaTyu5DcbT34nja7NwBQGUCZxfCSuq+R22bhS6FVOG7gYmZi91LY0MS/JJNQO4DoOYVPb21nHMpB26Ixl1m4Y5nZ9puyW8kIGgIuZXrHcxCg/vPc/88+KxN+SXZ6rNojPzeYSGbS8yLEhnEYBMQKgKGyePftvEO6mDycTWS15Grj6AojKoqByaRzHJyIkmMXLe1TIOx30+m0SE/bPUO99Ox8fDWaVk7vJHuWrKDDiFPQSnNRihBuPGZOLrersCpthWmr4sd3PiqregJA4t2spg2pdZkFLjNAOd9x1OQ/z8lCtdyIvJabBzi95urHhHW375nVJcd5F3oMgy5B0DOSiyxTPnWvqV+IXJhTqi4636IwKPjdshVDnfZoC4/5pxL2ij1B8wAEMIPtCyEddT2EvJVjQf9j1cNHLg3WlSvFrUzehBqB6ZVUdYHHJDhZbQv0bViL7Si4hy2XyeWCymx80sqHu8OGgXvAOwKaVAcB+MaINYP+g+ix0zSwZTHxy4FdqzSmVWNNYUbvMERZ5RZf807jaYbNH5cGegEqicReJyfPDyyC+at1c2+JA4inPbs6HqDi7NRF/FrN9Czb3HYMftLGad4EFiyxxICfUHFCqYkq7NC27Yb1yCd3Y8XvP7wGteowuODPdBoyTF5h+o1fKoCuuHPiZKEv/rn6yFx7pmpI3saj34/QxBYYRwTXzbF/4/TQ7LGt1wghbPhipGYKvkTL/CTFVjsv3nrMRaM5asfd7P331l9KoZiMifu4R9LlYK8zCaWPKpt/BHNVIlqffbiRo9Q5Wx3IeJYx67N29kqr4vBdQbeDJMxxaW4hRF/sxX2R4DU8XeNgzpObMQS7+SSvxsZkRpMpFZjXpAiPEZAbyp52Owfzr2ETp1RsRsIjfCxlKviONDIHPJsMlxdov9BbfFbhyGpOdzdDcSpKALAbpTdYVa6HUC+lvRdnRug2veSRxmfuJUKmacEtoJ8a1I2Zqn87Ln04xeAOblgynAmAGJC86+VirXwIqudoj+/poSyoOVity4mk9TY9zHHw0X10F2ZEk9onZSIk71FARkXWMyYKHbg2Yk/sMlDaB7c90g627Hikg=="
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
