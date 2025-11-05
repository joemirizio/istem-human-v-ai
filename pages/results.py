from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

import db

COLOR_1 = "#33a0bb"
COLOR_2 = "#d01c65"

st.set_page_config(
    "Humans vs. Machines - Results", page_icon=":material/smart_toy:", layout="wide"
)
st.html(Path("static/style.css"))

conn = st.connection("game", type="sql")

st.markdown("# :material/bar_chart: Results")

df = db.get_results(conn)

if not len(df):
    st.info("No results to display")
    if st.button("Home", icon=":material/home:"):
        st.switch_page("main.py")
    st.stop()

metrics = st.columns(3)
total_human = df.query("ai == 0")["session_id"].nunique()
total_ai = df.query("ai == 1")["session_id"].nunique()
total_participants = total_human + total_ai

metrics[0].metric("Total participants", total_participants, border=True)
metrics[1].metric("Human", total_human, border=True)
metrics[2].metric("Human + AI", total_ai, border=True)

df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce")
df["end_time"] = pd.to_datetime(df["end_time"], errors="coerce")
df = df.dropna(subset=["start_time", "end_time", "question_id", "ai", "guesses"])
df["elapsed_sec"] = (df["end_time"] - df["start_time"]).dt.total_seconds()
df = df[df["elapsed_sec"] >= 0]


# REMOVE OUTLIERS
# --- IQR-based outlier removal per (question_id, ai) ---
def iqr_bounds(s, k=1.5):
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    low = q1 - k * iqr
    high = q3 + k * iqr
    return pd.Series({"low": low, "high": high})


bounds = (
    df.groupby(["question_id", "ai"])["elapsed_sec"]
    .apply(iqr_bounds, k=1.5)
    .unstack()
    .reset_index()
)

df_clean = df.merge(bounds, on=["question_id", "ai"], how="left")
df_clean = df_clean[
    (df_clean["elapsed_sec"] >= df_clean["low"])
    & (df_clean["elapsed_sec"] <= df_clean["high"])
].copy()

# ----


# Optional: convert to minutes or hours for readability
# df_clean['elapsed_min'] = df_clean['elapsed_sec'] / 60.0
# y_col = 'elapsed_min'; y_label = 'Elapsed Time (minutes)'
y_col = "elapsed_sec"
y_label = "Elapsed Time (s)"

# Ensure ai is treated as a category with readable labels
df_clean["ai"] = df_clean["ai"].astype(int).map({0: "Human", 1: "Human + AI"})

# --- Plot: interactive grouped box + jittered points ---
fig = px.box(
    df_clean,
    x="question_id",
    y=y_col,
    color="ai",
    points="all",  # show jittered points
    notched=False,
    color_discrete_map={"Human": COLOR_1, "Human + AI": COLOR_2},
    category_orders={
        "ai": ["Human", "Human + AI"],
    },
)

# Improve hover & layout
fig.update_traces(
    jitter=0.3,
    pointpos=0,  # centered
    marker=dict(size=4, opacity=0.5, line=dict(width=0)),
    hovertemplate=("Question: %{x}<br>" + f"{y_label}: %{{y:.2f}}"),
)

fig.update_layout(
    title="Elapsed Time by Question and AI Usage (Outliers Removed by IQR)",
    xaxis_title="Question",
    yaxis_title=y_label,
    boxmode="group",  # side-by-side by color
    legend_title_text="User",
    template="plotly_white",
    margin=dict(l=40, r=20, t=60, b=40),
)


st.plotly_chart(fig)


# --- Aggregate if there are multiple rows per (question_id, ai) ---
# Choose your aggregator: 'mean', 'sum', 'median'
agg_func = "mean"

agg = (
    df.groupby(["question_id", "ai"], as_index=False).agg(
        guesses=("guesses", agg_func), n=("guesses", "size")
    )  # keep counts for hover
)

# Friendly labels for legend
agg["ai"] = agg["ai"].map({0: "Human", 1: "Human + AI"})

# Optional: sort question_id naturally if numeric-like strings
try:
    order = sorted(agg["question_id"].unique(), key=lambda v: float(v))
except Exception:
    order = sorted(agg["question_id"].astype(str).unique())

# --- Plot ---
fig = px.bar(
    agg,
    x="question_id",
    y="guesses",
    color="ai",
    barmode="group",  # side-by-side series
    color_discrete_map={"Human": COLOR_1, "Human + AI": COLOR_2},
    category_orders={
        "question_id": order,
        "ai": ["Human", "Human + AI"],
    },
)

fig.update_traces(
    hovertemplate=(
        f"Question: %{{x}}<br>Guesses ({agg_func}): %{{y:.2f}}<br>n: %{{customdata[0]}}"
    ),
    customdata=np.stack([agg["n"]], axis=-1),
)

fig.update_layout(
    title=f"Guesses by Question and AI Usage ({agg_func.capitalize()} per Group)",
    xaxis_title="Question",
    yaxis_title="Guesses",
    legend_title_text="User",
    template="plotly_white",
    margin=dict(l=40, r=20, t=60, b=40),
)

st.plotly_chart(fig)


if st.button(
    "Home", key="results-home", icon=":material/home:", use_container_width=True
):
    st.switch_page("main.py")
