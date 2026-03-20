import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# ✅ DB Connection with SSL
engine = create_engine(
    st.secrets["DB_URL"],
    connect_args={
        "ssl": {
            "ca": "ca.pem"
        }
    }
)

st.title("🧮 SQL Query Executor")

st.info("Select a predefined query or write your own SQL.")

# ✅ ALL 13 QUERIES
queries = {

    "Select a query": "",

    # -------- literacy_rates --------
    "1. Top 5 countries with highest adult literacy (2020)": """
        SELECT country, adult_literacy_rate
        FROM literacy_rates
        WHERE year = 2020
        ORDER BY adult_literacy_rate DESC
        LIMIT 5;
    """,

    "2. Countries where female youth literacy < 80%": """
        SELECT country, youth_literacy_female
        FROM literacy_rates
        WHERE youth_literacy_female < 80;
    """,

    "3. Global average adult literacy": """
        SELECT AVG(adult_literacy_rate) AS avg_literacy
        FROM literacy_rates;
    """,

    # -------- illiteracy_population --------
    "4. Countries with illiteracy % > 20% in 2000": """
        SELECT country, illiteracy_percent
        FROM illiteracy_population
        WHERE year = 2000
        AND illiteracy_percent > 20;
    """,

    "5. Illiteracy trend for India (2000–2020)": """
        SELECT year, illiteracy_percent
        FROM illiteracy_population
        WHERE country = 'India'
        AND year BETWEEN 2000 AND 2020
        ORDER BY year;
    """,

    "6. Top 10 countries with highest illiteracy (latest year)": """
        SELECT country, illiteracy_percent
        FROM illiteracy_population
        WHERE year = (SELECT MAX(year) FROM illiteracy_population)
        ORDER BY illiteracy_percent DESC
        LIMIT 10;
    """,

    # -------- gdp_schooling --------
    "7. Schooling > 7 and GDP < 5000": """
        SELECT country, avg_years_schooling, gdp_per_capita
        FROM gdp_schooling
        WHERE avg_years_schooling > 7
        AND gdp_per_capita < 5000;
    """,

    "8. Rank countries by GDP per schooling (2020)": """
        SELECT country, gdp_per_schooling_year,
               RANK() OVER (ORDER BY gdp_per_schooling_year DESC) AS rank_position
        FROM gdp_schooling
        WHERE year = 2020;
    """,

    "9. Global average schooling per year": """
        SELECT year, AVG(avg_years_schooling) AS avg_schooling
        FROM gdp_schooling
        GROUP BY year
        ORDER BY year;
    """,

    # -------- JOIN QUERIES --------
    "10. High GDP but low schooling (<6) in 2020": """
        SELECT country, gdp_per_capita, avg_years_schooling
        FROM gdp_schooling
        WHERE year = 2020
        AND avg_years_schooling < 6
        ORDER BY gdp_per_capita DESC
        LIMIT 10;
    """,

    "11. High illiteracy despite high schooling (>10)": """
        SELECT g.country, g.avg_years_schooling, i.illiteracy_percent
        FROM gdp_schooling g
        JOIN illiteracy_population i
        ON g.country = i.country AND g.year = i.year
        WHERE g.avg_years_schooling > 10
        AND i.illiteracy_percent > 10;
    """,

    "12. Literacy vs GDP growth (India - last 20 years)": """
        SELECT l.year,
               l.adult_literacy_rate,
               g.gdp_per_capita
        FROM literacy_rates l
        JOIN gdp_schooling g
        ON l.country = g.country AND l.year = g.year
        WHERE l.country = 'India'
        ORDER BY l.year DESC
        LIMIT 20;
    """,

    "13. Gender gap in high GDP countries (2020)": """
        SELECT l.country,
               l.youth_literacy_male,
               l.youth_literacy_female,
               (l.youth_literacy_male - l.youth_literacy_female) AS gender_gap
        FROM literacy_rates l
        JOIN gdp_schooling g
        ON l.country = g.country AND l.year = g.year
        WHERE g.gdp_per_capita > 30000
        AND l.year = 2020;
    """
}

# Dropdown
selected_query = st.selectbox("Choose a query", list(queries.keys()))

# Text area
query = st.text_area("SQL Query", value=queries[selected_query], height=180)

# Run button
if st.button("Run Query"):
    if query.strip() == "":
        st.warning("Please select or enter a query.")
    else:
        try:
            df = pd.read_sql(query, engine)

            st.success("Query executed successfully!")
            st.dataframe(df)

            # 📊 Visualization
            if len(df.columns) >= 2:
                x_col = df.columns[0]
                y_col = df.columns[1]

                chart_type = st.selectbox(
                    "Choose chart type", ["Bar", "Line", "Scatter"]
                )

                if chart_type == "Bar":
                    fig = px.bar(df, x=x_col, y=y_col)
                elif chart_type == "Line":
                    fig = px.line(df, x=x_col, y=y_col)
                else:
                    fig = px.scatter(df, x=x_col, y=y_col)

                st.plotly_chart(fig)

        except Exception as e:
            st.error(f"Error: {e}")