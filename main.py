import logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto, InputMediaVideo
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
import sqlite3

# TOKEN va kanal sozlamalari
TOKEN = "8049463348:AAHoPqcnOomirlgIGSlVaSFz0YRvyeaNC2U"
CHANNEL_USERNAME = "@Premyeramultifilmlar"
ADMIN_ID = 5663190258

# Logger
logging.basicConfig(level=logging.INFO)

# Baza
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
conn.commit()

def save_user(user_id):
    c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def get_all_users():
    c.execute("SELECT user_id FROM users")
    return [row[0] for row in c.fetchall()]

async def is_member(user_id):
    try:
        member = await app.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "creator", "administrator"]
    except:
        return False

def get_admin_keyboard():
    keyboard = [
        [KeyboardButton("📢 Reklama yuborish")],
        [KeyboardButton("📊 Statistika")],
        [KeyboardButton("❌ Bekor qilish"), KeyboardButton("◀️ Orqaga")],
        [KeyboardButton("🚫 Bloklash")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id)

    if await is_member(user.id):
        if user.id == ADMIN_ID:
            await update.message.reply_text(
                "Kod yuboring yoki pastdagi tugmalardan foydalaning:",
                reply_markup=get_admin_keyboard()
            )
        else:
            await update.message.reply_text("✍️🏼 Film kodini yuboring")
    else:
        keyboard = [
            [InlineKeyboardButton("✅Kanalga a’zo bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("🔄Tekshirish", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Botdan foydalanish uchun avval kanalga a’zo bo‘ling❗️",
            reply_markup=reply_markup
        )

async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id)

    if not await is_member(user.id):
        keyboard = [
            [InlineKeyboardButton("✅Kanalga a’zo bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("🔄Tekshirish", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Iltimos, avval kanalga a’zo bo‘ling❗️", reply_markup=reply_markup)
        return

    text = update.message.text.strip()

    if user.id == ADMIN_ID:
        if text == "📊 Statistika":
            all_users = get_all_users()
            await update.message.reply_text(f"Foydalanuvchilar soni: {len(all_users)}")
            return
        elif text == "📢 Reklama yuborish":
            await update.message.reply_text("Reklama matnini yuboring, rasm yoki video yuborishingiz mumkin. ❌ Bekor qilish tugmasini bosing.")
            context.user_data["reklama_mode"] = True
            return
        elif text == "❌ Bekor qilish":
            context.user_data["reklama_mode"] = False
            await update.message.reply_text("Reklama yuborish bekor qilindi.", reply_markup=get_admin_keyboard())
            return
        elif text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Asosiy menyuga qaytdingiz.", reply_markup=get_admin_keyboard())
            return
        elif text == "🚫 Bloklash":
            await update.message.reply_text("Bloklash uchun foydalanuvchi ID raqamini yuboring.")
            context.user_data["block_user_mode"] = True
            return

    if context.user_data.get("reklama_mode"):
        # Media faylni yuborish
        if update.message.text:
            users = get_all_users()
            count = 0
            for user_id in users:
                try:
                    await context.bot.send_message(chat_id=int(user_id), text=text)
                    count += 1
                except:
                    continue
            await update.message.reply_text(f"Reklama {count} foydalanuvchiga yuborildi.")
        elif update.message.photo:
            users = get_all_users()
            count = 0
            for user_id in users:
                try:
                    await context.bot.send_photo(chat_id=int(user_id), photo=update.message.photo[-1].file_id)
                    count += 1
                except:
                    continue
            await update.message.reply_text(f"Rasm {count} foydalanuvchiga yuborildi.")
        elif update.message.video:
            users = get_all_users()
            count = 0
            for user_id in users:
                try:
                    await context.bot.send_video(chat_id=int(user_id), video=update.message.video.file_id)
                    count += 1
                except:
                    continue
            await update.message.reply_text(f"Video {count} foydalanuvchiga yuborildi.")
        context.user_data["reklama_mode"] = False
        return

    if text.isdigit():
        link = f"https://t.me/{CHANNEL_USERNAME[1:]}/{text}"
        await update.message.reply_text(f"🎬 Mana siz so‘ragan film:👇\n{link}")
    else:
        await update.message.reply_text("Iltimos, faqat raqamli kod yuboring❗")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if query.data == "check_membership":
        if await is_member(user_id):
            if user_id == ADMIN_ID:
                await query.message.reply_text(
                    "✅ Botdan foydalanishingiz mumkin.\n✍🏼 Film kodini yuboring.",
                    reply_markup=get_admin_keyboard()
                )
            else:
                await query.message.reply_text("✅ Botdan foydalanishingiz mumkin.\n✍🏼 Film kodini yuboring.")
        else:
            keyboard = [
                [InlineKeyboardButton("✅Kanalga a’zo bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
                [InlineKeyboardButton("🔄Tekshirish", callback_data="check_membership")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Hali kanalga a'zo bo'lmadingiz❌", reply_markup=reply_markup)

async def block_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("block_user_mode"):
        user_id = update.message.text.strip()

        try:
            user_id = int(user_id)
            # Foydalanuvchini bloklash
            await context.bot.kick_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
            await update.message.reply_text(f"Foydalanuvchi {user_id} bloklandi.")
        except:
            await update.message.reply_text("Iltimos, to‘g‘ri foydalanuvchi ID raqamini kiriting.")
        
        context.user_data["block_user_mode"] = False

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
    app.add_handler(MessageHandler(filters.PHOTO, handle_code))
    app.add_handler(MessageHandler(filters.VIDEO, handle_code))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^\d+$'), block_user))  # Bloklash uchun ID qabul qilish
    app.run_polling()
