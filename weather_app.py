import streamlit as st
import requests
import cohere
import os
import base64
from auth_config import supabase
from datetime import datetime, timedelta
from dotenv import load_dotenv
from streamlit_lottie import st_lottie

# Load environment variables
load_dotenv()
co = cohere.Client(os.getenv("COHERE_API_KEY"))

# Set Streamlit page config
st.set_page_config(page_title="Weather Stylist ☀️", page_icon="🌈", layout="centered")

# Initialize session states
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "proceed_to_weather" not in st.session_state:
    st.session_state["proceed_to_weather"] = False
if "credits" not in st.session_state:
    st.session_state["credits"] = 3
if "last_reset" not in st.session_state:
    st.session_state["last_reset"] = datetime.now().isoformat()
if "weather_data" not in st.session_state:
    st.session_state["weather_data"] = None
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

# Reset credits every 24 hours
last_reset_time = datetime.fromisoformat(st.session_state["last_reset"])
if datetime.now() - last_reset_time >= timedelta(hours=24):
    st.session_state["credits"] = 3
    st.session_state["last_reset"] = datetime.now().isoformat()

# Sidebar Settings
st.sidebar.title("⚙️ Settings")
st.session_state["dark_mode"] = st.sidebar.toggle("🌑 Dark Mode", value=st.session_state["dark_mode"])

