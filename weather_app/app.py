from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# ✅ Your provided API key
API_KEY = "02a3b3ccd8d3da8c82816a60e9193b40"

# Base API endpoint with placeholders
API_URL = "https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"

@app.route("/", methods=["GET", "POST"])
def home():
    weather = None
    error = None

    if request.method == "POST":
        lat = request.form.get("latitude")
        lon = request.form.get("longitude")

        if not lat or not lon:
            error = "Please enter both latitude and longitude."
        else:
            try:
                # Convert to float to validate inputs
                float(lat)
                float(lon)

                # Construct the full API request URL
                url = API_URL.format(lat=lat, lon=lon, api_key=API_KEY)
                print("Requesting:", url)  # Optional debug print

                # Fetch the data
                response = requests.get(url)
                data = response.json()

                if data.get("cod") != 200:
                    error = data.get("message", "Failed to fetch weather data.")
                else:
                    weather = {
                        "city": data.get("name", "Unknown Location"),
                        "temperature": data["main"]["temp"],
                        "description": data["weather"][0]["description"].title(),
                        "humidity": data["main"]["humidity"],
                        "wind": data["wind"]["speed"]
                    }
            except ValueError:
                error = "Latitude and Longitude must be valid numbers."

    return render_template("index.html", weather=weather, error=error)

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=8080)
