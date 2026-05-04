import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="AI Patent Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    df = pd.read_csv("aipd_sample.csv")
    df["pub_dt"] = pd.to_datetime(df["pub_dt"], errors="coerce")

    score_map = {
        "Machine Learning": "ai_score_ml",
        "Evolutionary Comp.": "ai_score_evo",
        "NLP": "ai_score_nlp",
        "Speech Recognition": "ai_score_speech",
        "Computer Vision": "ai_score_vision",
        "Planning & Control": "ai_score_planning",
        "Knowledge Rep.": "ai_score_kr",
        "AI Hardware": "ai_score_hardware"
    }

    def get_dominant_score(row):
        cat = row["dominant_category"]
        col = score_map.get(cat)
        if col in row.index:
            return row[col]
        return None

    df["dominant_score"] = df.apply(get_dominant_score, axis=1)
    return df


df = load_data()

st.title("AI Patent Intelligence Dashboard")
st.markdown(
    """
    This Streamlit app analyzes a trimmed sample of USPTO AI patent records to support
    business intelligence around AI innovation trends, technology focus areas, and
    the evolution of the AI patent landscape.
    """
)

st.sidebar.header("Dashboard Filters")

year_min = int(df["year"].min())
year_max = int(df["year"].max())

selected_years = st.sidebar.slider(
    "Year range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max)
)

all_categories = sorted(df["dominant_category"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Dominant AI categories",
    options=all_categories,
    default=all_categories
)

filtered_df = df[
    (df["year"] >= selected_years[0]) &
    (df["year"] <= selected_years[1]) &
    (df["dominant_category"].isin(selected_categories))
].copy()

overview_tab, rq1_tab, rq2_tab, methods_tab = st.tabs(
    ["Overview", "RQ1: Temporal Trends", "RQ2: Domain Distribution", "Methods"]
)

with overview_tab:
    st.subheader("Project Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Records", f"{len(filtered_df):,}")
    c2.metric("Years Covered", f"{filtered_df['year'].min()}–{filtered_df['year'].max()}")
    c3.metric("AI Categories", f"{filtered_df['dominant_category'].nunique()}")
    c4.metric("Avg. Dominant Score", f"{filtered_df['dominant_score'].mean():.3f}")

    st.markdown(
        """
        **Business Problem:** Organizations need better visibility into AI-related intellectual property trends
        to support strategic IP planning, competitive intelligence, and technology monitoring.

        **Analytical Focus:** This prototype emphasizes descriptive analytics using publication year,
        dominant AI category, and model-based AI classification scores.
        """
    )

    st.subheader("Records by Dominant Category")
    category_counts = (
        filtered_df["dominant_category"]
        .value_counts()
        .reset_index()
    )
    category_counts.columns = ["dominant_category", "count"]

    fig_overview = px.bar(
        category_counts,
        x="dominant_category",
        y="count",
        color="dominant_category",
        title="Patent Records by Dominant AI Category"
    )
    fig_overview.update_layout(showlegend=False, xaxis_title="", yaxis_title="Patent count")
    st.plotly_chart(fig_overview, use_container_width=True)

    st.subheader("Sample Records")
    st.dataframe(
        filtered_df[[
            "doc_id", "pub_dt", "year", "dominant_category", "dominant_score"
        ]].head(100),
        use_container_width=True
    )

with rq1_tab:
    st.subheader("RQ1: How did AI patent activity evolve over time?")

    yearly_counts = (
        filtered_df.groupby("year")
        .size()
        .reset_index(name="patent_count")
        .sort_values("year")
    )

    fig_rq1 = px.line(
        yearly_counts,
        x="year",
        y="patent_count",
        markers=True,
        title="AI Patent Filings by Year"
    )
    fig_rq1.update_layout(xaxis_title="Year", yaxis_title="Patent count")
    st.plotly_chart(fig_rq1, use_container_width=True)

    if len(yearly_counts) > 1:
        yearly_counts["pct_change"] = yearly_counts["patent_count"].pct_change() * 100
        st.subheader("Year-over-Year Change")
        st.dataframe(yearly_counts, use_container_width=True)

    st.markdown(
        """
        This view supports temporal trend analysis by showing how AI-related patent records changed
        over the sample period. In the full project, this would be extended to the broader 1976–2023 timeline.
        """
    )

with rq2_tab:
    st.subheader("RQ2: What is the distribution of AI patents across technology domains?")

    domain_counts = (
        filtered_df.groupby("dominant_category")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    fig_rq2_bar = px.bar(
        domain_counts,
        x="dominant_category",
        y="count",
        color="dominant_category",
        title="Distribution by Dominant AI Category"
    )
    fig_rq2_bar.update_layout(showlegend=False, xaxis_title="", yaxis_title="Patent count")
    st.plotly_chart(fig_rq2_bar, use_container_width=True)

    st.subheader("Category Trends Over Time")
    category_trends = (
        filtered_df.groupby(["year", "dominant_category"])
        .size()
        .reset_index(name="count")
        .sort_values(["year", "dominant_category"])
    )

    fig_rq2_line = px.line(
        category_trends,
        x="year",
        y="count",
        color="dominant_category",
        markers=True,
        title="Dominant AI Categories by Year"
    )
    fig_rq2_line.update_layout(xaxis_title="Year", yaxis_title="Patent count")
    st.plotly_chart(fig_rq2_line, use_container_width=True)

    st.subheader("Average Confidence by Dominant Category")
    avg_scores = (
        filtered_df.groupby("dominant_category")["dominant_score"]
        .mean()
        .reset_index()
        .sort_values("dominant_score", ascending=False)
    )

    fig_scores = px.bar(
        avg_scores,
        x="dominant_category",
        y="dominant_score",
        color="dominant_category",
        title="Average Dominant AI Score by Category"
    )
    fig_scores.update_layout(showlegend=False, xaxis_title="", yaxis_title="Average score")
    st.plotly_chart(fig_scores, use_container_width=True)

with methods_tab:
    st.subheader("Methods and Project Notes")

    st.markdown(
        """
        ### Dataset
        - File used in this app: `aipd_sample.csv`
        - Records: trimmed sample for app prototyping
        - Key fields: publication date, year, dominant AI category, and category scores

        ### Data Preparation
        - Converted publication dates to datetime format
        - Used the provided `dominant_category` field for category-level analysis
        - Calculated a `dominant_score` based on the score associated with each record's dominant AI category

        ### Research Question Coverage
        - **RQ1:** Temporal growth patterns
        - **RQ2:** Technology domain distribution and category shifts over time

        ### Current App Scope
        This deployed prototype focuses on the parts of the dataset available in the trimmed sample.
        If assignee and grant-status fields are added later, the app can be extended to support:
        - **RQ3:** Competitive landscape
        - **RQ4:** Filing-to-grant success rates

        ### Final Prompt
        Build a Streamlit dashboard that analyzes a trimmed USPTO AI patent dataset and presents
        descriptive analytics on patent activity trends, dominant AI technology categories,
        and category movement over time for a business audience.
        """
    )
