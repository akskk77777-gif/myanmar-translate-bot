import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from flask import Flask
from threading import Thread

# ========== Config ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TRANSLATE_API = "https://libretranslate.de/translate"

# ========== Flask App (UptimeRobot ping) ==========
app = Flask('')

@app.route('/')
def home():
    return "🤖 Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# ========== Translation ==========
def is_myanmar(text):
    for char in text:
        if '\u1000' <= char <= '\u109F':
            return True
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐 *Myanmar Translate Bot*\n\n"
        "ဘာသာပြန်ချင်တဲ့ စာသားကို ပို့ပေးပါ။\n"
        "Auto detect လုပ်ပြီး မြန်မာ↔English ပြန်ပေးပါမယ်။\n\n"
        "📌 *Usage:*\n"
        "• မြန်မာစာ ပို့ရင် → English ပြန်\n"
        "• English ပို့ရင် → မြန်မာစာ ပြန်",
        parse_mode="Markdown"
    )

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    source = "my" if is_myanmar(text) else "en"
    target = "en" if source == "my" else "my"
    
    try:
        response = requests.post(TRANSLATE_API, data={
            "q": text,
            "source": source,
            "target": target,
            "format": "text"
        }, timeout=10)
        result = response.json()
        translated = result.get("translatedText", "ဘာသာပြန်ရာမှာ အမှားတစ်ခုဖြစ်သွားပါတယ်။")
        await update.message.reply_text(f"📝 *ပြန်ဆိုချက်:*\n\n{translated}", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text("⚠️ ဘာသာပြန်စနစ် အဆင်မပြေပါ။ နောက်မှ ထပ်စမ်းကြည့်ပါ။")

def main():
    Thread(target=run_flask).start()
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_text))
    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()