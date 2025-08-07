import streamlit as st
import joblib
import numpy as np
import pandas as pd
import requests
from datetime import datetime
import json

# --------------------------
# Email Alert Function
# --------------------------
def send_email_alert(subject, message, to_email):
    api_url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": "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",
        "content-type": "application/json"
    }
    payload = {
        "sender": {"name": "Flood Watcher", "email": "safiyabanoansari37740@iisuniv.ac.in"},
        "to": [{"email": "safiyabanoansari36487@iisuniv.ac.in"}],
        "subject": subject,
        "htmlContent": f"<html><body><h3>{subject}</h3><p>{message}</p></body></html>"
    }

    response = requests.post(api_url, headers=headers, data=json.dumps(payload))
    return response.status_code == 201

# --------------------------
# Load Model
# --------------------------
model = joblib.load("model.pkl")

# --------------------------
# UI Setup
# --------------------------
st.set_page_config(page_title="AI Glacier & River Discharge Watcher", page_icon="🧊")
st.title("🧊 AI Glacier & River Discharge Watcher")
st.markdown("Predict river discharge and assess flood risk based on rainfall, temperature, and glacier melt.")

# --------------------------
# Forecast Section
# --------------------------
st.header("📡 3-Day Weather Forecast (Shimla)")
API_KEY = "889329e4474f0830b46f32c2277fcf12"
CITY = "Shimla"
url = f"https://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={API_KEY}&units=metric"

forecast_df = pd.DataFrame()
try:
    response = requests.get(url)
    data = response.json()
    forecast_data = []

    for entry in data['list'][:24]:  # Next 3 days
        dt_txt = entry['dt_txt']
        temp = entry['main']['temp']
        rainfall = entry.get('rain', {}).get('3h', 0)
        forecast_data.append({'datetime': dt_txt, 'temp': temp, 'rainfall': rainfall})

    forecast_df = pd.DataFrame(forecast_data)
    st.dataframe(forecast_df.head(10))

    # Use first forecast value as input
    rainfall_forecast_today = forecast_df.iloc[0]['rainfall']
except:
    st.warning("⚠️ Unable to fetch forecast data. Check your API key or connection.")
    rainfall_forecast_today = st.slider("Forecasted Rainfall Today (mm)", 0, 200, 55)  # fallback

# --------------------------
# User Inputs
# --------------------------
st.header("📥 Enter Current Day Inputs")
temp_today = st.slider("Temperature Today (°C)", 0, 40, 21)
lag1 = st.slider("Rainfall Lag 1 (mm)", 0, 200, 48)
lag2 = st.slider("Rainfall Lag 2 (mm)", 0, 200, 52)
lag3 = st.slider("Rainfall Lag 3 (mm)", 0, 200, 39)
roll3 = st.slider("Rolling 3-Day Rainfall (mm)", 0, 200, 46)
roll7 = st.slider("Rolling 7-Day Rainfall (mm)", 0, 200, 43)

# --------------------------
# Calculations
# --------------------------
glacier_melt = max(0, (temp_today - 10)) * 1.2
effective_input = rainfall_forecast_today + glacier_melt

# Model input order must match training
input_data = np.array([[rainfall_forecast_today, lag1, lag2, lag3, roll3, roll7,
                        effective_input, glacier_melt, temp_today, rainfall_forecast_today]])

# --------------------------
# Prediction
# --------------------------
predicted_discharge = model.predict(input_data)[0]

# --------------------------
# Classification
# --------------------------
def classify_runoff(discharge):
    if discharge > 15000:
        return "Evacuate"
    elif discharge > 8000:
        return "Alert"
    else:
        return "Safe"

status = classify_runoff(predicted_discharge)

# --------------------------
# Email Alert
# --------------------------
email_sent = False
if status in ["Alert", "Evacuate"]:
    subject = f"[{status}] River Discharge Alert - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    message = f"""
    Predicted Discharge: {predicted_discharge:.2f} cusecs<br>
    Glacier Melt: {glacier_melt:.2f} mm<br>
    Effective Input: {effective_input:.2f} mm<br>
    Status: {status}<br>
    """
    email_sent = send_email_alert(subject, message, "safiyabanoansari36487@iisuniv.ac.in")

# --------------------------
# Output Display
# --------------------------
st.markdown(f"### 🌊 Predicted Discharge: `{predicted_discharge:.2f}` cusecs")
if status == "Evacuate":
    st.error("🚨 FLOOD WARNING: Immediate evacuation advised!")
elif status == "Alert":
    st.warning("⚠️ ALERT: Be on standby, potential flooding risk!")
else:
    st.success("✅ SAFE: Discharge within normal range.")

if email_sent:
    st.success("📧 Alert sent to emergency contacts.")
elif status in ["Alert", "Evacuate"]:
    st.warning("⚠️ Could not send alert. Check API key or email setup.")

# --------------------------
# Simulation Details
# --------------------------
with st.expander("📊 See Simulation Details"):
    st.write(f"Forecasted Rainfall Today: `{rainfall_forecast_today:.2f}` mm")
    st.write(f"Glacier Melt: `{glacier_melt:.2f}` mm")
    st.write(f"Effective Water Input: `{effective_input:.2f}` mm")
    st.write(f"Runoff Classification: `{status}`")

# --------------------------
# Alert Info
# --------------------------
st.header("📣 Alert System")
st.markdown("Alerts will be sent to:")
st.markdown("- 🚓 Disaster Management Authority")
st.markdown("- 🚁 Evacuation Teams")
st.markdown("- 🧳 Tourist Agencies")
st.markdown("- 🏥 Emergency Services")
