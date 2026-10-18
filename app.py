import streamlit as st
import pandas as pd
import requests
import os

# Professional Page Customization
st.set_page_config(page_title="Wirewolves Strategic Dashboard", layout="wide", page_icon="🎈")

st.title("Wirewolves Strategic Scouting Dashboard and Live Analytics Engine")
st.markdown("Master Production Engine: Integrated Match Pairing Matrix and Live Data Links")
st.markdown("---")

# -----------------------------------------------------------------------------
# DYNAMIC SEED MEMORY (Synchronizing Inputs and Leaderboards)
# -----------------------------------------------------------------------------
# UPGRADE: Now tracking individual match-by-match history instead of single team snapshots
if "match_scouting_history" not in st.session_state:
    st.session_state["match_scouting_history"] = pd.DataFrame([
        {"Match Number": 1, "Team Number": "4541", "Main Strategy": "Defensive Anchor", "Drive Train": "Swerve Drive", "Intake": "Ground Intake", "Env Navigation": "Level 3 Climber", "Scout Points (0-100)": 70.0, "Defensive Score": 95.0, "Notes": "Heavy lock defense"},
        {"Match Number": 5, "Team Number": "4541", "Main Strategy": "Defensive Anchor", "Drive Train": "Swerve Drive", "Intake": "Ground Intake", "Env Navigation": "Level 3 Climber", "Scout Points (0-100)": 75.0, "Defensive Score": 85.0, "Notes": "Decent shooter under trench"},
        {"Match Number": 2, "Team Number": "5338", "Main Strategy": "Dedicated Scorer", "Drive Train": "West Coast Drive", "Intake": "Source Intake", "Env Navigation": "Low Stage Hub", "Scout Points (0-100)": 80.0, "Defensive Score": 40.0, "Notes": "Fast cycles"},
        {"Match Number": 6, "Team Number": "5338", "Main Strategy": "Dedicated Scorer", "Drive Train": "West Coast Drive", "Intake": "Source Intake", "Env Navigation": "Low Stage Hub", "Scout Points (0-100)": 84.0, "Defensive Score": 50.0, "Notes": "Tried shooting under trench early"},
        {"Match Number": 3, "Team Number": "6863", "Main Strategy": "Dedicated Scorer", "Drive Train": "Swerve Drive", "Intake": "Dual Intake (Both)", "Env Navigation": "Level 3 Climber + Trap", "Scout Points (0-100)": 95.0, "Defensive Score": 30.0, "Notes": "100% accuracy near subwoofer"},
        {"Match Number": 4, "Team Number": "7770", "Main Strategy": "Defensive Anchor", "Drive Train": "Mecanum Drive", "Intake": "Ground Intake", "Env Navigation": "No Climb", "Scout Points (0-100)": 30.0, "Defensive Score": 85.0, "Notes": "Low movement, static zone block"},
        {"Match Number": 7, "Team Number": "8592", "Main Strategy": "Feeder / Cycle Bot", "Drive Train": "Swerve Drive", "Intake": "Dual Intake (Both)", "Env Navigation": "Level 1 Park", "Scout Points (0-100)": 65.0, "Defensive Score": 60.0, "Notes": "Focused on gathering pieces"},
    ])

if "important_notes" not in st.session_state:
    st.session_state["important_notes"] = [
        {"Category": "🚨 Strategy Alert", "Team": "4541", "Note": "Intake chain loose in match 5. Monitor closely."},
        {"Category": "⚙️ Arena Update", "Team": "General", "Note": "Trench floor clearance is slightly uneven on Red side."}
    ]

# -----------------------------------------------------------------------------
# LIVE EXTERNAL WEBSITE API FETCHING (The Blue Alliance)
# -----------------------------------------------------------------------------
if "TBA_API_KEY" in st.secrets:
    TBA_API_KEY = st.secrets["TBA_API_KEY"]
else:
    TBA_API_KEY = "N31fXmE12ELs2ymwWeDd8PhoJSGSb5ISquSTnudyoYbxJrEzbqGD029p1GL2sQJi"

EVENT_KEY = "2026ndsv"

@st.cache_data(ttl=600)
def fetch_live_tba_metrics(api_key, event_key):
    headers = {"X-TBA-Auth-Key": api_key}
    url = f"https://thebluealliance.com{event_key}/oprs"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            oprs = {str(k).strip(): round(v, 2) for k, v in data.get("oprs", {}).items()}
            return oprs
    except:
        pass
    return {}

live_oprs = fetch_live_tba_metrics(TBA_API_KEY, EVENT_KEY)

# -----------------------------------------------------------------------------
# SIDEBAR INTERACTIVE CONSOLES (Match-by-Match Data Input)
# -----------------------------------------------------------------------------
st.sidebar.header("🏆 Strategic Selection")
strategy_focus = st.sidebar.selectbox(
    "Select Alliance Team Role",
    ["Full Leaderboard", "Offensive Focus", "Defensive Focus", "Match Alliance Matcher"]
)

