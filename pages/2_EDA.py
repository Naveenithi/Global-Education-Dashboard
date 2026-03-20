import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# ✅ DB Connection with SSL
engine = create_engine(
    st.secrets["DB_URL"],
    connect_args={
        "ssl": {
            "ca": "ca.pem"
        }
    }
)

st.title("📊 EDA Visualizations")

try:
    df = pd.read_sql("SELECT * FROM literacy_rates", engine)

    st.write("Dataset Preview")
    st.dataframe(df.head())

    x_axis = st.selectbox("Select X-axis", df.columns)
    y_axis = st.selectbox("Select Y-axis", df.columns)

    chart_type = st.selectbox("Chart Type", ["Line", "Bar", "Scatter"])

    if chart_type == "Line":
        fig = px.line(df, x=x_axis, y=y_axis)
    elif chart_type == "Bar":
        fig = px.bar(df, x=x_axis, y=y_axis)
    else:
        fig = px.scatter(df, x=x_axis, y=y_axis)

    st.plotly_chart(fig)

except Exception as e:
    st.error(f"Error: {e}")