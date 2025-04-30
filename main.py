from flask import Flask, request
import telebot
import os

TOKEN = '7563506713:AAFeXPQApqWNdwZCtkr83yIR9aCF0G2M-Ls'
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode('utf-8'))
    bot.process_new_updates([update])
    return 'OK', 200

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Webhook Render orqali ishlayapti!")

@app.route('/setwebhook')
def set_webhook():
    webhook_url = f'https://Flaskozodbek.onrender.com/{TOKEN}'
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    return 'Webhook o‘rnatildi!', 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)