st.sidebar.markdown("---")
st.sidebar.header("📝 Input Live Match Scout Data")
st.sidebar.markdown("Log performance indicators for individual qualification matches:")

with st.sidebar.form(key="scout_input_form", clear_on_submit=True):
    input_match = st.number_input("Qualification Match Number *", min_value=1, step=1, value=1)
    input_team = st.text_input("Team Number *")
    
    drive_options = ["Swerve Drive", "West Coast Drive", "Mecanum Drive", "Tank Drive (KitBot)", "Other (Type below...)"]
    selected_drive = st.selectbox("Drive Train Type", drive_options)
    custom_drive = st.text_input("If 'Other', specify Drivetrain:")
    
    intake_options = ["Ground Intake", "Source Intake", "Dual Intake (Both)", "No Intake (Defense Only)", "Other (Type below...)"]
    selected_intake = st.selectbox("Intake Configuration", intake_options)
    custom_intake = st.text_input("If 'Other', specify Intake:")
    
    strategy_options = ["Dedicated Scorer", "Feeder / Cycle Bot", "Defensive Anchor", "Other (Type below...)"]
    selected_strategy = st.selectbox("Observed Match Strategy", strategy_options)
    custom_strategy = st.text_input("If 'Other', specify Strategy:")
    
    input_env_nav = st.text_input("Match Env Navigation (e.g., Climber Level, Stage Zone, Obstacles)")
    
    st.markdown("##### Performance Metrics for this Match")
    input_score = st.slider("Offensive Cycle Score (0-100)", 0.0, 100.0, 70.0)
    input_defense = st.slider("Defensive Capability Score (0-100)", 0.0, 100.0, 50.0)
    
    input_notes = st.text_area("Match Observations / Notes")
    
    submit_match_data = st.form_submit_button(label="Log Match & Update Leaderboard")

if submit_match_data and input_team:
    clean_team = str(input_team).strip()
    
    final_drive = custom_drive.strip() if selected_drive == "Other (Type below...)" and custom_drive else selected_drive
    final_intake = custom_intake.strip() if selected_intake == "Other (Type below...)" and custom_intake else selected_intake
    final_strategy = custom_strategy.strip() if selected_strategy == "Other (Type below...)" and custom_strategy else selected_strategy
    final_env = input_env_nav.strip() if input_env_nav else "Not Specified"
    
    new_match_entry = {
        "Match Number": int(input_match),
        "Team Number": clean_team,
        "Main Strategy": final_strategy,
        "Drive Train": final_drive,
        "Intake": final_intake,
        "Env Navigation": final_env,
        "Scout Points (0-100)": float(input_score),
        "Defensive Score": float(input_defense),
        "Notes": input_notes
    }
    
    # Append the new unique match log into historical memory database array
    st.session_state["match_scouting_history"] = pd.concat([st.session_state["match_scouting_history"], pd.DataFrame([new_match_entry])], ignore_index=True)
    
    if input_notes:
        st.session_state["important_notes"].insert(0, {
            "Category": f"🎮 Match {input_match} Log",
            "Team": clean_team,
            "Note": f"[{final_strategy}] {input_notes}"
        })
        
    st.sidebar.success(f"Match {input_match} metrics processed for Team {clean_team}!")
# -----------------------------------------------------------------------------
# ADVANCED MULTI-MATCH COMPUTE & AGGREGATION ENGINE
# -----------------------------------------------------------------------------
history_df = st.session_state["match_scouting_history"].copy()

# Group all match histories together to compute aggregate averages for every unique team
agg_rules = {
    "Scout Points (0-100)": "mean",
    "Defensive Score": "mean",
    "Main Strategy": lambda x: x.mode()[0] if not x.empty else "Unknown",
    "Drive Train": lambda x: x.iloc[-1] if not x.empty else "Unknown",
    "Intake": lambda x: x.iloc[-1] if not x.empty else "Unknown",
    "Env Navigation": lambda x: x.iloc[-1] if not x.empty else "Not Specified"
}
working_df = history_df.groupby("Team Number").agg(agg_rules).reset_index()

# Inject external metrics directly from the Blue Alliance Website API data
working_df["Live OPR (BlueAlliance)"] = working_df["Team Number"].map(live_oprs).fillna(0.0)
working_df["Official Standings Profile"] = "https://firstinspires.org"

# Min-Max Data Normalization to scale external API scores cleanly alongside human metrics
max_opr = working_df["Live OPR (BlueAlliance)"].max()
min_opr = working_df["Live OPR (BlueAlliance)"].min()
opr_range = max_opr - min_opr

if opr_range > 0:
    working_df["Normalized OPR"] = ((working_df["Live OPR (BlueAlliance)"] - min_opr) / opr_range) * 100
else:
    working_df["Normalized OPR"] = 50.0

