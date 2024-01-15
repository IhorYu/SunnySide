from datetime import datetime

import pytz
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from decouple import config

from api_integration import bot, client, weather_api_key
from database import create_connection


# Function to get the weather forecast using an external API
def get_weather_forecast(api_key=weather_api_key, location="Steinau an der straße"):
    base_url = "http://api.weatherapi.com/v1/forecast.json"
    # Parameters for the API request
    params = {
        'key': api_key,  # API key
        'q': location,  # Location query
        'days': 2  # Number of days for the forecast
    }

    # Sending a request to the API
    response = requests.get(base_url, params=params)
    # Returning the JSON response
    return response.json()


# Function to display weather information
def display_weather_info(weather_data, date_time):
    # Extracting the forecast date
    forecast_date = date_time.date()
    # Getting the forecast data
    forecast_day = weather_data['forecast']['forecastday']

    # Collecting weather information for morning, day, and evening
    weather_summary = []

    for day in forecast_day:
        if day['date'] == forecast_date.strftime('%Y-%m-%d'):
            hour_forecasts = day['hour']
            for hour_forecast in hour_forecasts:
                forecast_time = datetime.strptime(hour_forecast['time'], '%Y-%m-%d %H:%M')
                # Checking for specific times: morning (9 AM), day (3 PM), and evening (9 PM)
                if forecast_time.hour in [9, 15, 21]:
                    # Extracting relevant weather data
                    temp_c = hour_forecast['temp_c']
                    condition = hour_forecast['condition']['text']
                    wind_speed = hour_forecast['wind_kph']
                    wind_dir = hour_forecast['wind_dir']
                    humidity = hour_forecast['humidity']
                    precip_chance = hour_forecast['chance_of_rain']

                    # Determining the time of day for the forecast
                    time_of_day = "Morning" if forecast_time.hour == 9 else "Day" if forecast_time.hour == 15 else "Evening"
                    # Adding the forecast to the summary
                    weather_summary.append(
                        f"{time_of_day} - Temp: {temp_c}°C, Condition: {condition}, Wind: {wind_speed} kph ({wind_dir}), Humidity: {humidity}%, Chance of Rain: {precip_chance}%")

    # Joining all the weather summaries into one string
    return ' | '.join(weather_summary)


# Requesting the forecast for the current date and time
current_date_time = datetime.now()
weather_data = get_weather_forecast()
# Generating the weather report
weather_report = display_weather_info(weather_data, current_date_time)
print(weather_report)


# Function for showing weather, used in the job scheduler
def show_weather():
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system",
             "content": ""},
            {"role": "user", "content": f"{config('PROMPT_WEATHER')} {weather_report}"}
        ]
    )

    content = completion.choices[0].message.content
    return content


# Function to send daily messages to users
def send_daily_message():
    database = "telegram_users.db"
    conn = create_connection(database)
    content = show_weather()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users")
        rows = cur.fetchall()
        for row in rows:
            try:
                bot.send_message(row[0], content)
            except Exception as e:
                print(f"Error sending message to user {row[0]}: {e}")


scheduler = BackgroundScheduler()
scheduler.configure(timezone=pytz.timezone('Europe/Berlin'))
scheduler.add_job(send_daily_message, 'cron', hour=8, minute=0)
