import telebot
from decouple import config
from openai import OpenAI

# Retrieve the bot token and OpenAI API key from the environment variables
bot_token = config('BOT_TOKEN')
client = OpenAI(api_key=config("OPENAI_API_KEY"))
weather_api_key = (config("WEATHER_API_KEY"))

# Initialize the Telegram bot
bot = telebot.TeleBot(bot_token)
