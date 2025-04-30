import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler
import os

TOKEN = '8101801994:AAHiwSIALDSkD3-6UWfJKjJCWGpI4HT0iDQ'  # Tokenni shu yerga yozing
bot = Bot(token=TOKEN)
app = Flask(__name__)

# Dispatcher — handlerlarni boshqaradi
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

# Log yozish (muammo bo‘lsa oson aniqlash uchun)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# /start komandasi
def start(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Webhook python-telegram-bot orqali ishlayapti!")

dispatcher.add_handler(CommandHandler("start", start))

# Webhook endpoint
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'OK'

# Oddiy test endpoint
@app.route('/')
def index():
    return 'Bot ishlayapti!'

# Webhook o‘rnatish
@app.route('/setwebhook')
def set_webhook():
    url = f'https://flaskozodbek.onrender.com/{TOKEN}'  # Render'dagi URL
    success = bot.set_webhook(url=url)
    if success:
        return 'Webhook muvaffaqiyatli o‘rnatildi!'
    else:
        return 'Webhook o‘rnata olmadik.'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
