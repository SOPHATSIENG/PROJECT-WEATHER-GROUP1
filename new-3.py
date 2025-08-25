import os
import requests
from gtts import gTTS
from flask import Flask, render_template_string

app = Flask(__name__)

# --------------------------
# Weather Data
# --------------------------
API_KEY = "a60d8294585352cd1271ad7a5b2b36e4"
CITY = "Battambang"
URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

response = requests.get(URL)
data = response.json()

if response.status_code != 200 or "main" not in data:
    temp = 0
    weather_desc = "No data"
    lat, lon = 0, 0
    humidity = 0
    wind = 0
    icon = "☁️"
else:
    temp = data["main"]["temp"]
    weather_desc = data["weather"][0]["description"]
    lat = data["coord"]["lat"]
    lon = data["coord"]["lon"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]
    icon = "☀️" if "clear" in weather_desc.lower() else "🌧️" if "rain" in weather_desc.lower() else "☁️"

# Messages
if temp is not None:
    if "rain" in weather_desc.lower():
        message_en = f"It's hot today in {CITY}. The temperature is {temp}°C with {weather_desc}."
        message_kh = f"ថ្ងៃនេះមេឃភ្លៀងនៅ{CITY}សីតុណ្ហភាព{temp}°C​​ សូមកុំចេញក្រៅប្រយ័ត្ន{weather_desc}"
    elif temp >= 30:
        message_en = f"It's hot today in {CITY}. The temperature is {temp}°C with {weather_desc}."
        message_kh = f"ថ្ងៃនេះកម្ដៅនៅ{CITY}សីតុណ្ហភាព{temp}°C​​ សូមផឹកទឹកឲ្យបានច្រើនដើម្បីសុខភាពបើមិនផឹកយ័ត្នអ្នកគ្រូដាវីថាឲ្យខ្ញុំគ្រាន់ប្រាប់។ {weather_desc}"
    elif temp <= 20:
        message_en = f"It's cold today in {CITY}. The temperature is {temp}°C with {weather_desc}."
        message_kh = f"ថ្ងៃនេះត្រជាក់ណាស់នៅ {CITY}។ សីតុណ្ហភាព {temp}°C សូមមេតាពាក់អាវឲ្យក្រាស់ផងញុមបារម្មណ៍ពីរសុខភាពរបស់អ្នក ។ {weather_desc}"
    else:
        message_en = f"The weather in {CITY} is moderate. It's {temp}°C with {weather_desc}."
        message_kh = f"ថ្ងៃនេះអាកាសធាតុនៅ {CITY}​ធម្មតា។ សីតុណ្ហភាព {temp}°C អ្នកអាចដើរលេងកម្សាន្ដបានដោយសេរីមិនទើសក្បាលអាណាឡើយកុំខ្វល់អីតាមសប្បាយបើអ្នកណាហ៊ានវៃមកប្រាបើបងផាតបងផាតវៃទាំងអស់។​​​​ {weather_desc}​"
else:
    message_en = "Weather data not available."
    message_kh = "មិនមានទិន្នន័យអាកាសធាតុ។"




    # --------------------------
# Choose background image
# --------------------------
if "clear" in weather_desc.lower():
    bg_url = "https://www.google.com/url?sa=i&url=https%3A%2F%2Feducation.nationalgeographic.org%2Fresource%2Fweather%2F&psig=AOvVaw3zFcutAx3BLmYe4aijExuP&ust=1755766635428000&source=images&cd=vfe&opi=89978449&ved=0CBUQjRxqFwoTCJCN_8iCmY8DFQAAAAAdAAAAABAE"
elif "rain" in weather_desc.lower():
    bg_url = "https://i.ibb.co/S0RJ8Rj/rain-bg.jpg"
elif "cloud" in weather_desc.lower():
    bg_url = "image.png"


elif "storm" in weather_desc.lower() or "thunder" in weather_desc.lower():
    bg_url = "https://i.ibb.co/4dMsh0C/storm-bg.jpg"
else:
    bg_url = "https://i.ibb.co/F8YTGtG/default-bg.jpg"

# --------------------------
# Generate Khmer speech file
# --------------------------
AUDIO_FILE = "static/khmer_weather.mp3"
os.makedirs("static", exist_ok=True)

tts = gTTS(text=message_kh, lang="km")
tts.save(AUDIO_FILE)

# --------------------------
# HTML (Weather Card UI)
# --------------------------
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Weather App UI</title>
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
      background: url("{{ bg_url }}");
    #   color: white;
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
    return render_template_string(
        HTML_PAGE,
        city=CITY,
        message_en=message_en,
        message_kh=message_kh,
        temp=temp,
        weather_desc=weather_desc,
        humidity=humidity,
        wind=wind,
        icon=icon
    )

if __name__ == "__main__":
    app.run(debug=True)