# Dynamic Calculations Categories using aggregated rolling multi-match score indicators
working_df["Hybrid Offense Rating"] = round((working_df["Normalized OPR"] * 0.6) + (working_df["Scout Points (0-100)"] * 0.4), 2)
working_df["Defensive Power Index"] = round(working_df["Defensive Score"], 2)
working_df["Composite Power Rating"] = round((working_df["Hybrid Offense Rating"] * 0.5) + (working_df["Defensive Power Index"] * 0.5), 2)

# Global default sort ordering algorithm
working_df = working_df.sort_values(by="Composite Power Rating", ascending=False).reset_index(drop=True)

# -----------------------------------------------------------------------------
# MAIN DASHBOARD INTERFACE LAYOUT (Dropdown Control Flow Blocks)
# -----------------------------------------------------------------------------
main_col, notes_col = st.columns([3, 1.3])

with main_col:
    if strategy_focus == "Full Leaderboard":
        st.subheader("📊 Dynamic Global Event Leaderboard (Aggregated Averages)")
        st.markdown("*Ranked dynamically by rolling averages across multiple qualification matches mixed with min-max normalized live web server metrics.*")
        
        display_df = working_df.copy()
        display_df.index = display_df.index + 1
        display_df.index.name = "Global Rank"
        st.dataframe(display_df, use_container_width=True)
        
    elif strategy_focus == "Offensive Focus":
        st.subheader("🎯 Custom Offensive Strategy Picklist")
        st.markdown("*Sorted dynamically by Hybrid Offense Rating (Blended API metrics + mean cycle points).*")
        
        offense_df = working_df.sort_values(by="Hybrid Offense Rating", ascending=False).reset_index(drop=True)
        offense_df.index = offense_df.index + 1
        offense_df.index.name = "Offensive Rank"
        
        st.dataframe(offense_df[["Team Number", "Main Strategy", "Drive Train", "Env Navigation", "Live OPR (BlueAlliance)", "Scout Points (0-100)", "Hybrid Offense Rating"]], use_container_width=True)
        
    elif strategy_focus == "Defensive Focus":
        st.subheader("🛡️ Custom Defensive Strategy Picklist")
        st.markdown("*Sorted dynamically by rolling Defensive Power Index parameters tracked live on the field.*")
        
        defense_df = working_df.sort_values(by="Defensive Power Index", ascending=False).reset_index(drop=True)
        defense_df.index = defense_df.index + 1
        defense_df.index.name = "Defensive Rank"
        
        st.dataframe(defense_df[["Team Number", "Main Strategy", "Drive Train", "Intake", "Env Navigation", "Defensive Power Index"]], use_container_width=True)
        
    elif strategy_focus == "Match Alliance Matcher":
        st.subheader("Automated Match Alliance Combinator Engine")
        st.markdown("Select prospective alliance partners to evaluate real-time strategic synergy and projected output.")
        
        team_list = working_df["Team Number"].unique()
        
        col1, col2, col3 = st.columns(3)
        with col1: t1 = st.selectbox("Alliance Station 1 (You)", team_list, key="s1")
        with col2: t2 = st.selectbox("Alliance Partner 2", team_list, key="s2")
        with col3: t3 = st.selectbox("Alliance Partner 3", team_list, key="s3")
        
        team_stats = working_df[working_df["Team Number"].isin([t1, t2, t3])]
        total_projected_opr = round(team_stats["Live OPR (BlueAlliance)"].sum(), 2)
        mean_offense = round(team_stats["Hybrid Offense Rating"].mean(), 2)
        mean_defense = round(team_stats["Defensive Power Index"].mean(), 2)
        
        st.markdown("### Projected Alliance Strength Matrix")
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric(label="Combined Alliance OPR (Live API)", value=f"{total_projected_opr} Points")
        with metric_col2:
            st.metric(label="Mean Alliance Offensive Index", value=f"{mean_offense} Pts")
        with metric_col3:
            st.metric(label="Mean Alliance Defensive Index", value=f"{mean_defense} Pts")
            
        st.dataframe(team_stats[["Team Number", "Main Strategy", "Env Navigation", "Live OPR (BlueAlliance)", "Hybrid Offense Rating", "Defensive Power Index", "Composite Power Rating"]], use_container_width=True, hide_index=True)

    # Secondary Content View: Raw Match Ledger History Breakdown
    st.markdown("---")
    st.subheader("📜 Raw Match Telemetry Log Ledger")
    st.markdown("Every independent qualification match sheet recorded by the scouter crew:")
    st.dataframe(st.session_state["match_scouting_history"].sort_values(by="Match Number", ascending=False), use_container_width=True, hide_index=True)

with notes_col:
    st.subheader("📌 Team Scouting Feed")
    st.markdown("Live tactical logs per team:")
    
    if st.session_state["important_notes"]:
        for item in st.session_state["important_notes"]:
            with st.container(border=True):
                st.markdown(f"**{item['Category']} | Team {item['Team']}**")
                st.write(item["Note"])
    else:
        st.info("No crucial notes logged for this event panel.")
