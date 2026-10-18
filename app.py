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
if "master_scouting_data" not in st.session_state:
    st.session_state["master_scouting_data"] = pd.DataFrame([
        {"Team Number": "4541", "Main Strategy": "Defensive Anchor", "Drive Train": "Swerve Drive", "Intake": "Ground Intake", "Env Navigation": "Level 3 Climber", "Scout Points (0-100)": 75.0, "Defensive Score": 90.0, "Notes": "Decent shooter under trench"},
        {"Team Number": "5338", "Main Strategy": "Dedicated Scorer", "Drive Train": "West Coast Drive", "Intake": "Source Intake", "Env Navigation": "Low Stage Hub", "Scout Points (0-100)": 82.0, "Defensive Score": 45.0, "Notes": "Tried shooting under trench early"},
        {"Team Number": "6863", "Main Strategy": "Dedicated Scorer", "Drive Train": "Swerve Drive", "Intake": "Dual Intake (Both)", "Env Navigation": "Level 3 Climber + Trap", "Scout Points (0-100)": 95.0, "Defensive Score": 30.0, "Notes": "Really good shooting consistency"},
        {"Team Number": "7770", "Main Strategy": "Defensive Anchor", "Drive Train": "Mecanum Drive", "Intake": "Ground Intake", "Env Navigation": "No Climb (Heavy Floor)", "Scout Points (0-100)": 30.0, "Defensive Score": 85.0, "Notes": "Low movement, heavy field defense"},
        {"Team Number": "8592", "Main Strategy": "Feeder / Cycle Bot", "Drive Train": "Swerve Drive", "Intake": "Dual Intake (Both)", "Env Navigation": "Level 1 Park Only", "Scout Points (0-100)": 65.0, "Defensive Score": 60.0, "Notes": "Focused on gathering game elements"},
    ])

