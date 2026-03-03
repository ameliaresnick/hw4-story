import altair as alt
import pandas as pd

def base_theme():
    return {
        "config": {
            "view": {"stroke": None},
            "axis": {"labelFontSize": 12, "titleFontSize": 14},
            "legend": {"labelFontSize": 12, "titleFontSize": 14},
        }
    }

def _team_season_agg(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["Season", "Team"], as_index=False)
          .agg(Pts=("Pts", "sum"), GF=("GF", "sum"), GA=("GA", "sum"))
          .assign(GD=lambda d: d["GF"] - d["GA"])
    )

def chart_team_scatter(df: pd.DataFrame) -> alt.Chart:
    team_season = _team_season_agg(df)
    seasons = sorted(team_season["Season"].unique().tolist())

    selectSeason = alt.param(
        name="Select_Season",
        bind=alt.binding_select(options=seasons, name="Season: "),
        value=seasons[0] if len(seasons) else None
    )

    q1 = (
        alt.Chart(team_season)
        .transform_filter(alt.datum.Season == selectSeason)
        .mark_circle(size=80)
        .encode(
            x=alt.X("Pts:Q", title="Points"),
            y=alt.Y("Team:N", sort="ascending", title="Team"),
            tooltip=["Season:N", "Team:N", "Pts:Q", "GF:Q", "GA:Q", "GD:Q"]
        )
        .add_params(selectSeason)
        .properties(width=520, height=520, title="Team performance by season (dropdown)")
    )

    return q1

def chart_linked_scatter_to_attack(df: pd.DataFrame) -> alt.Chart:
    team_season = _team_season_agg(df)
    seasons = sorted(team_season["Season"].unique().tolist())

    selectSeason = alt.param(
        name="Select_Season",
        bind=alt.binding_select(options=seasons, name="Season: "),
        value=seasons[0] if len(seasons) else None
    )

    default_team = sorted(team_season["Team"].unique().tolist())[0] if len(team_season) else None

    teamSelect = alt.selection_point(
        fields=["Team"],
        empty=True,
        value=[{"Team": default_team}] if default_team is not None else None
    )

    q1 = (
        alt.Chart(team_season)
        .transform_filter(alt.datum.Season == selectSeason)
        .mark_circle(size=80)
        .encode(
            x=alt.X("Pts:Q", title="Points"),
            y=alt.Y("Team:N", sort="ascending", title="Team"),
            opacity=alt.condition(teamSelect, alt.value(1), alt.value(0.25)),
            tooltip=["Season:N", "Team:N", "Pts:Q", "GF:Q", "GA:Q", "GD:Q"]
        )
        .add_params(selectSeason, teamSelect)
        .properties(width=520, height=520, title="Team performance by season (dropdown + click team)")
    )

    q2 = (
        alt.Chart(df)
        .transform_filter(alt.datum.Season == selectSeason)
        .transform_filter(teamSelect)
        .transform_window(
            rolling_goals="mean(GF)",
            frame=[-3, 0],
            groupby=["Season", "Team", "Venue"]
        )
        .mark_line()
        .encode(
            x=alt.X("MatchNum:Q", title="Match (ordered by date)"),
            y=alt.Y("rolling_goals:Q", title="Rolling avg goals (4-match)"),
            color=alt.Color("Venue:N", title="Venue"),
            tooltip=["Season:N", "Team:N", "Venue:N", "MatchNum:Q", "rolling_goals:Q"]
        )
        .properties(width=520, height=300, title="Selected team attacking performance over time")
    )

    return (q1 | q2)

def chart_home_away_bars(df: pd.DataFrame) -> alt.Chart:
    season_options = sorted(df["Season"].unique().tolist())

    selectSeason = alt.param(
        name="Select_Season_Q3",
        bind=alt.binding_select(options=season_options, name="Season: "),
        value=season_options[0] if len(season_options) else None
    )

    pts = (
        df.groupby(["Season", "Team", "Venue"], as_index=False)
          .agg(Pts=("Pts", "sum"))
    )

    wide = (
        pts.pivot_table(index=["Season", "Team"], columns="Venue", values="Pts", fill_value=0)
           .reset_index()
           .rename_axis(None, axis=1)
    )

    if "Home" not in wide.columns:
        wide["Home"] = 0
    if "Away" not in wide.columns:
        wide["Away"] = 0

    wide["Diff"] = wide["Home"] - wide["Away"]

    bars = (
        alt.Chart(pts)
        .transform_filter(alt.datum.Season == selectSeason)
        .mark_bar()
        .encode(
            y=alt.Y("Team:N", sort="ascending", title="Team"),
            x=alt.X("Pts:Q", title="Points"),
            color=alt.Color("Venue:N", title="Venue"),
            tooltip=["Season:N", "Team:N", "Venue:N", "Pts:Q"]
        )
        .add_params(selectSeason)
        .properties(width=520, height=500, title="Home vs away points by team")
    )

    diff = (
        alt.Chart(wide)
        .transform_filter(alt.datum.Season == selectSeason)
        .mark_bar()
        .encode(
            y=alt.Y("Team:N", sort="ascending", title="Team"),
            x=alt.X("Diff:Q", title="HomePts - AwayPts"),
            tooltip=["Season:N", "Team:N", "Home:Q", "Away:Q", "Diff:Q"]
        )
        .properties(width=380, height=500, title="Home advantage (HomePts - AwayPts)")
    )

    return (bars | diff)