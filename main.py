from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

proxies = {"https": "http://localhost:8088"}

def geocode_city_country(city, country):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=10&language=en&format=json"
    response = requests.get(url, proxies = proxies, verify=False)
    if not response.ok:
        return None
    data = response.json()
    if not data.get("results"):
        return None
    
    result = next((r for r in data["results"] if r.get("country") == country), None)
    
    if result:
        return {"latitude": result["latitude"], "longitude": result["longitude"]}
    
    if data["results"]:
        first_result = data["results"][0]
        return {"latitude": first_result["latitude"], "longitude": first_result["longitude"]}
    
    return None

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
        weather_response = requests.get(weather_url, proxies=proxies, verify=False)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        if "current_weather" not in weather_data:
            return jsonify({"error": "Invalid weather data received from API."}), 500
            
        return jsonify(weather_data["current_weather"])

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch weather data: {e}"}), 500

if __name__ == "__main__":
    app.run(port=8080)
