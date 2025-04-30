from flask import Flask, request
import telebot
import os

TOKEN = '8101801994:AAHiwSIALDSkD3-6UWfJKjJCWGpI4HT0iDQ'  # Telegram bot token
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# GET so‘rovi orqali serverni tekshirish (Bu URL'ga kirganingizda server ishlayapti deb javob beradi)
@app.route('/', methods=['GET'])
def index():
    return 'Bot ishlayapdi', 200

# Webhook orqali Telegram xabarlarini qabul qilish (POST so‘rovi)
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode('utf-8'))  # Telegram'dan kelgan xabarni qabul qilish
    bot.process_new_updates([update])  # Yangi xabarni bot orqali qayta ishlash
    return 'OK', 200

# /start komandasi uchun handler
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Webhook Render orqali ishlayapti!")  # Botdan xabar yuborish

# Webhookni o‘rnatish uchun GET so‘rovi
@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    webhook_url = f'https://Flaskozodbek.onrender.com/{TOKEN}'  # Render serveringizdagi URL
    bot.remove_webhook()  # Eski webhookni olib tashlash
    bot.set_webhook(url=webhook_url)  # Yangi webhookni o‘rnatish
    return 'Webhook o‘rnatildi!', 200  # Tasdiqlash xabari

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Portni o‘rnatish
    app.run(host='0.0.0.0', port=port)  # Flask ilovasini ishga tushirish
