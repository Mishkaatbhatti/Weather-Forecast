import requests
import gradio as gr
from datetime import datetime

# Weather condition codes mapping (simplified)
weather_codes = {
    0: "☀️ Clear sky",
    1: "🌤️ Mainly clear",
    2: "⛅ Partly cloudy",
    3: "☁️ Overcast",
    45: "🌫️ Fog",
    48: "🌫️ Depositing rime fog",
    51: "🌦️ Light drizzle",
    53: "🌦️ Moderate drizzle",
    55: "🌧️ Dense drizzle",
    61: "🌦️ Slight rain",
    63: "🌧️ Moderate rain",
    65: "🌧️ Heavy rain",
    71: "❄️ Slight snow fall",
    73: "❄️ Moderate snow fall",
    75: "❄️ Heavy snow fall",
    95: "⛈️ Thunderstorm",
    99: "⛈️ Thunderstorm with hail"
}

def get_weather(city):
    # Geocoding API to get latitude & longitude
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo_response = requests.get(geo_url).json()

    if "results" not in geo_response:
        return f"❌ City '{city}' not found."

    lat = geo_response["results"][0]["latitude"]
    lon = geo_response["results"][0]["longitude"]

    # Weather API (current + hourly rain)
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current_weather=true&hourly=precipitation"
    )
    weather_response = requests.get(weather_url).json()

    if "current_weather" not in weather_response:
        return "❌ Weather data not available."

    weather = weather_response["current_weather"]
    temperature = weather["temperature"]
    windspeed = weather["windspeed"]
    code = weather["weathercode"]

    condition = weather_codes.get(code, f"Code {code}")

    # Rain prediction (next few hours)
    hourly_times = weather_response["hourly"]["time"]
    hourly_precip = weather_response["hourly"]["precipitation"]

    now = datetime.utcnow().strftime("%Y-%m-%dT%H:00")
    rain_forecast = []
    for t, p in zip(hourly_times, hourly_precip):
        if t >= now and p > 0:
            rain_forecast.append(f"{t}: 🌧️ {p} mm")

    if rain_forecast:
        rain_info = "\n".join(rain_forecast[:5])  # Show next 5 hours
    else:
        rain_info = "No rain expected in the next hours"

    return (
        f" City: {city}\n"
        f" Temperature: {temperature} °C\n"
        f" Windspeed: {windspeed} km/h\n"
        f" Condition: {condition}\n\n"
        f" Rain Forecast (next hours):\n{rain_info}"
    )

# Gradio Interface
iface = gr.Interface(
    fn=get_weather,
    inputs=gr.Textbox(label="Enter City Name"),
    outputs="text",
    title=" Weather Forecast App",
    description="Get current weather and rain prediction using Open-Meteo API.",
)

if __name__ == "__main__":
    iface.launch()
