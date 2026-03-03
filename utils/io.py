import pandas as pd
import streamlit as st

@st.cache_data
def load_data() -> pd.DataFrame:
    df1 = pd.read_csv("data/PL-season-2324.csv")
    df2 = pd.read_csv("data/PL-season-2425.csv")

    df1["Season"] = "2023–24"
    df2["Season"] = "2024–25"

    df = pd.concat([df1, df2], ignore_index=True)

    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

    df["HomePts"] = df["FTR"].map({"H": 3, "D": 1, "A": 0})
    df["AwayPts"] = df["FTR"].map({"A": 3, "D": 1, "H": 0})

    home = df[["Season","Date","HomeTeam","AwayTeam","FTHG","FTAG","HomePts"]].copy()
    home.columns = ["Season","Date","Team","Opponent","GF","GA","Pts"]
    home["Venue"] = "Home"

    away = df[["Season","Date","AwayTeam","HomeTeam","FTAG","FTHG","AwayPts"]].copy()
    away.columns = ["Season","Date","Team","Opponent","GF","GA","Pts"]
    away["Venue"] = "Away"

    long = pd.concat([home, away], ignore_index=True).sort_values(["Season","Team","Date"])
    long["MatchNum"] = long.groupby(["Season","Team"]).cumcount() + 1

    return long
    
