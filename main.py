from flask import Flask, request
import telebot, os

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# أمر البداية
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 أهلا! أرسل رابط YouTube أو TikTok وسأجهزه لك.")

# أي رسالة نصية
@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    url = message.text.strip()
    bot.reply_to(message, f"📥 لقد استلمت الرابط: {url}")

# استقبال التحديثات من تيليجرام
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_str = request.stream.read().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

# إعداد Webhook
@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=os.getenv("WEBHOOK_URL") + TOKEN)
    return "Bot started", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
