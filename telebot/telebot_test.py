import os
import telebot

API_KEY = os.getenv('API_KEY')
#API_KEY = "6074681084:AAGSjqYnAzXEGBgaYWH11b5S2Zp-_l9-3sc"
CHAT_ID = ""

bot = telebot.TeleBot(API_KEY)

@bot.message_handlers(commands=["start"])
def greet(message):
    bot.message(message.chat.id, message.chat.id)

bot.pooling()