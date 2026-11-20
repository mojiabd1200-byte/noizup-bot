
import os
import json
import uuid
import threading
from flask import Flask
from rubikabot import Bot, Dispatcher, Command

TOKEN = os.environ["RUBIKA_BOT_TOKEN"]
ADMIN_ID = os.environ["ADMIN_ID"]
BOT_USERNAME = "NoizUpBot"

DB_FILE = "media.json"

bot = Bot(TOKEN)
dp = Dispatcher(bot)
app = Flask(__name__)


def load_media():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


media = load_media()


def save_media():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(media, f, ensure_ascii=False)


@dp.message(Command("start"))
def start(message, command_args=None):

    media_id = command_args or getattr(message, "start_id", None)

    if not media_id:
        aux = getattr(message, "aux_data", None)
        media_id = getattr(aux, "start_id", None) if aux else None

    if media_id and media_id in media:
        item = media[media_id]

        try:
            bot.forward_message(
                from_chat_id=item["chat_id"],
                message_id=item["message_id"],
                to_chat_id=message.chat_id
            )
        except Exception as e:
            print("FORWARD ERROR:", repr(e))
            message.answer("ارسال فایل ناموفق بود. لطفاً دوباره تلاش کن.")

        return

    message.answer(
        "سلام! ❤️ به Noiz Up خوش اومدی.\n"
        "برای دریافت فایل، باید از لینک اختصاصی همون فایل وارد بشی."
    )


@dp.message()
def receive_media(message):

    if str(message.sender_id) != str(ADMIN_ID):
        return

    file = getattr(message, "file", None)

    if not file:
        message.answer("لطفاً آهنگ یا ویدیو رو به صورت فایل ارسال کن.")
        return

    media_id = uuid.uuid4().hex[:12]

    media[media_id] = {
        "chat_id": message.chat_id,
        "message_id": message.message_id
    }

    save_media()

    link = f"https://rubika.ir/{BOT_USERNAME}?start={media_id}"

    message.answer(
        "✅ فایل با موفقیت ثبت شد!\n\n"
        f"🔗 لینک اختصاصی:\n{link}\n\n"
        "این لینک رو برای دیگران بفرست."
    )


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
