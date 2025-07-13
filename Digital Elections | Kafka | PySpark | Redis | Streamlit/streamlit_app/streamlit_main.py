import altair as alt
import redis
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd

st_autorefresh(interval=1000, key="auto-refresh")

st.set_page_config(layout="wide")
st.title("🗳️ Digital Election Dashboard")
st.write("(Live Results Monitoring Latency(1-5ms)")

# Connect to Redis (inside Docker)
r = redis.Redis(host="redis", port=6379, decode_responses=True)

# Read vote data from Redis
votes = r.hgetall("results")

if votes:
    df = pd.DataFrame(list(votes.items()), columns=["candidate", "unique_voters"])
    df["unique_voters"] = df["unique_voters"].astype(int)
    df = df.drop_duplicates("candidate", keep="last")
    df = df.sort_values(by="unique_voters", ascending=False).reset_index(drop=True)

    total_votes = df["unique_voters"].sum()
    df["percentage"] = (df["unique_voters"] / total_votes) * 100
    df["rank"] = df.index + 1


    def rank_emoji(r):
        return {1: "1", 2: "2", 3: "3"}.get(r, f"{r}")

    df["rank_display"] = df["rank"].apply(rank_emoji)

    # Styling function
    def highlight_top(row):
        if row["Rank"] == "1":
            return ['background-color: #411a12; font-weight: bold'] * len(row)
        elif row["Rank"] == "2":
            return ['background-color: #121841; font-weight: bold'] * len(row)
        elif row["Rank"] == "3":
            return ['background-color: #51263b; font-weight: bold'] * len(row)
        else:
            return [''] * len(row)

    # Table
    st.subheader("🏆 Leaderboard")
    styled_df = df[["rank_display", "candidate", "unique_voters", "percentage"]].rename(
        columns={
            "rank_display": "Rank",
            "candidate": "Candidate",
            "unique_voters": "Votes",
            "percentage": "Percentage (%)"
        }
    )
    st.dataframe(styled_df.style
        .format({"Votes": "{:,}", "Percentage (%)": "{:.2f}%"})
        .apply(highlight_top, axis=1))

    # Colors for charts
    soft_color_scale = alt.Scale(
        domain=df["candidate"].tolist(),
        range=[
            "#4E79A7", "#A0CBE8", "#F28E2B", "#FFBE7D",
            "#59A14F", "#8CD17D", "#B6992D", "#F1CE63",
            "#499894", "#86BCB6"
        ]
    )

    # 📊 Horizontal Bar Chart
    bar_chart = alt.Chart(df).mark_bar().encode(
        y=alt.Y("candidate:N", sort="-x", axis=alt.Axis(title="Candidate")),
        x=alt.X("percentage:Q", axis=alt.Axis(title="Vote Percentage (%)")),
        color=alt.Color("candidate:N", scale=soft_color_scale, legend=None),
        tooltip=[
            "candidate",
            alt.Tooltip("unique_voters", format=",d"),
            alt.Tooltip("percentage", format=".2f")
        ]
    ).properties(
        width=700,
        height=400,
        title="📊 Vote Percentage by Candidate"
    )
    st.altair_chart(bar_chart, use_container_width=True)

    # 🍩 Donut Chart
    donut_chart = alt.Chart(df).encode(
        theta=alt.Theta("percentage:Q"),
        color=alt.Color("candidate:N", scale=soft_color_scale, legend=alt.Legend(title="Candidate")),
        tooltip=[
            "candidate",
            alt.Tooltip("unique_voters", format=",d"),
            alt.Tooltip("percentage", format=".2f")
        ]
    ).mark_arc(innerRadius=70).properties(
        width=400,
        height=400,
        title="🍩 Vote Percentage Distribution"
    )
    st.altair_chart(donut_chart, use_container_width=False)

else:
    st.info("Waiting for vote aggregation results...")
