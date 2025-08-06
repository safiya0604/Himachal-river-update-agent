import streamlit as st
import joblib
import numpy as np

# Load model
model = joblib.load("model.pk1")

st.title("🧊 AI Glacier & River Discharge Watcher")
st.markdown("Predict river discharge and assess flood risk based on rainfall, temperature, and glacier melt.")

# User Inputs
rainfall_today = st.slider("Rainfall Today (mm)", 0, 200, 55)
temp_today = st.slider("Temperature Today (°C)", 0, 40, 21)
lag1 = st.slider("Rainfall Lag 1 (mm)", 0, 200, 48)
lag2 = st.slider("Rainfall Lag 2 (mm)", 0, 200, 52)
lag3 = st.slider("Rainfall Lag 3 (mm)", 0, 200, 39)
roll3 = st.slider("Rolling 3-Day Rainfall (mm)", 0, 200, 46)
roll7 = st.slider("Rolling 7-Day Rainfall (mm)", 0, 200, 43)

# Glacier melt simulation
glacier_melt = max(0, (temp_today - 10)) * 1.2
effective_input = rainfall_today + glacier_melt

# Prediction
input_data = np.array([[rainfall_today, temp_today, glacier_melt, effective_input, lag1, lag2, lag3, roll3, roll7]])
predicted_discharge = model.predict(input_data)[0]

# Display results
st.markdown(f"### 🌊 Predicted Discharge: `{predicted_discharge:.2f}` cusecs")

if predicted_discharge > 15000:
    st.error("🚨 Flood Alert: High river discharge detected!")
else:
    st.success("✅ Safe: Discharge within acceptable range.")

# Debug / show glacier melt
with st.expander("See Simulation Details"):
    st.write(f"📊 Glacier Melt: `{glacier_melt:.2f}` mm")
    st.write(f"💧 Effective Water Input: `{effective_input:.2f}` mm")
