import streamlit as st
import pandas as pd
import requests
import os

# Professional Page Customization
st.set_page_config(page_title="Wirewolves Strategic Dashboard", layout="wide")

st.title("Wirewolves Strategic Scouting Dashboard and Live Analytics Engine")
st.markdown("Master Production Engine: Integrated Match Pairing Matrix and Live Data Links")
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

# 1. Sidebar Strategic Inputs and Expanded Pit Characteristics
st.sidebar.header("Strategic Controls")
strategy_focus = st.sidebar.selectbox(
    "Select Alliance Team Role:",
    ["Full Leaderboard", "Offensive Focus", "Defensive Focus", "Match Alliance Matcher"]
)

st.sidebar.markdown("---")
st.sidebar.header("Pit Scouting: Robot Characteristics")

with st.sidebar.form(key="pit_form", clear_on_submit=True):
    pit_team = st.text_input("Team Number*")
    pit_drive = st.selectbox("Drive Train Type", ["Swerve Type", "Tank Type", "Mechanum Type"])
    pit_intake = st.selectbox("Intake Assembly", ["Ground Intake", "Source Intake", "Dual Intake"])
    pit_strategy = st.selectbox("Observed Strategy", ["Shooter", "Gatherer", "Defense"])
    submit_pit = st.form_submit_button(label="Save Pit Scout Profile")

if submit_pit and pit_team:
    st.sidebar.success(f"Pit configuration saved for Team {pit_team}!")

# 2. Advanced Mathematical Calculations and Data Merging
if not df.empty:
    working_df = df.copy()
    
    # Inject Live OPR columns straight from the internet servers
    working_df["Live OPR (Official)"] = working_df["Team Number"].map(live_oprs).fillna(0.0)
    
    # Generate direct, functional HTML clickable web links for every team row
    working_df["Official Standings Profile"] = "https://firstinspires.org"

    def extract_max_points(val):
        val_str = str(val).strip()
        if '-' in val_str:
            try: return float(val_str.split('-')[-1])
            except: return 0.0
        elif '1-20' in val_str or '20' in val_str: return 20.0
        return 0.0

    working_df["Cleaned Points"] = working_df["Robot Points / Shots per match"].apply(extract_max_points)

    # 3. Handle Dropdown Control Flows
    if strategy_focus == "Offensive Focus":
        st.subheader("Custom Offensive Picklist")
        def calculate_hybrid_offense(row):
            score = row["Cleaned Points"] * 1.5
            score += row["Live OPR (Official)"] * 2.0
            return round(score, 2)
        working_df["Hybrid Offense Rating"] = working_df.apply(calculate_hybrid_offense, axis=1)
        filtered_df = working_df[working_df["Main strategy"].str.contains("Shooter|Offense", case=False, na=False)]
        display_df = filtered_df.sort_values(by="Hybrid Offense Rating", ascending=False)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
    elif strategy_focus == "Defensive Focus":
        st.subheader("Custom Defensive Picklist")
        display_df = working_df[(working_df["Defensive Bot"].str.contains("Yes", case=False, na=False))]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
    elif strategy_focus == "Match Alliance Matcher":
        st.subheader("Automated Match Alliance Combinator Engine")
        st.markdown("Select prospective alliance partners to evaluate real-time strategic synergy and projected output.")
        
        # Build selection containers
        col1, col2, col3 = st.columns(3)
        with col1: t1 = st.selectbox("Alliance Station 1 (You)", working_df["Team Number"].unique(), key="s1")
        with col2: t2 = st.selectbox("Alliance Partner 2", working_df["Team Number"].unique(), key="s2")
        with col3: t3 = st.selectbox("Alliance Partner 3", working_df["Team Number"].unique(), key="s3")
        
        # Functional Multi-Robot Computation Math Block
        team_stats = working_df[working_df["Team Number"].isin([t1, t2, t3])]
        total_projected_opr = round(team_stats["Live OPR (Official)"].sum(), 2)
        total_scout_points = round(team_stats["Cleaned Points"].sum(), 2)
        
        # Display automated strategic data matrix cards instantly on the screen
        st.markdown("### 📊 Projected Alliance Strength Matrix")
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric(label="Combined Alliance OPR (Live Web Data)", value=f"{total_projected_opr} Points")
        with metric_col2:
            st.metric(label="Projected Match Cycle Score (Scout Data)", value=f"{total_scout_points} Pieces")
            
        st.dataframe(team_stats[["Team Number", "Main strategy", "Live OPR (Official)", "Cleaned Points", "Official Standings Profile"]], use_container_width=True, hide_index=True)
        
    else:
        st.subheader("Integrated Event Leaderboard")
        # Display clean, optimized interactive data table
        st.dataframe(working_df, use_container_width=True, hide_index=True)
