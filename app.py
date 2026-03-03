import streamlit as st
import altair as alt
import pandas as pd
from utils.io import load_data

from charts.charts import (
    base_theme,
    chart_team_scatter,
    chart_linked_scatter_to_attack,
    chart_home_away_bars,
)

st.set_page_config(page_title="HW4 Story", layout="wide")
alt.themes.register("project", base_theme)
alt.themes.enable("project")

df = load_data()

st.title("HW4: EPL Performance Patterns")

st.markdown(
    "Over the past two Premier League seasons (2023–24 and 2024–25), team performance has shifted, and total points captures some major changes. "
    "However, there are many other reasons that factor into why total points has shifted so much between seasons. "
    "While winners and losers are often highlighted, there is often obscurity in how those results are produced. "
    "This story asks a deeper question: beyond total points, how do consistency in attacking performance and home-versus-away differences shape the gap between seasons?\n\n"
    "The biggest differences between seasons aren’t just about how many points teams accumulate, but about how consistently they score and whether that performance actually travels from home to away matches."
    "Takeaway: teams can land on similar point totals through very different consistency profiles."
)

st.divider()

seasons = sorted(df["Season"].dropna().unique().tolist())

team_season = (
    df.groupby(["Season", "Team"], as_index=False)
      .agg(Pts=("Pts", "sum"), GF=("GF", "sum"), GA=("GA", "sum"))
)
if len(team_season) > 0:
    pts_pivot = team_season.pivot_table(index="Team", columns="Season", values="Pts")
    pts_pivot["delta_pts"] = pts_pivot[seasons[-1]] - pts_pivot[seasons[0]] if len(seasons) >= 2 else None
    biggest_risers = (
        pts_pivot.sort_values("delta_pts", ascending=False)
        .dropna(subset=["delta_pts"])
        .head(5)
        .reset_index()
    )
    biggest_fallers = (
        pts_pivot.sort_values("delta_pts", ascending=True)
        .dropna(subset=["delta_pts"])
        .head(5)
        .reset_index()
    )
else:
    biggest_risers = pd.DataFrame()
    biggest_fallers = pd.DataFrame()

st.header("Team performance by season")
st.write(
    "First, I’m anchoring everything in total points because that’s the first step in analyzing what changed between seasons."
    "However, I’m not treating points like the whole story, just the starting point."
)

with st.expander("How to read this"):
    st.write(
        "Use the season dropdown to switch between 2023–24 and 2024–25. "
        "Compare movement in total points by teams. The order stays fixed (but some teams differ between seasons)."
    )
    st.write(
        "I’m mainly looking for: (1) who jumps a lot across seasons, and (2) who stays in the same general band."
    )

st.altair_chart(chart_team_scatter(df), use_container_width=True)

if len(biggest_risers) > 0 and len(biggest_fallers) > 0:
    st.subheader("Quick season-to-season movers")
    c1, c2 = st.columns(2)
    with c1:
        st.write("Biggest risers (points gained):")
        st.dataframe(
            biggest_risers[["Team", "delta_pts"]].rename(columns={"delta_pts": "Δ points"}),
            hide_index=True,
            use_container_width=True,
        )
    with c2:
        st.write("Biggest fallers (points lost):")
        st.dataframe(
            biggest_fallers[["Team", "delta_pts"]].rename(columns={"delta_pts": "Δ points"}),
            hide_index=True,
            use_container_width=True,
        )

st.divider()

st.header("From points to consistency")
st.write(
    "Points tell you outcomes, but how consistent were teams throughout each season in earning those points?"
    "This section connects a team’s season-level position of total points to what their attacking output looked like from match to match."
)

st.write(
    "In practice, a team can finish with a high number of total points but still be volatile throughout the season with a varying match-to-match output, "
    "or they could finish lower but be surprisingly steady. I’m treating consistency as part of the explanation for why seasons shift."
)

with st.expander("How to read this"):
    st.write(
        "Use the season dropdown, then click a team on the left scatter. "
        "The right chart updates to show that team’s rolling attacking output over time, split by Home vs Away."
    )
    st.write(
        "The rolling average smooths noise, but if the line is still jumping around a lot, that shows real instability."
    )

st.altair_chart(chart_linked_scatter_to_attack(df), use_container_width=True)

st.write(
    "What I’m watching for here are "
    "teams whose attacking line is steady across the season vs teams that look streaky, "
    "and whether Home vs Away lines separate in a way that suggests performance doesn’t fully travel."
)

st.divider()

st.header("Home vs away performance")
st.write(
    "Finally, I’m isolating the question of if performance differs by venue. Even if two teams finish near each other in total points, "
    "one might be much more dependent on home results while the other travels better."
)

st.write(
    "I’m showing two things: home vs away points totals, and a direct metric showing home advantage (home points – away points). "
    "This makes it easier to spot teams whose record is actually dependent on being home."
)

with st.expander("How to read this"):
    st.write(
        "Switch the season dropdown and compare the same team’s bars across seasons. "
        "On the left, the light blue bar shows away points and the dark blue bar shows home points. A bigger gap between home and away bars means more reliance on venue."
    )
    st.write(
        "On the right, positive values mean a team earned more points at home than away, and negative values mean the opposite (Burnley scored more points at away games versus home, for example)."
    )

st.altair_chart(chart_home_away_bars(df), use_container_width=True)

st.divider()

st.header("Conclusion")
st.write(
    "At a surface level, season differences show up as point shifts. "
    "But when you pair that with attacking consistency and home/away splits, the story gets more explanatory. "
    "Some teams change because their performance profile actually changes, meaning they have more stable attack and travel better, "
    "while others change because variance and venue effects swing their outcomes."
)

st.write(
    "Here is an analysis of two teams with different causes in changes in points: Nottingham Forest and Tottenham" 
)
st.write(
    "Nottingham Forest stands out as one of the clearest season-to-season risers. In the season-level scatter, their total points increase by 29 from 2023–24 to 2024–25. What makes this interesting is how that improvement happens."
    " Looking at their attacking consistency in the linked chart, Forest’s rolling goal average does not necessarily become dramatically smoother in 2024–25, but it appears slightly higher across longer stretches of the season. Instead of relying only on isolated spikes, their attacking output in the stronger season seems to hold at a slightly more sustained level at key points."
    " Moving to the home vs away bars, Forest does not appear overly dependent on home advantage relative to other teams, as the bars are generally even on the left, and there is little change in home points - away points on the right. Their gains seem to come from broader performance improvements rather than just venue-specific boosts. In this case, the rise in total points aligns with improved consistency."
)
st.write(
    "Tottenham provides the opposite case. As one of the largest point fallers between seasons, losing 28 points, they illustrate how a team can drop significantly in the table even if parts of their profile remain competitive."
    "In the season-level scatter, Tottenham’s total points fall noticeably in 2024–25. When we examine their rolling attacking output, the pattern appears very uneven in both seasons."
    "The home vs away comparison adds another layer. Tottenham’s home advantage is greater in the 2024-25 season, suggesting that part of the drop could be tied to changes in venue-based performance. If home production weakens or away output fails to compensate, total points decline quickly."
    "Unlike Forest, whose improvement looks like increased steadiness, Tottenham’s drop appears tied to inconsistency and uneven performance across venues."
)
st.write(
    "At a surface level, season differences show up as point shifts. But pairing total points with attacking consistency and home/away splits tells a more complete story. Nottingham Forest’s rise appears tied to steadier performance across matches, while Tottenham’s fall reflects volatility and shifting venue effects. The gap between seasons is not just about how many points teams earn, but about how those points are produced."
)