import streamlit as st
import pandas as pd
import os

# Professional Page Setup
st.set_page_config(page_title="Wirewolves Strategic Dashboard", layout="wide")

st.title("🐺 FRC Strategic Scouting Dashboard & Picklist Generator")
st.markdown("### Weekend 3: Multi-Parameter Ranking Engine Enabled")
st.markdown("---")

# 1. Load data safely using Pandas
csv_filename = "scouting_data.csv"

if os.path.exists(csv_filename):
    df = pd.read_csv(csv_filename)
    df["Team Number"] = df["Team Number"].astype(str)
else:
    st.error(f"Missing {csv_filename}. Please add it to your GitHub folder.")
    df = pd.DataFrame()

# 2. Sidebar Control Panel
st.sidebar.header("📊 Strategic Controls")

# Strategy Dropdown Menu
strategy_focus = st.sidebar.selectbox(
    "Select Alliance Team Role:",
    ["Full Leaderboard", "Offensive Focus (Custom Weighting)", "Defensive Focus (Custom Weighting)"]
)

# 3. Heavy-Duty Data Logic and Ranking Math
if not df.empty:
    working_df = df.copy()
    
    # Helper clean function to extract high-end scores from ranges like '101-150' or '21-50'
    def extract_max_points(val):
        val_str = str(val).strip()
        if '-' in val_str:
            try:
                return float(val_str.split('-')[1]) # Takes the highest number in the range
            except:
                return 0.0
        elif '1-20' in val_str or '20' in val_str:
            return 20.0
        return 0.0

    # Apply the range cleaning formula behind the scenes
    working_df["Cleaned Points"] = working_df["Robot Points / Shots per match"].apply(extract_max_points)

    if "Offensive Focus" in strategy_focus:
        st.subheader("🎯 Custom Offensive Picklist (Ranked by Strategic Yield Math)")
        st.caption("Sorting Math Matrix: (Max Match Points × 2.5) + (Accuracy Bonus if 90-100%)")
        
        # Calculate a sophisticated custom rating score
        def calculate_offense_score(row):
            score = row["Cleaned Points"] * 2.5
            if "90-100%" in str(row["Approximate Accuracy (shooting)"]):
                score += 50.0  # Big reward for extreme accuracy
            elif "70-90%" in str(row["Approximate Accuracy (shooting)"]):
                score += 25.0
            if "yes" in str(row["Shooting in auto"]).lower():
                score += 30.0  # Reward for autonomous capability
            return score

        working_df["Strategic Offense Score"] = working_df.apply(calculate_offense_score, axis=1)
        
        # Filter for shooters and sort instantly from highest score to lowest
        filtered_df = working_df[working_df["Main strategy"].str.contains("Shooter|Offense", case=False, na=False)]
        display_df = filtered_df.sort_values(by="Strategic Offense Score", ascending=False)
        
    elif "Defensive Focus" in strategy_focus:
        st.subheader("🛡️ Custom Defensive Picklist (Ranked by Lockdown Metrics)")
        st.caption("Sorting Math Matrix: (Base Position Value) + (Effectiveness Scale Rating)")
        
        def calculate_defense_score(row):
            score = 0.0
            if "yes" in str(row["Defensive Bot"]).lower():
                score += 50.0
            if "high" in str(row["How effective? (Defense)"]).lower():
                score += 50.0
            elif "medium" in str(row["How effective? (Defense)"]).lower():
                score += 25.0
            return score

        working_df["Strategic Defense Score"] = working_df.apply(calculate_defense_score, axis=1)
        
        # Filter for defensive impact teams and sort
        filtered_df = working_df[
            (working_df["Defensive Bot"].str.contains("Yes", case=False, na=False)) | 
            (working_df["How effective? (Defense)"].str.contains("High|Medium|Medium", case=False, na=False))
        ]
        display_df = filtered_df.sort_values(by="Strategic Defense Score", ascending=False)
    else:
        st.subheader("📋 Raw Data Standings (Unsorted)")
        display_df = working_df

    # 4. Display the polished, calculated table on screen
    st.dataframe(display_df, use_container_width=True, hide_index=True)
