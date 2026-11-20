
import os
import json
import uuid
import threading
from flask import Flask
from rubikabot import Bot, Dispatcher, Command

# تنظیمات محرمانه
TOKEN = os.environ["RUBIKA_BOT_TOKEN"]
ADMIN_ID = os.environ["ADMIN_ID"]

BOT_USERNAME = "NoizUpBot"
DB_FILE = "videos.json"

bot = Bot(TOKEN)
dp = Dispatcher(bot)
app = Flask(__name__)

# خواندن و ذخیره اطلاعات ویدئوها
def load_videos():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

videos = load_videos()

def save_videos():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)

# پیام شروع و دریافت لینک اختصاصی
@dp.message(Command("start"))
def start(message):
    aux_data = getattr(message, "aux_data", None)
video_id = getattr(aux_data, "start_id", None) if aux_data else None

    if video_id and video_id in videos:
        item = videos[video_id]
        try:
            bot.forward_message(
                from_chat_id=item["chat_id"],
                message_id=item["message_id"],
                to_chat_id=message.chat_id
            )
        except Exception:
            message.answer("ارسال ویدئو ناموفق بود. لطفاً دوباره تلاش کن.")
        return

    message.answer(
        "سلام! به ربات Noiz Up خوش اومدی ❤️\n"
        "برای دریافت ویدئو، لینک اختصاصی همون ویدئو رو باز کن."
    )

# دریافت ویدئو از مدیر
@dp.message()
def receive_video(message):
    if str(message.sender_id) != str(ADMIN_ID):
        return

    if not getattr(message, "file", None):
        return

    video_id = uuid.uuid4().hex[:10]

    videos[video_id] = {
        "chat_id": message.chat_id,
        "message_id": message.message_id
    }

    save_videos()

    link = f"https://rubika.ir/{BOT_USERNAME}?start={video_id}"

    message.answer(
        "✅ ویدئو ثبت شد!\n\n"
        f"🔗 لینک اختصاصی:\n{link}\n\n"
        "این لینک رو می‌تونی برای دیگران بفرستی."
    )

# صفحه سلامت سرویس برای Render
@app.route("/")
def home():
    return "Noiz Up Bot is running!"

@app.route("/health")
def health():
    return "OK", 200

def run_bot():
    dp.start_polling(offset_file="rubika_offset.json")

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
