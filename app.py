import streamlit as st
import pandas as pd
import requests
import os

# Professional Page Setup
st.set_page_config(page_title="Wirewolves Strategic Dashboard", layout="wide")

st.title("🐺 FRC Strategic Scouting Dashboard & Live Analytics Engine")
st.markdown("### Weekend 4: Live The Blue Alliance API Integration Active")
st.markdown("---")

# 1. Load local spreadsheet data safely using Pandas
csv_filename = "scouting_data.csv"

if os.path.exists(csv_filename):
    df = pd.read_csv(csv_filename)
    df["Team Number"] = df["Team Number"].astype(str).str.strip()
else:
    st.error(f"Missing {csv_filename}. Please make sure it is in your folder.")
    df = pd.DataFrame()

# 2. Live API Connection Configuration
# Replace the placeholder text inside quotes with your actual key from Step 1!
TBA_API_KEY = "YOUR_BLUE_ALLIANCE_API_KEY_HERE"
EVENT_KEY = "2026mdsv" # Target event key (e.g., 2026 Maryland District Severn Event)

@st.cache_data(ttl=600)  # Caches web data for 10 minutes so your app runs fast
def fetch_live_tba_metrics(api_key, event_key):
    """Hits The Blue Alliance API pipeline to fetch official team stats live."""
    headers = {"X-TBA-Auth-Key": api_key}
    url = f"https://thebluealliance.com{event_key}/oprs"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Extract OPR metrics cleanly into a dictionary structure
            oprs = {k.replace("frc", ""): round(v, 2) for k, v in data.get("oprs", {}).items()}
            return oprs
    except:
        pass
    return {}

# Attempt to load live numbers if key is provided
live_oprs = {}
if TBA_API_KEY != "YOUR_BLUE_ALLIANCE_API_KEY_HERE":
    live_oprs = fetch_live_tba_metrics(TBA_API_KEY, EVENT_KEY)

# 3. Sidebar Control Panels
st.sidebar.header("📊 Strategic Controls")
strategy_focus = st.sidebar.selectbox(
    "Select Alliance Team Role:",
    ["Full Leaderboard", "Offensive Focus (Scout + Live OPR)", "Defensive Focus"]
)

# 4. Merge Local Data with Live Web Analytics
if not df.empty:
    working_df = df.copy()
    
    # Map live OPR scores to their matching team row automatically
    working_df["Live OPR (Official)"] = working_df["Team Number"].map(live_oprs).fillna(0.0)
    
    # Simple cleaning metric for range strings
    def extract_max_points(val):
        val_str = str(val).strip()
        if '-' in val_str:
            try: return float(val_str.split('-')[-1])
            except: return 0.0
        elif '1-20' in val_str or '20' in val_str: return 20.0
        return 0.0

    working_df["Cleaned Points"] = working_df["Robot Points / Shots per match"].apply(extract_max_points)

    if "Offensive Focus" in strategy_focus:
        st.subheader("🎯 Live Offensive Picklist (Local Stats Balanced with Live OPR)")
        
        # Supercharged Sorting Calculation: Combines your scout observations with official data science metrics
        def calculate_hybrid_offense(row):
            score = row["Cleaned Points"] * 1.5
            score += row["Live OPR (Official)"] * 2.0  # Give massive priority weight to verified live OPR performance
            if "yes" in str(row["Shooting in auto"]).lower():
                score += 20.0
            return round(score, 2)

        working_df["Hybrid Offense Rating"] = working_df.apply(calculate_hybrid_offense, axis=1)
        filtered_df = working_df[working_df["Main strategy"].str.contains("Shooter|Offense", case=False, na=False)]
        display_df = filtered_df.sort_values(by="Hybrid Offense Rating", ascending=False)
        
    elif "Defensive Focus" in strategy_focus:
        st.subheader("🛡️ Custom Defensive Picklist")
        filtered_df = working_df[
            (working_df["Defensive Bot"].str.contains("Yes", case=False, na=False)) | 
            (working_df["How effective? (Defense)"].str.contains("High|Medium", case=False, na=False))
        ]
        display_df = filtered_df
    else:
        st.subheader("📋 Integrated Event Leaderboard")
        display_df = working_df

    # Render data frames professionally on screen
    st.dataframe(display_df, use_container_width=True, hide_index=True)
