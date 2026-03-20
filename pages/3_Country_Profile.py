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

st.title("🌍 Country Profile")

try:
    countries = pd.read_sql("SELECT DISTINCT country FROM literacy_rates", engine)
    country = st.selectbox("Select Country", countries['country'])

    query = f"""
    SELECT l.year,
           l.adult_literacy_rate,
           l.youth_literacy_avg,
           g.gdp_per_capita,
           g.avg_years_schooling
    FROM literacy_rates l
    JOIN gdp_schooling g
    ON l.country = g.country AND l.year = g.year
    WHERE l.country = '{country}'
    ORDER BY l.year
    """

    df = pd.read_sql(query, engine)

    st.subheader(f"{country} Overview")

    fig1 = px.line(df, x='year', y='adult_literacy_rate', title="Adult Literacy")
    fig2 = px.line(df, x='year', y='gdp_per_capita', title="GDP per Capita")

    st.plotly_chart(fig1)
    st.plotly_chart(fig2)

    st.dataframe(df)

except Exception as e:
    st.error(f"Error: {e}")