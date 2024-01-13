from telebot import types

from api_integration import bot, client, bot_token
from utils import show_weather

button_text = '4'


def start_handler(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    button = types.KeyboardButton(button_text)
    markup.add(button)
    bot.send_message(message.chat.id, "Добро пожаловать! Нажмите на кнопку ниже.", reply_markup=markup)


def message_or_button_pressed(message):
    # Check if the message text is the same as the button text
    if message.text == button_text:
        # Respond that the button was pressed
        # bot.send_message(message.chat.id, "Вы нажали кнопку!")
        show_weather(message)
    else:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": ""},
                {"role": "user", "content": f"{message.text}"}
            ]
        )

        content = completion.choices[0].message.content
        bot.send_message(message.chat.id, content)


def handle_photo(message):
    # Getting the photo ID of the largest size photo
    photo_id = message.photo[-1].file_id

    # Getting file info
    file_info = bot.get_file(photo_id)

    # Forming the URL to access the photo
    photo_url = f"https://api.telegram.org/file/bot{bot_token}/{file_info.file_path}"

    # Check if there's caption text with the photo
    if message.caption:

        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {f"type": "text", "text": f"{message.caption}"},
                        {
                            "type": "image_url",
                            "image_url": {
                                f"url": f"{photo_url}",
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,

        )

        content = response.choices[0].message.content
        response_text = f"{content}"

    else:
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {f"type": "text", "text": "Что на картинке?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                f"url": f"{photo_url}",
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )

        content = response.choices[0].message.content
        response_text = f"{content}"

    bot.send_message(message.chat.id, response_text)
