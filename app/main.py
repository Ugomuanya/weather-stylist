import os
import requests
import stripe
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# API Keys
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

stripe.api_key = STRIPE_SECRET_KEY

# Routes

@app.get("/")
def welcome():
    return {"message": "🌤️ Hello from Weather App (OpenWeather version)!"}

@app.get("/weather")
def get_weather(city: str = "London"):
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(weather_url)
    data = response.json()

    if data.get("cod") != 200:
        return {"error": "Could not fetch weather. Check city name."}

    temp_c = data["main"]["temp"]
    condition = data["weather"][0]["description"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]

    return {
        "city": city,
        "temperature": f"{temp_c}°C",
        "feels_like": f"{feels_like}°C",
        "condition": condition,
        "humidity": f"{humidity}%",
        "wind_speed": f"{wind_speed} m/s"
    }

@app.post("/create-checkout-session")
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Weather App Credits (10 credits)"
                    },
                    "unit_amount": 500,  # $5.00 = 500 cents
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="http://localhost:8501",
            cancel_url="http://localhost:8501",
        )
        return JSONResponse(content={"checkout_url": session.url})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
