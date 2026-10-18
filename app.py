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
