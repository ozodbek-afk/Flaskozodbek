import json
import os
import asyncio
from flask import Flask, request
from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Bot
)
from telegram.ext import (
    ApplicationBuilder,
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from admin import admin_panel, broadcast_start, handle_broadcast
from config import BOT_TOKEN, ADMIN_IDS

# === Fayl yo‘li
USERS_FILE = "users.json"

# === Foydalanuvchilarni yuklash va saqlash funksiyalari
def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_user(user_id, name, phone):
    users = load_users()
    users[str(user_id)] = {"name": name, "phone": phone}
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# === Start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    users = load_users()

    if str(user_id) in users:
        await update.message.reply_text(
            f"👋 Salom, {users[str(user_id)]['name']}! Siz allaqachon ro‘yxatdan o‘tgansiz.\n\nAsosiy menyu:",
            reply_markup=await get_main_menu()
        )
    else:
        contact_button = KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)
        keyboard = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "👋 Salom! TBC Bank kartasini olish uchun telefon raqamingizni yuboring:",
            reply_markup=keyboard
        )

# === Kontakt qabul qilish
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    contact = update.message.contact.phone_number
    save_user(user.id, user.first_name, contact)

    await update.message.reply_text(
        f"✅ Rahmat, {user.first_name}!\n📞 Raqamingiz: {contact}\n\nAsosiy menyu:",
        reply_markup=await get_main_menu()
    )

# === Asosiy menyu
async def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🎥 Video qo‘llanma", callback_data="video")],
        [InlineKeyboardButton("📄 Ishonchnoma hujjatlari", callback_data="docs")],
        [InlineKeyboardButton("🎁 Promokod haqida", callback_data="promo")],
        [InlineKeyboardButton("👨‍💻 Bog‘lanish 24/7", callback_data="admin")],
    ]
    return InlineKeyboardMarkup(keyboard)

# === Callback tugmalarni boshqarish
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "video":
        try:
            with open("/home/ozodbekpanjiyev/tbc/VN20250430_041020.mp4", "rb") as video_file:
                await query.message.reply_video(video=video_file, caption="Videodagi promokod eski, Yangi promokod: SCE438E8B1")
        except FileNotFoundError:
            await query.message.reply_text("❌ Video fayli topilmadi.")
        await query.delete_message()

    elif query.data == "docs":
        await query.message.reply_text("📄 Quyidagi hujjatlarni yuklab oling:")
        try:
            with open("/home/ozodbekpanjiyev/tbc/hujjat1.pdf", "rb") as doc1, \
                 open("/home/ozodbekpanjiyev/tbc/hujjat2.pdf", "rb") as doc2, \
                 open("/home/ozodbekpanjiyev/tbc/hujjat3.pdf", "rb") as doc3:
                await query.message.reply_document(document=doc1)
                await query.message.reply_document(document=doc2)
                await query.message.reply_document(document=doc3)
        except FileNotFoundError:
            await query.message.reply_text("❌ Hujjatlar topilmadi.")

    elif query.data == "promo":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="main")]])
        await query.edit_message_text(
            "🎁 [Code] SCE438E8B1    [link] https://app.tbcbank.uz/SfqR/7uyx8us5",
            reply_markup=markup,
            disable_web_page_preview=True
        )

    elif query.data == "admin":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Orqaga", callback_data="main")]])
        await query.edit_message_text("👨‍💻 Admin bilan bog‘lanish: @Tbc_card_admin", reply_markup=markup)

    elif query.data == "main":
        await send_main_menu(update, context)

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = await get_main_menu()
    if update.message:
        await update.message.reply_text("⬇️ Quyidagi menyudan tanlang:", reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text("⬇️ Quyidagi menyudan tanlang:", reply_markup=reply_markup)

# === Flask app va webhook
app = Flask(__name__)
bot = Bot(BOT_TOKEN)
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# === Handlerlar
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
telegram_app.add_handler(CallbackQueryHandler(handle_buttons))
telegram_app.add_handler(CommandHandler("adminpanel", admin_panel))
telegram_app.add_handler(CallbackQueryHandler(broadcast_start, pattern="^broadcast$"))

for admin_id in ADMIN_IDS:
    telegram_app.add_handler(MessageHandler(filters.TEXT & filters.User(admin_id), handle_broadcast))

@app.route(f'/{BOT_TOKEN}', methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.run(telegram_app.process_update(update))
    return "OK"

@app.route('/')
def index():
    return "Bot ishlayapti!"

@app.route('/setwebhook')
def set_webhook():
    url = f'https://flaskozodbek.onrender.com/{BOT_TOKEN}'
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(bot.set_webhook(url=url))
    loop.close()
    return 'Webhook muvaffaqiyatli o‘rnatildi!' if result else 'Webhook o‘rnata olmadik.'

# === Flask serverni ishga tushirish
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
