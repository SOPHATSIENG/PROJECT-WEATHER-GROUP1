import os
import time
import threading
import requests
from datetime import datetime
from gtts import gTTS
from flask import Flask, render_template_string

# --------------------------
# Flask App
# --------------------------
app = Flask(__name__)

# --------------------------
# Weather API
# --------------------------
API_KEY = "a60d8294585352cd1271ad7a5b2b36e4"  # your OpenWeather API key
CITY = "Phnom Penh"
URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

def get_weather():
    response = requests.get(URL)
    data = response.json()

    if response.status_code != 200 or "main" not in data:
        return {
            "temp": 0,
            "weather_desc": "No data",
            "humidity": 0,
            "wind": 0,
            "icon": "☁️",
            "message_en": "Weather data not available.",
            "message_kh": "មិនមានទិន្នន័យអាកាសធាតុ។"
        }

    temp = data["main"]["temp"]
    weather_desc = data["weather"][0]["description"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]

    # Icon selection
    if "clear" in weather_desc.lower():
        icon = "☀️"
    elif "rain" in weather_desc.lower():
        icon = "🌧️"
    else:
        icon = "☁️"

    # Messages
    if "rain" in weather_desc.lower():
        message_en = f"It's raining today in {CITY}. Temperature {temp}°C."
        message_kh = f"ថ្ងៃនេះមានភ្លៀងនៅ {CITY} សីតុណ្ហភាព {temp}°C។ សូមប្រយ័ត្ន!"
    elif temp >= 30:
        message_en = f"It's hot today in {CITY}. {temp}°C with {weather_desc}."
        message_kh = f"ថ្ងៃនេះក្តៅណាស់នៅ {CITY} សីតុណ្ហភាព {temp}°C។ សូមផឹកទឹកច្រើន!"
    elif temp <= 20:
        message_en = f"It's cold today in {CITY}. {temp}°C with {weather_desc}."
        message_kh = f"ថ្ងៃនេះត្រជាក់ណាស់នៅ {CITY}។ សូមពាក់អាវក្រាស់!"
    else:
        message_en = f"The weather in {CITY} is normal. {temp}°C with {weather_desc}."
        message_kh = f"អាកាសធាតុធម្មតា នៅ {CITY}។ សីតុណ្ហភាព {temp}°C។"

    return {
        "temp": temp,
        "weather_desc": weather_desc,
        "humidity": humidity,
        "wind": wind,
        "icon": icon,
        "message_en": message_en,
        "message_kh": message_kh
    }

# --------------------------
# Generate Khmer Speech File
# --------------------------
def generate_audio(message_kh):
    AUDIO_FILE = "static/khmer_weather.mp3"
    os.makedirs("static", exist_ok=True)
    tts = gTTS(text=message_kh, lang="km")
    tts.save(AUDIO_FILE)
    return AUDIO_FILE

# --------------------------
# HTML Page
# --------------------------
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sky Whisper Weather</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
      background: #f3f4f6;
    }
    .weather-card {
      margin-top: 50px;
      width: 800px;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
      background: #fff;
    }
    .weather-header {
      padding: 20px;
      text-align: center;
    }
    .temperature { font-size: 64px; font-weight: bold; margin: 10px 0; }
    .icon { font-size: 48px; }
    .weather-info { padding: 15px; background: #fafafa; }
    .weather-info p { margin: 5px 0; font-size: 16px; }
    .highlight { font-weight: bold; color: #333; }
    .speak-btn {
      margin-top: 10px;
      padding: 8px 15px;
      border: none;
      background: #3b82f6;
      color: white;
      font-size: 14px;
      border-radius: 6px;
      cursor: pointer;
    }
    .speak-btn:hover { background: #2563eb; }
  </style>
</head>
<body>
  <div class="weather-card">
    <div class="weather-header">
      <h2>{{ city }}</h2>
      <div class="temperature">{{ temp }}°C</div>
      <div class="icon">{{ icon }}</div>
      <p>{{ weather_desc }}</p>
    </div>
    <div class="weather-info">
      <p><b>English:</b> {{ message_en }}</p>
      <p><b>Khmer:</b> <span id="khmer-msg">{{ message_kh }}</span></p>
      
      <!-- Khmer speech -->
      <audio id="khmerAudio" src="/static/khmer_weather.mp3"></audio>
      <button class="speak-btn" onclick="document.getElementById('khmerAudio').play()">🔊 Speak Khmer</button>

      <p>💧 Humidity: <span class="highlight">{{ humidity }}%</span></p>
      <p>💨 Wind: <span class="highlight">{{ wind }} km/h</span></p>
    </div>
  </div>
</body>
</html>
"""

@app.route("/")
def home():
    weather = get_weather()
    generate_audio(weather["message_kh"])
    return render_template_string(
        HTML_PAGE,
        city=CITY,
        **weather
    )

# --------------------------
# Sky Whisper Auto Reminder (3 times per day)
# --------------------------
def sky_whisper_task():
    reminder_times = [(8, 0), (12, 0), (18, 0)]  # 08:00, 12:00, 18:00
    spoken_today = set()
    print("Sky Whisper is running... Waiting for:", reminder_times)

    while True:
        now = datetime.now()
        current_time = (now.hour, now.minute)

        # Reset at midnight
        if now.hour == 0 and now.minute == 0:
            spoken_today.clear()

        if current_time in reminder_times and current_time not in spoken_today:
            weather = get_weather()
            audio_file = generate_audio(weather["message_kh"])

            # Play audio
            os.system(f"start {audio_file}")   # Windows
            # os.system(f"afplay {audio_file}") # Mac
            # os.system(f"mpg123 {audio_file}") # Linux

            print(f"Sky Whisper spoke at {now.strftime('%H:%M')}!")
            spoken_today.add(current_time)
            time.sleep(60)

        time.sleep(1)

# Run Sky Whisper in background
threading.Thread(target=sky_whisper_task, daemon=True).start()

# --------------------------
# Start Flask app
# --------------------------
if __name__ == "__main__":
    app.run(debug=True)
