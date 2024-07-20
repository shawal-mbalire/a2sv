import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import seaborn as sns
import matplotlib.pyplot as plt

# Load environment variables from .env file
load_dotenv()

# Database connection parameters from environment variables
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
dbname = os.getenv('DB_NAME')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

# Create the database URL
DATABASE_URL = f'postgresql+pg8000://{user}:{password}@{host}:{port}/{dbname}'

# Create the engine
engine = create_engine(DATABASE_URL)

st.title("Power Usage Analysis and Anomaly Detection")

# Function to fetch data from the database
@st.cache
def fetch_data(query):
    with engine.connect() as connection:
        return pd.read_sql(query, connection)

# Fetch data from the tables
power_values_df = fetch_data("SELECT * FROM power_values")
recent_power_values_df = fetch_data("SELECT * FROM recent_power_values")
anomaly_predictions_df = fetch_data("SELECT * FROM anomaly_predictions")
power_meter_df = fetch_data("SELECT * FROM power_meter")

# Display data overview
st.header("Data Overview")
st.write("Power Values")
st.dataframe(power_values_df.head())

st.write("Recent Power Values")
st.dataframe(recent_power_values_df.head())

st.write("Anomaly Predictions")
st.dataframe(anomaly_predictions_df.head())

# Filter options
st.header("Filter Options")
filter_type = st.radio("Filter by:", ("Location", "User ID"))

if filter_type == "Location":
    region = st.selectbox("Select Region", power_meter_df['region'].unique())
    district = st.selectbox("Select District", power_meter_df[power_meter_df['region'] == region]['district'].unique())
    filtered_users = power_meter_df[(power_meter_df['region'] == region) & (power_meter_df['district'] == district)]['user_id'].unique()
else:
    user_id = st.selectbox("Select User ID", power_meter_df['user_id'].unique())
    filtered_users = [user_id]

# Visualize power usage patterns
st.header("Power Usage Patterns")
st.subheader("Power Values Over Time")

# Plotting power values over time for filtered users
filtered_power_values = power_values_df[power_values_df['user_id'].isin(filtered_users)]
fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(data=filtered_power_values, x='date_logged', y='power_value', hue='user_id', ax=ax)
plt.xticks(rotation=45)
st.pyplot(fig)

# Anomaly Detection Analysis
st.header("Anomaly Detection")
st.subheader("Anomalies Over Time")

# Plotting anomalies over time for filtered users
filtered_anomalies = anomaly_predictions_df[anomaly_predictions_df['user_id'].isin(filtered_users)]
fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(data=filtered_anomalies, x='date_predicted', y='user_id', hue='anomaly', palette={True: 'red', False: 'blue'}, ax=ax)
plt.xticks(rotation=45)
st.pyplot(fig)

st.subheader("Anomaly Summary")
anomaly_summary = filtered_anomalies.groupby('anomaly').size().reset_index(name='counts')
st.bar_chart(anomaly_summary.set_index('anomaly'))

# User-specific Analysis
st.header("User-Specific Analysis")

if filter_type == "User ID":
    user_power_values = power_values_df[power_values_df['user_id'] == user_id]
    user_recent_values = recent_power_values_df[recent_power_values_df['user_id'] == user_id]
    user_anomalies = anomaly_predictions_df[anomaly_predictions_df['user_id'] == user_id]

    st.subheader(f"Power Values for User {user_id}")
    st.line_chart(user_power_values.set_index('date_logged')['power_value'])

    st.subheader(f"Recent Power Values for User {user_id}")
    st.line_chart(user_recent_values.set_index('date_logged')['power_value'])

    st.subheader(f"Anomalies for User {user_id}")
    st.write(user_anomalies)

    if st.button("Show Anomalies Only"):
        st.write(user_anomalies[user_anomalies['anomaly'] == True])

st.write("End of Analysis")
