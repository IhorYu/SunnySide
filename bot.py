from api_integration import bot
from handlers import start_handler, message_or_button_pressed, handle_photo

# Handling the '/start' command
bot.message_handler(commands=['start'])(start_handler)

# Handling messages that are not commands
bot.message_handler(func=lambda message: True, content_types=['text'])(message_or_button_pressed)

# Handling photo messages
bot.message_handler(content_types=['photo'])(handle_photo)

# Running the bot in a polling loop
bot.polling()