# PDF Download (sidebar)
pdf_file = "api_design.pdf"
if os.path.exists(pdf_file):
    with open(pdf_file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    st.sidebar.download_button(
        label="📥 Download API Design PDF",
        data=base64.b64decode(base64_pdf),
        file_name="API_Design.pdf",
        mime="application/pdf"
    )

# Apply Theme
if st.session_state["dark_mode"]:
    st.markdown("""
    <style>
    body, .stApp {
        background-color: #0e1117;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    body {
      background: linear-gradient(-45deg, #74ebd5, #ACB6E5, #ff9a9e, #fad0c4);
      background-size: 400% 400%;
      animation: gradientBG 15s ease infinite;
    }
    @keyframes gradientBG {
      0% {background-position: 0% 50%;}
      50% {background-position: 100% 50%;}
      100% {background-position: 0% 50%;}
    }
    </style>
    """, unsafe_allow_html=True)

# Lottie Animation
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_weather = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_x62chJ.json")

# Outfit Suggestion using Cohere
def ask_ai(prompt):
    try:
        response = co.generate(
            model='command-light',
            prompt=prompt,
            max_tokens=100
        )
        return response.generations[0].text.strip()
    except Exception as e:
        return f"⚠️ AI error: {e}"

def simple_outfit(weather_data):
    temp = float(weather_data["temperature"].replace("°C", "").strip())
    if temp > 25:
        return "🍛 T-shirt and shorts!"
    elif temp > 15:
        return "👕 Light jacket and jeans!"
    else:
        return "🧕 Warm coat and boots!"

# Header UI
st_lottie(lottie_weather, height=200, key="weather_lottie")
st.markdown("## 👗 AI Weather Stylist")
st.markdown("### 🌦️ Weather updates with AI outfit suggestions")
st.divider()

# --- AUTH FLOW ---
if not st.session_state["authenticated"]:
    st.markdown("### 🔐 Login or Signup")
    auth_mode = st.radio("", ("Login", "Signup"), horizontal=True)
    email = st.text_input("📧 Email")
    password = st.text_input("🔒 Password", type="password")
    if st.button(f"🚪 {auth_mode}"):
        try:
            if auth_mode == "Login":
                user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            else:
                user = supabase.auth.sign_up({"email": email, "password": password})
            st.session_state["user"] = user
            st.session_state["authenticated"] = True
            st.success(f"{auth_mode} successful! 🎉")
        except Exception as e:
            st.error(f"{auth_mode} failed: {e}")

# --- POST LOGIN ---
if st.session_state["authenticated"] and not st.session_state["proceed_to_weather"]:
    user_email = st.session_state["user"].user.email
    st.success(f"Welcome, **{user_email}**! 🎈")
    if st.button("👉 Proceed to Weather Checker"):
        st.session_state["proceed_to_weather"] = True

# --- MAIN APP ---
if st.session_state["authenticated"] and st.session_state["proceed_to_weather"]:
    st.divider()
    st.subheader("👤 Profile & Weather Tools")

    with st.expander("👤 View Profile"):
        user_email = st.session_state["user"].user.email
        credits = st.session_state["credits"]
        registration_date = st.session_state["user"].user.created_at.split('T')[0] if "created_at" in st.session_state["user"].user else "Unknown"
        st.markdown(f"**📧 Email:** `{user_email}`")
        st.markdown(f"**💳 Credits Remaining:** `{credits}`")
        st.markdown(f"**📅 Registration Date:** `{registration_date}`")

        st.markdown("#### 🔒 Change Password")
        new_password = st.text_input("Enter new password", type="password")
        confirm_password = st.text_input("Confirm new password", type="password")
        if st.button("✅ Update Password"):
            if new_password != confirm_password:
                st.error("❌ Passwords do not match.")
            elif len(new_password) < 6:
                st.error("❌ Password must be at least 6 characters.")
            else:
                try:
                    supabase.auth.update_user({"password": new_password})
                    st.success("✅ Password updated successfully!")
                except Exception as e:
                    st.error(f"❌ Error updating password: {e}")

        st.divider()
        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.success("Logged out successfully! 👋")
            st.experimental_rerun()

        st.markdown("#### 🗑️ Delete My Account")
        confirm = st.text_input("Type DELETE to confirm account deletion")
        if st.button("⚠️ Confirm Delete Account"):
            if confirm == "DELETE":
                try:
                    supabase.auth.delete_user()
                    st.session_state.clear()
                    st.success("🗑️ Account deleted successfully.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ Error deleting account: {e}")
            else:
                st.error("❌ You must type DELETE exactly to confirm.")

    st.divider()
    st.subheader("📍 Check Weather")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"💳 **Remaining Credits:** `{st.session_state['credits']}` / 3")
    with col2:
        next_reset = datetime.fromisoformat(st.session_state["last_reset"]) + timedelta(hours=24)
        time_remaining = next_reset - datetime.now()
        hours, remainder = divmod(int(time_remaining.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        st.caption(f"⏳ **Credits reset in:** {hours}h {minutes}m {seconds}s")

    city = st.text_input("🏙️ City", "London").strip().title()

    if st.button("🌤️ Check Weather", disabled=st.session_state["credits"] <= 0):
        if st.session_state["credits"] > 0:
            try:
                response = requests.get(f"http://localhost:8000/weather?city={city}")
                data = response.json()

                if "error" in data:
                    st.error(data["error"])
                else:
                    st.session_state["weather_data"] = data
                    st.session_state["credits"] -= 1
                    st.success(f"✅ Weather fetched for {city}")

            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("🛘 Out of credits.")

    if st.session_state["credits"] <= 0:
        st.markdown("### 💳 Buy More Credits")
        if st.button("🏦 Buy 10 Credits ($5) via Bank Transfer"):
            st.info("""
            ### 🏦 Bank Transfer Instructions:
            - **Bank Name:** XYZ Bank
            - **Account Name:** Weather AI Stylist
            - **Account Number:** 123456789
            - **Amount:** $5
            - **Reference:** Your Email Address

            After payment, send a confirmation email to **admin@yourapp.com** with your email address and transaction receipt.
            Credits will be added within 1 hour. 🚀
            """)

    if st.session_state.get("weather_data"):
        data = st.session_state["weather_data"]

        st.metric("🌡️ Temperature", data["temperature"])
        st.metric("💧 Humidity", data["humidity"])
        st.metric("💨 Wind Speed", data["wind_speed"])
        st.write(f"🌥️ Condition: **{data['condition']}**")

        simple = simple_outfit(data)
        st.markdown(f"👕 **Simple Outfit Suggestion:** _{simple}_")

        st.divider()
        st.markdown("### 🧐 Ask AI for more outfit ideas")

        custom_question = st.text_input("💬 Enter your question for AI (optional)")

        if st.button("🧐 Get AI Suggestion"):
            if custom_question.strip():
                weather_context = f"Current weather: {data['condition']}, {data['temperature']}. Suggest outfits."
                final_prompt = f"{weather_context}\n\nUser question: {custom_question}"
                ai_response = ask_ai(final_prompt)
                st.markdown(f"👗 **AI Suggestion:** _{ai_response}_")
            else:
                st.warning("Please enter a question to ask the AI!")
