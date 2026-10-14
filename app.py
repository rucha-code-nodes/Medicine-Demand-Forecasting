import streamlit as st
import pandas as pd
import pickle

# 1. Load the trained model and lookup data
@st.cache_resource
def load_resources():
    with open('medicine_demand_model.pkl', 'rb') as f:
        model = pickle.load(f)

    df_lookup = pd.read_pickle('monthly_demand_lookup.pkl')
    return model, df_lookup

model, df_lookup = load_resources()

st.title("💊 Medicine Demand Forecasting System")
st.write("Predict monthly medicine requirements for clinics based on historical consumption.")

# 2. User Selection Dropdowns
clinics = df_lookup['Clinic'].unique().tolist()
selected_clinic = st.selectbox("Select Clinic", clinics)

# Filter medicines available for that clinic
medicines = df_lookup[df_lookup['Clinic'] == selected_clinic]['Medicine'].unique().tolist()
selected_medicine = st.selectbox("Select Medicine / Bundle", medicines)

# Select target month (1 to 12)
target_month = st.slider("Select Target Month (1=Jan, 12=Dec)", min_value=1, max_value=12, value=6)

# 3. Automatically fetch the latest available lag data for this clinic & medicine
record = df_lookup[(df_lookup['Clinic'] == selected_clinic) & (df_lookup['Medicine'] == selected_medicine)]

if not record.empty:
    # Get the most recent lag values from the dataset
    latest_row = record.iloc[-1]
    lag_1 = latest_row['lag_1']
    lag_2 = latest_row['lag_2']

    st.write(f"---")
    st.write(f"**Historical Context Found:**")
    st.write(f"- Demand last month (`lag_1`): {lag_1} units")
    st.write(f"- Demand two months ago (`lag_2`): {lag_2} units")

    # 4. Predict Button
    if st.button("Generate Forecast"):
        user_input = pd.DataFrame([[lag_1, lag_2, target_month]], columns=['lag_1', 'lag_2', 'month'])
        prediction = model.predict(user_input)[0]
        final_prediction = max(0, round(prediction))

        st.success(f"📦 Predicted Demand for Next Month: **{final_prediction} units**")
else:
    st.warning("No historical data found for this specific combination.")
