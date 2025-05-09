# 🌦️ Weather Stylist AI — Final Project

Welcome to "Weather Stylist AI"
A full-stack project that integrates weather forecasting with fashion suggestions using AI and real-time data.

Architecture Overview
The system follows a modular client-server architecture:
•	The Streamlit client app allows users to log in, input a city name, and receive AI-generated outfit suggestions based on real-time weather.
•	It communicates with a RESTful API built using FastAPI.
•	The backend handles user authentication using Supabase, weather data via the OpenWeather API, and fashion recommendations using the Cohere API.
•	Credit deduction is enforced at the backend, where each AI suggestion call reduces the user’s credit count stored in Supabase.


Project Overview

- Backend: FastAPI for RESTful API endpoints
- Frontend: Streamlit web app (client interface)
- Authentication: Supabase Auth
- AI Service: Cohere (for fashion suggestion generation)
- Weather Data: OpenWeatherMap API
- Credit System: Users have limited credits per login/session

---


---

How to Run Locally

1. Clone the Repository
   ```bash
git clone https://github.com/Ugomuanya/weather-stylist.git
cd weather-stylist

2. Set Up the Backend 

cd api
pip install -r requirements.txt
uvicorn main:app --reload

3. Run the Streamlit Client

cd ../client
streamlit run app.py

API Documentation 
Available under the API Docs section in the streamlit app.

AUthentication
This is Handled by Supabase Auth
Login is required to access credit-based weather requests.

Testing 
Automated testing was done using pytest
to run tests

input "Pytest" and run in your cloned terminal 


AI & External API
Cohere is used to generate outfit suggestions 
OpenWeatherMap provides current weatehr data.

Credit System
Each user sessio has a daily limited number of requests.


Author
Name: Ugochukwu Muanya
GitHub:@Ugomuanya


License
This project is used for educational purposes only.








