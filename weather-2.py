import os
import requests
import pyttsx3
from gtts import gTTS
from playsound import playsound
from flask import Flask, render_template_string
import schedule
import time
import threading
from datetime import datetime

# --------------------------
# Khmer speaking function
# --------------------------
def find_khmer_voice(engine):
    """Find Khmer voice ID for pyttsx3, if available."""
    for v in engine.getProperty('voices'):
        langs = []
        try:
            langs = [l.decode('utf-8') for l in getattr(v, 'languages', [])]
        except Exception:
            langs = getattr(v, 'languages', []) or []
        lang_text = " ".join(langs).lower()
        name = (getattr(v, 'name', '') or '').lower()
        vid = (getattr(v, 'id', '') or '').lower()

        if ('km' in lang_text) or ('khmer' in name) or ('km-kh' in name) or ('km-kh' in vid):
            return v.id
    return None

def speak_kh(text_kh: str):
    """Speak Khmer: try pyttsx3 Khmer voice, else gTTS."""
    try:
        engine = pyttsx3.init()
        kh_voice_id = find_khmer_voice(engine)
        if kh_voice_id:
            engine.setProperty('voice', kh_voice_id)
            rate = engine.getProperty('rate')
            engine.setProperty('rate', int(rate * 0.9))
            engine.say(text_kh)
            engine.runAndWait()
            return
    except Exception:
        pass

    # Fall back to gTTS
    tts = gTTS(text=text_kh, lang='km')
    fname = 'khmer_tts.mp3'
    tts.save(fname)
    try:
        playsound(fname)
    finally:
        try:
            os.remove(fname)
        except OSError:
            pass

# --------------------------
# Weather and Forecast
# --------------------------
API_KEY = 'a60d8294585352cd1271ad7a5b2b36e4'
CITY = 'battambang'
URL = f'https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric'
FORECAST_URL = f'https://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={API_KEY}&units=metric'

# Global values (for Flask page)
temp = None
weather_desc = ''
lat, lon = 0, 0
message_en = ''
message_kh = ''

def check_weather():
    global temp, weather_desc, lat, lon, message_en, message_kh
    response = requests.get(URL)
    data = response.json()

    if response.status_code != 200 or 'main' not in data:
        print("Error fetching weather data:", data.get('message', 'Unknown error'))
        temp = None
        weather_desc = ''
        lat, lon = 0, 0
        message_en = "Weather data not available."
        message_kh = "មិនមានទិន្នន័យអាកាសធាតុ។"
        return

    temp = data['main']['temp']
    weather_desc = data['weather'][0]['description']
    lat = data['coord']['lat']
    lon = data['coord']['lon']

    # Build messages
    if temp >= 30:
        message_en = f"It's hot today in {CITY}. The temperature is {temp}°C with {weather_desc}."
        message_kh = f"ថ្ងៃនេះកម្ដៅនៅ{CITY}សីតុណ្ហភាព{temp}°C។ សូមផឹកទឹកឲ្យបានច្រើនដើម្បីសុខភាព។ {weather_desc}"
    elif temp <= 20:
        message_en = f"It's cold today in {CITY}. The temperature is {temp}°C with {weather_desc}."
        message_kh = f"ថ្ងៃនេះត្រជាក់ណាស់នៅ {CITY}។ សីតុណ្ហភាព {temp}°C សូមពាក់អាវឲ្យក្រាស់។ {weather_desc}"
    else:
        message_en = f"The weather in {CITY} is moderate. It's {temp}°C with {weather_desc}."
        message_kh = f"ថ្ងៃនេះអាកាសធាតុនៅ {CITY} ធម្មតា។ សីតុណ្ហភាព {temp}°C អ្នកអាចដើរលេងកម្សាន្ដបាន។ {weather_desc}"

    # Speak Khmer message
    print(datetime.now(), ">>>", message_en)
    print(message_kh)
    speak_kh(message_kh)

def rain_alert():
    response = requests.get(FORECAST_URL).json()
    if "list" not in response:
        return

    for item in response["list"][:2]:  # check next ~6 hours
        weather_desc = item["weather"][0]["description"].lower()
        forecast_time = item["dt_txt"]

        if "rain" in weather_desc:
            alert_msg = "មានភ្លៀងនឹងធ្លាក់ក្នុងរយៈពេល ១០ នាទីទៀត។ សូមប្រយ័ត្ន។"
            print("Rain Alert >>>", forecast_time, weather_desc)
            speak_kh(alert_msg)
            break

# --------------------------
# Flask web page
# --------------------------
app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Weather in {{ city }}</title>
    <meta charset="utf-8"/>
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
    <style>
        #map { height: 400px; }
        body { font-family: Arial, sans-serif; padding: 20px; }
    </style>
</head>
<body>
    <h1>Weather in {{ city }}</h1>
    <p><b>English:</b> {{ message_en }}</p>
    <p><b>Khmer:</b> {{ message_kh }}</p>
    <div id="map"></div>
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <script>
        var map = L.map('map').setView([{{ lat }}, {{ lon }}], 12);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        L.marker([{{ lat }}, {{ lon }}]).addTo(map)
            .bindPopup('{{ city }}: {{ temp }}°C, {{ weather_desc }}')
            .openPopup();
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(
        HTML_PAGE,
        city=CITY,
        message_en=message_en,
        message_kh=message_kh,
        temp=temp,
        weather_desc=weather_desc,
        lat=lat,
        lon=lon
    )

# --------------------------
# Scheduler setup
# --------------------------
def schedule_runner():
    # Run initial check
    check_weather()
    rain_alert()
    while True:
        schedule.run_pending()
        time.sleep(30)

# Schedule jobs
schedule.every().day.at("07:00").do(check_weather)
schedule.every().day.at("12:00").do(check_weather)
schedule.every().day.at("16:20").do(check_weather)
schedule.every(10).minutes.do(rain_alert)

# Start scheduler in background thread
threading.Thread(target=schedule_runner, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)
