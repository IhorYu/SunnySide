import telebot
from decouple import config
from openai import OpenAI

bot_token = config('BOT_TOKEN')
client = OpenAI(api_key=config("OPENAI_API_KEY"))
weather_api_key = (config("WEATHER_API_KEY"))

bot = telebot.TeleBot(bot_token)
