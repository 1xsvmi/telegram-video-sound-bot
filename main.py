from flask import Flask, request
import telebot, os, yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# أمر البداية
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👋 أهلا! أرسل رابط YouTube أو TikTok.\n"
                          "ثم اختر إن كنت تريد تحميل الفيديو أو الصوت.")

# استقبال الروابط
@bot.message_handler(func=lambda msg: msg.text.startswith("http"))
def handle_url(message):
    url = message.text.strip()
    markup = telebot.types.InlineKeyboardMarkup()
    btn1 = telebot.types.InlineKeyboardButton("🎥 فيديو", callback_data=f"video|{url}")
    btn2 = telebot.types.InlineKeyboardButton("🎵 صوت", callback_data=f"audio|{url}")
    markup.add(btn1, btn2)
    bot.reply_to(message, "اختر ما تريد تحميله:", reply_markup=markup)

# عند اختيار النوع
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    action, url = call.data.split("|", 1)
    bot.answer_callback_query(call.id, "⏳ جاري التحميل...")
    try:
        if action == "video":
            filename = download_media(url, video=True)
            bot.send_video(call.message.chat.id, open(filename, "rb"))
        else:
            filename = download_media(url, video=False)
            bot.send_audio(call.message.chat.id, open(filename, "rb"))
        os.remove(filename)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ حدث خطأ: {e}")

# دالة التحميل
def download_media(url, video=True):
    outtmpl = "file.%(ext)s"
    ydl_opts = {
        "format": "bestvideo+bestaudio/best" if video else "bestaudio",
        "outtmpl": outtmpl,
        "quiet": True,
        "noplaylist": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    return filename

# Webhook
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_str = request.stream.read().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=os.getenv("WEBHOOK_URL") + TOKEN)
    return "Bot started", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
