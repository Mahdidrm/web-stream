import streamlit as st
import pandas as pd
import numpy as np
import time
import altair as alt
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Real-Time Energy Monitor", layout="wide")

SECONDS = 600
np.random.seed(42)

def generate_data(seconds):
    timestamps = pd.date_range(start=pd.Timestamp.now(), periods=seconds, freq='s')
    production = np.random.uniform(50, 100, size=seconds)
    internal_consumption = np.random.uniform(30, 90, size=seconds)
    external_consumers = np.random.uniform(0, 20, size=seconds)

    net_energy = production - internal_consumption - external_consumers
    price_per_kwh = np.clip(0.1 + 0.005 * (internal_consumption + external_consumers - production), 0.05, 0.5)
    cost = np.maximum(internal_consumption + external_consumers - production, 0) * price_per_kwh * 0.92  # Convert to EUR

    return pd.DataFrame({
        "timestamp": timestamps,
        "production": production,
        "internal_consumption": internal_consumption,
        "external_consumers": external_consumers,
        "net_energy": net_energy,
        "price_per_kwh": price_per_kwh,
        "cost_eur": cost
    })

# === 🔮 PREDICTION SECTION START ===
def simulate_price_prediction(df, future_seconds=60):
    X = np.arange(len(df)).reshape(-1, 1)
    y = df['price_per_kwh'].values
    model = LinearRegression().fit(X, y)
    X_future = np.arange(len(df), len(df) + future_seconds).reshape(-1, 1)
    future_prices = model.predict(X_future)
    future_timestamps = pd.date_range(start=df['timestamp'].iloc[-1] + pd.Timedelta(seconds=1), periods=future_seconds, freq='s')
    return pd.DataFrame({"timestamp": future_timestamps, "predicted_price": future_prices})

st.title("🔌 Real-Time Electricity Usage Simulator")
st.markdown("""
This dashboard simulates and visualizes electricity production, consumption, and cost over a 10-minute period.

---
### 👁️ Overview
• Real-time simulation
• Decision score with visual gauge
• Hourly price and prediction
• Clear guidance on usage timing
---
""")

placeholder = st.empty()
data = generate_data(SECONDS)

for i in range(1, SECONDS + 1):
    current_data = data.iloc[:i]
    current_price = current_data['price_per_kwh'].iloc[-1]
    current_cost = current_data['cost_eur'].iloc[-1]

    # User-friendly status message
    if current_price < 0.15:
        status = "✅ Cheap electricity – good time to use power!"
        status_color = "green"
    elif current_price < 0.3:
        status = "⚠ Moderate price – consider waiting."
        status_color = "orange"
    else:
        status = "🚫 Expensive electricity – avoid heavy usage now!"
        status_color = "red"

    # Predict future prices
    future_df = simulate_price_prediction(current_data, future_seconds=60)
# === 🔮 PREDICTION SECTION END ===

    # Estimate average price in 5 minutes (hour of day simulation)
    simulated_hour_data = current_data.copy()
    simulated_hour_data['hour'] = simulated_hour_data['timestamp'].dt.hour
    current_hour = simulated_hour_data['hour'].iloc[-1]
    avg_hourly_price = simulated_hour_data[simulated_hour_data['hour'] == current_hour]['price_per_kwh'].mean() * 0.92  # in EUR

    with placeholder.container():
        
        # 🧠 Decision Score
        decision_score = int(max(0, min(100, (0.5 - current_price) * 250)))
        if decision_score > 75:
            decision_advice = "🟢 Go – Electricity is cheap. Use it now."
        elif decision_score > 40:
            decision_advice = "🟠 Wait – It's not the best moment."
        else:
            decision_advice = "🔴 Stop – High cost. Delay usage if possible."

        st.markdown(f"<h3 style='color:black; text-align:center; margin-top: 1em; margin-bottom: 0.5em;'>{decision_advice}</h3>", unsafe_allow_html=True)
        import plotly.graph_objects as go

        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=decision_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Decision Score", 'font': {'size': 20}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
                'bar': {'color': "#2ECC71" if decision_score > 75 else "#F39C12" if decision_score > 40 else "#E74C3C"},
                'steps': [
                    {'range': [0, 40], 'color': '#FDEDEC'},
                    {'range': [40, 75], 'color': '#FCF3CF'},
                    {'range': [75, 100], 'color': '#E8F8F5'}
                ],
            }
        ))

        st.plotly_chart(gauge_fig, use_container_width=True, key=f"gauge_{i}")
        st.markdown(f"<h4 style='color:gray'>⏳ Based on similar time periods, the average electricity price this hour is estimated at <strong>{avg_hourly_price:.4f} €/kWh</strong>.</h4>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color:{status_color}'>{status}</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Production (kW)", f"{current_data['production'].iloc[-1]:.2f}")
        col2.metric("Current Consumption (kW)", f"{current_data['internal_consumption'].iloc[-1]:.2f}")
        col3.metric("Current Cost (€/s)", f"{current_cost:.4f}")

        # Chart: Production, Consumption, External Consumers
        chart_data = current_data[['timestamp', 'production', 'internal_consumption', 'external_consumers']].melt('timestamp')
        chart = alt.Chart(chart_data).mark_line().encode(
            x='timestamp:T',
            y='value:Q',
            color='variable:N'
        ).properties(title="Electricity Metrics Over Time", height=300)
        with st.expander("⚡ Electricity Production and Usage"):
            st.altair_chart(chart, use_container_width=True)

        # Chart: Net Energy
        with st.expander("📉 Net Energy Chart"):
            st.line_chart(current_data[['net_energy']], use_container_width=True)

        # Chart: Future Price Forecast with bands
        price_band = alt.Chart(future_df).mark_area(opacity=0.3).encode(
            x='timestamp:T',
            y=alt.Y('predicted_price:Q', title='Predicted Price (€/kWh)')
        ).properties(title="Predicted Electricity Price (€/kWh)", height=300)

        line = alt.Chart(future_df).mark_line(color="purple").encode(
            x='timestamp:T',
            y='predicted_price:Q'
        )

        with st.expander("📈 Detailed Forecast Chart"):
            st.altair_chart(price_band + line, use_container_width=True)

        # Display predicted values in a table
        st.subheader("🔮 Next 1-Minute Price Forecast (€/kWh)")
        st.dataframe(future_df.head(10).style.format({"predicted_price": "{:.4f}"}))

        # Hourly Trend Summary
        with st.expander("🕒 Hourly Trend Summary"):
            hourly_avg = current_data.copy()
            hourly_avg['hour'] = hourly_avg['timestamp'].dt.hour
            hourly_summary = hourly_avg.groupby('hour')[['price_per_kwh']].mean().reset_index()
            hourly_summary['price_per_kwh'] = hourly_summary['price_per_kwh'] * 0.92  # convert to EUR
            hourly_chart = alt.Chart(hourly_summary).mark_bar().encode(
                x=alt.X('hour:O', title='Hour of Day'),
                y=alt.Y('price_per_kwh:Q', title='Avg Price (€/kWh)'),
                tooltip=['hour', 'price_per_kwh']
            ).properties(title='Average Price by Hour')
            st.altair_chart(hourly_chart, use_container_width=True)


    time.sleep(1)
