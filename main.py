import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

BOT_TOKEN = "ТВОЙ_ТОКЕН_ЗДЕСЬ"
CHAT_ID = "ТВОЙ_CHAT_ID_ЗДЕСЬ"
URL = "https://www.ebay.com/itm/356848025074"

active = False
last_info_time = datetime.now() - timedelta(hours=1)
last_update_id = None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("❌ Telegram send error:", e)

def send_menu():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "▶️ Пуск", "callback_data": "start"},
                {"text": "⏹ Стоп", "callback_data": "stop"},
                {"text": "⚙️ Статус", "callback_data": "status"}
            ]
        ]
    }
    data = {
        "chat_id": CHAT_ID,
        "text": "🔘 Выберите действие:",
        "reply_markup": keyboard
    }
    try:
        requests.post(url, json=data)
    except Exception as e:
        print("❌ Ошибка при отправке меню:", e)

def check_stock():
    try:
        html = requests.get(URL).text
        has_out = "Out of stock" in html or "This item is out of stock" in html
        has_buy = "Add to cart" in html or "Buy It Now" in html or "Place bid" in html
        return (not has_out) and has_buy
    except Exception as e:
        print("❌ Ошибка при загрузке страницы:", e)
        return False

def check_commands():
    global active, last_update_id
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        response = requests.get(url).json()
        for update in response["result"]:
            update_id = update["update_id"]

            if last_update_id is not None and update_id <= last_update_id:
                continue

            last_update_id = update_id

            if "callback_query" in update:
                data = update["callback_query"]["data"]
                chat_id = str(update["callback_query"]["from"]["id"])

                if chat_id != CHAT_ID:
                    continue

                if data == "start":
                    active = True
                    send_telegram("▶️ Мониторинг запущен.")
                elif data == "stop":
                    active = False
                    send_telegram("⏹ Мониторинг остановлен.")
                elif data == "status":
                    status = "🟢 ВКЛЮЧЕН" if active else "🔴 ВЫКЛЮЧЕН"
                    send_telegram(f"⚙️ Статус бота: {status}")

            elif "message" in update:
                message = update["message"]
                text = message.get("text", "").lower()
                chat_id = str(message.get("chat", {}).get("id", ""))

                if chat_id != CHAT_ID:
                    continue

                if text == "/пуск":
                    active = True
                    send_telegram("▶️ Мониторинг запущен.")
                elif text == "/стоп":
                    active = False
                    send_telegram("⏹ Мониторинг остановлен.")
                elif text == "/статус":
                    status = "🟢 ВКЛЮЧЕН" if active else "🔴 ВЫКЛЮЧЕН"
                    send_telegram(f"⚙️ Статус бота: {status}")
                elif text == "/меню":
                    send_menu()

    except Exception as e:
        print("❌ Ошибка в check_commands:", e)

def main():
    global last_info_time
    print("🚀 Бот запущен с Telegram-кнопками.")
    send_telegram("🤖 Бот запущен. Используй кнопки или команды /пуск, /стоп, /статус.")
    send_menu()

    while True:
        check_commands()

        if active:
            if check_stock():
                send_telegram("🛒 Товар в наличии! 👉 https://www.ebay.com/itm/356848025074")
            else:
                now = datetime.now()
                if now - last_info_time >= timedelta(hours=1):
                    send_telegram("⏳ Я работаю, но товара пока нет.")
                    last_info_time = now
        else:
            print("⏸ Мониторинг выключен.")

        time.sleep(60)

if __name__ == "__main__":
    main()
