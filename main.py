import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
import asyncio, sqlite3, os

TOKEN = "8049463348:AAHoPqcnOomirlgIGSlVaSFz0YRvyeaNC2U"
CHANNEL_USERNAME = "@Premyeramultifilmlar"
ADMIN_ID = 5663190258

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# Telegram application
application = ApplicationBuilder().token(TOKEN).build()

# DB connection
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
conn.commit()

def save_user(user_id):
    c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

async def is_member(user_id):
    try:
        memb = await application.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return memb.status in ["member", "creator", "administrator"]
    except:
        return False

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id)
    if await is_member(user.id):
        if user.id == ADMIN_ID:
            await update.message.reply_text("Assalomu alaykum, admin! Buyruqlarni yuboring.")
        else:
            await update.message.reply_text("Salom, film kodini yuboring.")
    else:
        buttons = [
            [InlineKeyboardButton("✅ Kanalga a'zo bo'lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("🔄 Tekshirish", callback_data="check_membership")]
        ]
        await update.message.reply_text(
            "Botdan foydalanish uchun avval kanalga a'zo bo‘ling❗️",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

# callback va/xabarlar
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Xabar qabul qilindi!")

async def button_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "check_membership":
        if await is_member(query.from_user.id):
            await query.edit_message_text("✅ A'zo ekansiz, davom eting.")
        else:
            await query.edit_message_text("❌ Siz hali kanal a'zosi emassiz.")

# Webhook route
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    asyncio.run(application.process_update(update))
    return "OK"

@app.route("/")
def home():
    return "multfilmboti ishlayapti!"

# Main
if __name__ == "__main__":
    WEBHOOK_URL = f"https://multfilmboti.onrender.com/{TOKEN}"
    asyncio.run(application.bot.set_webhook(WEBHOOK_URL))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_cb))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)