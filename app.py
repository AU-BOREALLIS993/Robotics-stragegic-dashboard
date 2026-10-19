import streamlit as st
import pandas as pd
import requests

# 1. Page Configuration & Custom Branding
st.set_page_config(
    page_title="Wirewolves Strategic Scouting Dashboard", 
    layout="wide", 
    page_icon="🐺"
)

st.title("Wirewolves Strategic Scouting Dashboard and Live Analytics Engine")
st.markdown("### Master Production Engine: Integrated Match Pairing Matrix and Live Data Links")
st.markdown("---")

# 2. Dynamic Memory Core (Maintains database state across page clicks and navigation changes)
if "match_scouting_history" not in st.session_state:
    st.session_state["match_scouting_history"] = pd.DataFrame([
        {"Match Number": 1, "Team Number": "4541", "Main Strategy": "Defensive Anchor", "Drive Train": "Swerve Drive", "Intake": "Ground Intake", "Env Navigation": "Level 3 Climber", "Scout Points (0-100)": 70.0, "Defensive Score": 95.0, "Notes": "Heavy lock defense"},
        {"Match Number": 5, "Team Number": "4541", "Main Strategy": "Defensive Anchor", "Drive Train": "Swerve Drive", "Intake": "Ground Intake", "Env Navigation": "Level 3 Climber", "Scout Points (0-100)": 75.0, "Defensive Score": 85.0, "Notes": "Decent shooter under trench"},
        {"Match Number": 2, "Team Number": "5338", "Main Strategy": "Dedicated Scorer", "Drive Train": "West Coast Drive", "Intake": "Source Intake", "Env Navigation": "Low Stage Hub", "Scout Points (0-100)": 80.0, "Defensive Score": 40.0, "Notes": "Fast cycles"},
        {"Match Number": 6, "Team Number": "5338", "Main Strategy": "Dedicated Scorer", "Drive Train": "West Coast Drive", "Intake": "Source Intake", "Env Navigation": "Low Stage Hub", "Scout Points (0-100)": 84.0, "Defensive Score": 50.0, "Notes": "Tried shooting under trench early"},
        {"Match Number": 3, "Team Number": "6863", "Main Strategy": "Dedicated Scorer", "Drive Train": "Swerve Drive", "Intake": "Dual Intake (Both)", "Env Navigation": "Level 3 Climber + Trap", "Scout Points (0-100)": 95.0, "Defensive Score": 30.0, "Notes": "100% accuracy near subwoofer"},
        {"Match Number": 4, "Team Number": "7770", "Main Strategy": "Defensive Anchor", "Drive Train": "Mecanum Drive", "Intake": "Ground Intake", "Env Navigation": "No Climb", "Scout Points (0-100)": 30.0, "Defensive Score": 85.0, "Notes": "Low movement, static zone block"},
        {"Match Number": 7, "Team Number": "8592", "Main Strategy": "Feeder / Cycle Bot", "Drive Train": "Swerve Drive", "Intake": "Dual Intake (Both)", "Env Navigation": "Level 1 Park", "Scout Points (0-100)": 65.0, "Defensive Score": 60.0, "Notes": "Focused on gathering pieces"}
    ])

if "important_notes" not in st.session_state:
    st.session_state["important_notes"] = [
        {"Category": "🚨 Strategy Alert", "Team": "4541", "Note": "Intake chain loose in match 5. Monitor closely."},
        {"Category": "🏟️ Arena Update", "Team": "General", "Note": "Trench floor clearance is slightly uneven on Red side."}
    ]

# 3. Live External Web Server Interface (The Blue Alliance)
TBA_API_KEY = "N31fXme12ELSzymWwdD8PHoJSG5bSI5quSTnudyoYbxJrEzbqGDo29p1GL2sQJi"
EVENT_KEY = "2026ndsv"

@st.cache_data(ttl=60)
def fetch_live_tba_metrics(api_key, event_key):
    headers = {"X-TBA-Auth-Key": api_key}
    url = f"https://thebluealliance.com{event_key}/oprs"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return {str(k).strip(): round(v, 2) for k, v in data.get("oprs", {}).items()}
    except:
        pass
    return {}

live_oprs = fetch_live_tba_metrics(TBA_API_KEY, EVENT_KEY)

# 4. Interactive Sidebar Panel
st.sidebar.header("🏆 Strategic Selection")
strategy_focus = st.sidebar.selectbox(
    "Select Alliance Team Role",
    ["Full Leaderboard", "Offensive Focus", "Defensive Focus", "Match Alliance Matcher"]
)

st.sidebar.markdown("---")
st.sidebar.header("📝 Input Live Match Scout Data")

with st.sidebar.form(key="scout_input_form", clear_on_submit=True):
    input_match = st.number_input("Qualification Match Number *", min_value=1, step=1, value=1)
    input_team = st.text_input("Team Number *")
    
    selected_drive = st.selectbox("Drive Train Type", ["Swerve Drive", "West Coast Drive", "Mecanum Drive", "Tank Drive (KitBot)", "Other (Type below...)"])
    custom_drive = st.text_input("If 'Other', specify Drivetrain:")
    
    selected_intake = st.selectbox("Intake Configuration", ["Ground Intake", "Source Intake", "Dual Intake (Both)", "No Intake (Defense Only)", "Other (Type below...)"])
    custom_intake = st.text_input("If 'Other', specify Intake:")
    
    selected_strategy = st.selectbox("Observed Match Strategy", ["Dedicated Scorer", "Feeder / Cycle Bot", "Defensive Anchor", "Other (Type below...)"])
    custom_strategy = st.text_input("If 'Other', specify Strategy:")
    
    input_env_nav = st.text_input("Match Env Navigation (e.g., Climber Level, Stage Zone)")
    
    st.markdown("##### Performance Metrics")
    input_score = st.slider("Offensive Cycle Score (0-100)", 0.0, 100.0, 70.0)
    input_defense = st.slider("Defensive Capability Score (0-100)", 0.0, 100.0, 50.0)
    input_notes = st.text_area("Match Observations / Notes")
    
    submit_match_data = st.form_submit_button(label="Log Match & Update Leaderboard")

# 5. Form Submittal Handling Engine
if submit_match_data:
    if not input_team.strip():
        st.sidebar.error("⚠️ Team Number is required to log match data!")
    else:
        clean_team = str(input_team).strip()
        final_drive = custom_drive.strip() if selected_drive == "Other (Type below...)" and custom_drive else selected_drive
        final_intake = custom_intake.strip() if selected_intake == "Other (Type below...)" and custom_intake else selected_intake
        final_strategy = custom_strategy.strip() if selected_strategy == "Other (Type below...)" and custom_strategy else selected_strategy
        final_env = input_env_nav.strip() if input_env_nav else "Not Specified"
        
        new_entry = {
            "Match Number": int(input_match), "Team Number": clean_team, "Main Strategy": final_strategy,
            "Drive Train": final_drive, "Intake": final_intake, "Env Navigation": final_env,
            "Scout Points (0-100)": float(input_score), "Defensive Score": float(input_defense), "Notes": input_notes
        }
        
        st.session_state["match_scouting_history"] = pd.concat([
            st.session_state["match_scouting_history"], pd.DataFrame([new_entry])
        ], ignore_index=True)
        
        if input_notes:
            st.session_state["important_notes"].insert(0, {
                "Category": "📝 Match Log", "Team": clean_team, "Note": f"[{final_strategy}] {input_notes}"
            })
        st.sidebar.success(f"✅ Match {input_match} saved for Team {clean_team}!")
