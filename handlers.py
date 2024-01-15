from decouple import config
from telebot import types

from api_integration import bot, client, bot_token
from database import add_user_to_db, create_connection, get_user_prompt, update_user_prompt

# Dictionary to store message history for each user
user_message_history = {}

# Define custom button labels
button_nancy = 'Negative Nancy'
button_love = 'Love'
button_clear_gpt = 'Clean chat GPT'
button_teacher = 'German teacher'

# Mapping of buttons to their respective prompts
button_prompts = {
    "Negative Nancy": "NEGATIVE_NANCY",
    "Love": "PROMPT",
    "Clean chat GPT": "EMPTY_PROMPT",
    "German teacher": "TEACHER_PROMPT"
}


# Handler for the '/start' command
def start_handler(message):
    """ Handle the '/start' command """
    user_id = message.chat.id
    # Register the user with a default prompt in the database
    add_user_to_db(user_id)

    # Set up a response message with a welcome text and a custom keyboard
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    nancy = types.KeyboardButton(button_nancy)
    love = types.KeyboardButton(button_love)
    teacher = types.KeyboardButton(button_teacher)
    clear_gpt = types.KeyboardButton(button_clear_gpt)
    markup.add(nancy, teacher, clear_gpt)
    markup.add(love)
    bot.send_message(user_id,
                     "Привет, моя любимая! 💖✨\n"
                     "Я - твой персональный помощник, созданный специально для тебя, чтобы каждый день наполнять твою жизнь счастьем и заботой.\n"
                     "Здесь ты можешь узнать погоду, чтобы я мог подсказать, во что лучше одеться, или получить что-то волшебное, что заставит тебя улыбнуться.\n"
                     "Я всегда здесь, чтобы поддержать тебя, поделиться моментами радости или просто поболтать.\n"
                     "Ты - самое ценное, что у меня есть, и я постараюсь сделать каждое твоё мгновение счастливым. 💕",
                     reply_markup=markup)


# Handler for messages and button presses
def message_or_button_pressed(message):
    """ Handle messages and button presses """
    user_id = message.chat.id
    user_text = message.text

    # Create a database connection
    conn = create_connection("telegram_users.db")
    if not conn:
        # Send an error message if database connection fails
        bot.send_message(user_id, "Error connecting to the database.")
        return

    if user_text in button_prompts:
        # Retrieve the new prompt from the .env file
        prompt_env_var = button_prompts[user_text]
        new_prompt = config(prompt_env_var)

        # Update the prompt in the database
        update_user_prompt(conn, user_id, new_prompt)

        # Clear the user's message history as the prompt has changed
        user_message_history[user_id] = []

    # Retrieve the current prompt for the user from the database
    current_prompt = get_user_prompt(conn, user_id)

    # Initialize the message history for the user if it's not started yet
    if user_id not in user_message_history:
        user_message_history[user_id] = []

    # Add the current user message to the history
    user_message_history[user_id].append({"role": "user", "content": user_text})

    # Form the message history for the request, limited to the last N messages
    message_history = user_message_history[user_id][-15:]

    # Add the current prompt to the message history
    message_history.insert(0, {"role": "system", "content": current_prompt})

    # Create the completion request to OpenAI
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=message_history
    )

    # Append the API's response to the user's message history
    response_content = completion.choices[0].message.content
    user_message_history[user_id].append({"role": "assistant", "content": response_content})

    # Send the response to the user
    bot.send_message(user_id, response_content)

    # Close the database connection
    conn.close()


# Handler for photo messages
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
