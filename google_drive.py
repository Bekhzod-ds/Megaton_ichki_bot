# bot.py
import os
import telebot
from flask import Flask, request
from google_drive import upload_file_to_drive

API_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Example command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to Megaton Delivery Bot!")

# Example photo/file handler
@bot.message_handler(content_types=['photo', 'document'])
def handle_media(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id if message.photo else message.document.file_id)
        file_path = file_info.file_path
        downloaded_file = bot.download_file(file_path)

        local_filename = f"temp_{message.chat.id}.jpg"
        with open(local_filename, 'wb') as f:
            f.write(downloaded_file)

        drive_url = upload_file_to_drive("Yetkazmalar", local_filename, local_filename)
        bot.reply_to(message, f"✅ File uploaded: {drive_url}")

        os.remove(local_filename)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@app.route(f"/{API_TOKEN}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

@app.route("/", methods=['GET'])
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{os.environ.get('WEBHOOK_URL')}/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
