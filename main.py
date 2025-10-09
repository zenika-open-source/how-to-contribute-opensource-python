from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

def geocode_city_country(city, country):
    """
    Geocodes a city and country to latitude and longitude using the Open-Meteo API.
    """
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=10&language=en&format=json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        return None
    except ValueError:
        return None

    if not data.get("results"):
        return None

    for result in data["results"]:
        if result.get("country") == country:
            return {"latitude": result["latitude"], "longitude": result["longitude"]}

    first_result = data["results"][0]
    return {"latitude": first_result["latitude"], "longitude": first_result["longitude"]}

@app.route("/")
def index():
    return jsonify({"message": "Welcome to the PyWeather API!"})

@app.route("/api/weather")
def get_weather():
    city = request.args.get("city")
    country = request.args.get("country")

    if not city or not country:
        return jsonify({"error": "City and country are required"}), 400

    geo = geocode_city_country(city, country)

    if not geo or "latitude" not in geo or "longitude" not in geo:
        return jsonify({"error": "Could not find location. Please try a different city."}), 404

    lat = geo["latitude"]
    lon = geo["longitude"]
    
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    
    try:
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        if "current_weather" not in weather_data:
            return jsonify({"error": "Invalid weather data received from API."}), 500
            
        return jsonify(weather_data["current_weather"])

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch weather data: {e}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