if "important_notes" not in st.session_state:
    st.session_state["important_notes"] = [
        {"Category": "🚨 Strategy Alert", "Team": "4541", "Note": "Intake chain loose in last match. Monitor closely."},
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
# SIDEBAR INTERACTIVE CONSOLES (Per-Team Data Input)
# -----------------------------------------------------------------------------
st.sidebar.header("🏆 Strategic Selection")
strategy_focus = st.sidebar.selectbox(
    "Select Alliance Team Role",
    ["Full Leaderboard", "Offensive Focus", "Defensive Focus", "Match Alliance Matcher"]
)

st.sidebar.markdown("---")
st.sidebar.header("📝 Input Live Team Scout Data")
st.sidebar.markdown("Log or update pit/match characteristics per team:")

with st.sidebar.form(key="scout_input_form", clear_on_submit=True):
    input_team = st.text_input("Team Number *")
    
    drive_options = ["Swerve Drive", "West Coast Drive", "Mecanum Drive", "Tank Drive (KitBot)", "Other (Type below...)"]
    selected_drive = st.selectbox("Drive Train Type", drive_options)
    custom_drive = st.text_input("If 'Other', specify Drivetrain:")
    
    intake_options = ["Ground Intake", "Source Intake", "Dual Intake (Both)", "No Intake (Defense Only)", "Other (Type below...)"]
    selected_intake = st.selectbox("Intake Configuration", intake_options)
    custom_intake = st.text_input("If 'Other', specify Intake:")
    
    strategy_options = ["Dedicated Scorer", "Feeder / Cycle Bot", "Defensive Anchor", "Other (Type below...)"]
    selected_strategy = st.selectbox("Observed Field Strategy", strategy_options)
    custom_strategy = st.text_input("If 'Other', specify Strategy:")
    
    input_env_nav = st.text_input("Match Env Navigation (e.g., Climber Level, Stage Zone, Obstacles)")
    
    st.markdown("##### Performance Metrics")
    input_score = st.slider("Offensive Cycle Score (0-100)", 0.0, 100.0, 70.0)
    input_defense = st.slider("Defensive Capability Score (0-100)", 0.0, 100.0, 50.0)
    
    input_notes = st.text_area("Strategic Observations / Pit Notes")
    
    submit_team_data = st.form_submit_button(label="Save Profile & Compute Rankings")

if submit_team_data and input_team:
    clean_team = str(input_team).strip()
    
    final_drive = custom_drive.strip() if selected_drive == "Other (Type below...)" and custom_drive else selected_drive
    final_intake = custom_intake.strip() if selected_intake == "Other (Type below...)" and custom_intake else selected_intake
    final_strategy = custom_strategy.strip() if selected_strategy == "Other (Type below...)" and custom_strategy else selected_strategy
    final_env = input_env_nav.strip() if input_env_nav else "Not Specified"
    
    new_entry = {
        "Team Number": clean_team,
        "Main Strategy": final_strategy,
        "Drive Train": final_drive,
        "Intake": final_intake,
        "Env Navigation": final_env,
        "Scout Points (0-100)": input_score,
        "Defensive Score": final_drive,
        "Notes": input_notes
    }
    
    current_df = st.session_state["master_scouting_data"]
    current_df = current_df[current_df["Team Number"] != clean_team]
    st.session_state["master_scouting_data"] = pd.concat([current_df, pd.DataFrame([new_entry])], ignore_index=True)
    
    if input_notes:
        st.session_state["important_notes"].insert(0, {
            "Category": "📈 Data Update",
            "Team": clean_team,
            "Note": f"[{final_strategy}] (Env: {final_env}) {input_notes}"
        })
        
    st.sidebar.success(f"Metrics processed! Team {clean_team} successfully integrated.")
# -----------------------------------------------------------------------------
# ADVANCED MULTI-CATEGORY COMPUTE ENGINE
# -----------------------------------------------------------------------------
working_df = st.session_state["master_scouting_data"].copy()

working_df["Live OPR (BlueAlliance)"] = working_df["Team Number"].map(live_oprs).fillna(0.0)
working_df["Official Standings Profile"] = "https://firstinspires.org"

working_df["Hybrid Offense Rating"] = round((working_df["Live OPR (BlueAlliance)"] * 0.6) + (working_df["Scout Points (0-100)"] * 0.4), 2)
working_df["Defensive Power Index"] = round(working_df["Defensive Score"], 2)
working_df["Composite Power Rating"] = round((working_df["Hybrid Offense Rating"] * 0.5) + (working_df["Defensive Power Index"] * 0.5), 2)

working_df = working_df.sort_values(by="Composite Power Rating", ascending=False).reset_index(drop=True)

# -----------------------------------------------------------------------------
# MAIN DASHBOARD INTERFACE LAYOUT (Dropdown Control Flow Blocks)
# -----------------------------------------------------------------------------
main_col, notes_col = st.columns([3, 1.3])

with main_col:
    if strategy_focus == "Full Leaderboard":
        st.subheader("📊 Dynamic Global Event Leaderboard")
        st.markdown("*Ranked dynamically using an integrated master configuration of local scouter variables and live web server metrics.*")
        
        display_df = working_df.copy()
        display_df.index = display_df.index + 1
        display_df.index.name = "Global Rank"
        st.dataframe(display_df, use_container_width=True)
        
    elif strategy_focus == "Offensive Focus":
        st.subheader("🎯 Custom Offensive Strategy Picklist")
        st.markdown("*Sorted dynamically by Hybrid Offense Rating (Blended API metrics + localized cycle points).*")
        
        offense_df = working_df.sort_values(by="Hybrid Offense Rating", ascending=False).reset_index(drop=True)
        offense_df.index = offense_df.index + 1
        offense_df.index.name = "Offensive Rank"
        
        st.dataframe(offense_df[["Team Number", "Main Strategy", "Drive Train", "Env Navigation", "Live OPR (BlueAlliance)", "Scout Points (0-100)", "Hybrid Offense Rating"]], use_container_width=True)
        
    elif strategy_focus == "Defensive Focus":
        st.subheader("🛡️ Custom Defensive Strategy Picklist")
        st.markdown("*Sorted dynamically by Defensive Power Index parameters tracked live on the field.*")
        
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
