import streamlit as st
import pandas as pd
import requests
import os

st.set_page_config(page_title="Wirewolves Strategic Dashboard", layout="wide")

st.title("Wirewolves Strategic Scouting Dashboard and Live Analytics Engine")
st.markdown("Weekend 4: Live The Blue Alliance API Integration Active")
st.markdown("---")

csv_filename = "scouting_data.csv"

if os.path.exists(csv_filename):
    df = pd.read_csv(csv_filename)
    df["Team Number"] = df["Team Number"].astype(str).str.strip()
else:
    st.error("Missing scouting_data.csv file. Please add it to your folder.")
    df = pd.DataFrame()

TBA_API_KEY = "N3lfxmEl2ELs2ywwVeDdBhHoJSGSbSISqusTnu4y0rbXJrE2bqGBO29p1GL2sQJ1"
EVENT_KEY = "2026mdsv"

@st.cache_data(ttl=600)
def fetch_live_tba_metrics(api_key, event_key):
    headers = {"X-TBA-Auth-Key": api_key}
    url = f"https://thebluealliance.com{event_key}/oprs"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            oprs = {k.replace("frc", ""): round(v, 2) for k, v in data.get("oprs", {}).items()}
            return oprs
    except:
        pass
    return {}

live_oprs = fetch_live_tba_metrics(TBA_API_KEY, EVENT_KEY)

st.sidebar.header("Strategic Controls")
strategy_focus = st.sidebar.selectbox(
    "Select Alliance Team Role:",
    ["Full Leaderboard", "Offensive Focus", "Defensive Focus"]
)

if not df.empty:
    working_df = df.copy()
    working_df["Live OPR (Official)"] = working_df["Team Number"].map(live_oprs).fillna(0.0)
    
    def extract_max_points(val):
        val_str = str(val).strip()
        if '-' in val_str:
            try:
                return float(val_str.split('-')[-1])
            except:
                return 0.0
        elif '1-20' in val_str or '20' in val_str:
            return 20.0
        return 0.0

    working_df["Cleaned Points"] = working_df["Robot Points / Shots per match"].apply(extract_max_points)

    if strategy_focus == "Offensive Focus":
        st.subheader("Custom Offensive Picklist")
        
        def calculate_hybrid_offense(row):
            score = row["Cleaned Points"] * 1.5
            score += row["Live OPR (Official)"] * 2.0
            if "yes" in str(row["Shooting in auto"]).lower():
                score += 20.0
            return round(score, 2)

        working_df["Hybrid Offense Rating"] = working_df.apply(calculate_hybrid_offense, axis=1)
        filtered_df = working_df[working_df["Main strategy"].str.contains("Shooter|Offense", case=False, na=False)]
        display_df = filtered_df.sort_values(by="Hybrid Offense Rating", ascending=False)
        
    elif strategy_focus == "Defensive Focus":
        st.subheader("Custom Defensive Picklist")
        filtered_df = working_df[
            (working_df["Defensive Bot"].str.contains("Yes", case=False, na=False)) | 
            (working_df["How effective? (Defense)"].str.contains("High|Medium", case=False, na=False))
        ]
        display_df = filtered_df
    else:
        st.subheader("Integrated Event Leaderboard")
        display_df = working_df

    st.dataframe(display_df, use_container_width=True, hide_index=True)
