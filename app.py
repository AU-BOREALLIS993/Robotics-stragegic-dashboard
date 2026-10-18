import streamlit as st
import pandas as pd
import requests
import os

# Professional Page Customization
st.set_page_config(page_title="Wirewolves Strategic Dashboard", layout="wide")

st.title("Wirewolves Strategic Scouting Dashboard and Live Analytics Engine")
st.markdown("Master Production Engine: Integrated Match Pairing Matrix and Live Data Links")
st.markdown("---")

# -----------------------------------------------------------------------------
# GLOBAL MEMORY CACHE (Simulating Live Database)
# -----------------------------------------------------------------------------
# This allows users to add or update teams dynamically.
# Pre-populated with your initial scouting pool so the app isn't blank for judges.
if "master_scouting_data" not in st.session_state:
    st.session_state["master_scouting_data"] = pd.DataFrame([
        {"Team Number": "4541", "Main Strategy": "Defense", "Scout Score (0-100)": 75.0, "Notes": "Decent shooter under trench"},
        {"Team Number": "5338", "Main Strategy": "Shooter", "Scout Score (0-100)": 82.0, "Notes": "Tried shooting under trench early"},
        {"Team Number": "6863", "Main Strategy": "Shooter", "Scout Score (0-100)": 90.0, "Notes": "Really good shooting consistency"},
        {"Team Number": "7770", "Main Strategy": "Defense", "Scout Score (0-100)": 40.0, "Notes": "Low movement, does not shoot"},
        {"Team Number": "8592", "Main Strategy": "Gatherer", "Scout Score (0-100)": 55.0, "Notes": "Focused on gathering balls"},
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
            # Grab OPR calculations straight from the official blue alliance website data
            oprs = {str(k).strip(): round(v, 2) for k, v in data.get("oprs", {}).items()}
            return oprs
    except:
        pass
    return {}

live_oprs = fetch_live_tba_metrics(TBA_API_KEY, EVENT_KEY)

# -----------------------------------------------------------------------------
# SIDEBAR INTERACTIVE CONSOLES (Data Input)
# -----------------------------------------------------------------------------
st.sidebar.header("🏆 Strategic Selection")
strategy_focus = st.sidebar.selectbox(
    "Select Alliance Team Role",
    ["Full Leaderboard", "Offensive Focus", "Defensive Focus", "Match Alliance Matcher"]
)

st.sidebar.markdown("---")
st.sidebar.header("📝 Input Live Team Scout Data")
st.sidebar.markdown("Add a new team or overwrite existing data instantly:")

with st.sidebar.form(key="scout_input_form", clear_on_submit=True):
    input_team = st.text_input("Team Number *")
    input_strategy = st.selectbox("Primary Strategy", ["Shooter", "Gatherer", "Defense"])
    input_score = st.slider("Human Scout Performance Score", 0.0, 100.0, 70.0)
    input_notes = st.text_area("Strategic Observations")
    
    submit_team_data = st.form_submit_button(label="Update Leaderboard & Recalculate")

# Process the user data entry
if submit_team_data and input_team:
    clean_team = str(input_team).strip()
    
    # Create the new data dictionary row
    new_entry = {
        "Team Number": clean_team,
        "Main Strategy": input_strategy,
        "Scout Score (0-100)": input_score,
        "Notes": input_notes
    }
    
    # Drop existing row for this team if it exists to overwrite cleanly, then append new row
    current_df = st.session_state["master_scouting_data"]
    current_df = current_df[current_df["Team Number"] != clean_team]
    st.session_state["master_scouting_data"] = pd.concat([current_df, pd.DataFrame([new_entry])], ignore_index=True)
    
    # Automatically add to the live critical notes tracking feed per team
    if input_notes:
        st.session_state["important_notes"].insert(0, {
            "Category": "📈 Data Update",
            "Team": clean_team,
            "Note": input_notes
        })
        
    st.sidebar.success(f"Metrics processed! Team {clean_team} ranks recalculated.")

# -----------------------------------------------------------------------------
# DYNAMIC DATA COMPUTATION & RANKING ALGORITHMS
# -----------------------------------------------------------------------------
# Process and compile the working dataset frame
working_df = st.session_state["master_scouting_data"].copy()

# 1. Pull data directly from external source (The Blue Alliance) and map it per team
working_df["Live OPR (BlueAlliance)"] = working_df["Team Number"].map(live_oprs).fillna(0.0)

# 2. Advanced Custom Formula: Merges external web data with human scouting parameters
# Formula: 60% of external web performance data + 40% of internal team scout evaluations
def calculate_composite_rank(row):
    composite_metric = (row["Live OPR (BlueAlliance)"] * 0.6) + (row["Scout Score (0-100)"] * 0.4)
    return round(composite_metric, 2)

working_df["Composite Power Rating"] = working_df.apply(calculate_composite_rank, axis=1)

# 3. Dynamic Ranking: Sort the entire dataset globally based on our custom algorithm calculation
working_df = working_df.sort_values(by="Composite Power Rating", ascending=False).reset_index(drop=True)
working_df.index = working_df.index + 1  # Standardize rank ordering indexed from 1
working_df.index.name = "Global Rank"

# 4. External Reference standard lookups
working_df["Official FIRST Profile"] = "https://firstinspires.org"

# -----------------------------------------------------------------------------
# MAIN DASHBOARD INTERFACE LAYOUT
# -----------------------------------------------------------------------------
main_col, notes_col = st.columns([3, 1.3])

with main_col:
    if strategy_focus == "Full Leaderboard":
        st.subheader("📊 Dynamic Global Event Leaderboard")
        st.markdown("*Ranked dynamically using a composite index of 60% Blue Alliance live OPR data and 40% local scout parameters.*")
        st.dataframe(working_df, use_container_width=True, hide_index=False)
        
    elif strategy_focus == "Offensive Focus":
        st.subheader("🎯 Custom Offensive Strategy Picklist")
        offense_df = working_df[working_df["Main Strategy"].str.contains("Shooter|Offense", case=False, na=False)]
        st.dataframe(offense_df, use_container_width=True, hide_index=False)
        
    elif strategy_focus == "Defensive Focus":
        st.subheader("🛡️ Custom Defensive Strategy Picklist")
        defense_df = working_df[working_df["Main Strategy"].str.contains("Defense", case=False, na=False)]
        st.dataframe(defense_df, use_container_width=True, hide_index=False)
        
    elif strategy_focus == "Match Alliance Matcher":
        st.subheader("🤖 Automated Match Alliance Combinator Engine")
        st.markdown("Select prospective alliance partners to evaluate real-time strategic synergy and projected output.")
        
        team_list = working_df["Team Number"].unique()
        
        col1, col2, col3 = st.columns(3)
        with col1: t1 = st.selectbox("Alliance Station 1 (You)", team_list, key="s1")
        with col2: t2 = st.selectbox("Alliance Partner 2", team_list, key="s2")
        with col3: t3 = st.selectbox("Alliance Partner 3", team_list, key="s3")
        
        team_stats = working_df[working_df["Team Number"].isin([t1, t2, t3])]
        total_projected_opr = round(team_stats["Live OPR (BlueAlliance)"].sum(), 2)
        total_scout_score = round(team_stats["Scout Score (0-100)"].mean(), 2)
        
        st.markdown("### Projected Alliance Strength Matrix")
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric(label="Combined Alliance OPR (Live External Web Data)", value=f"{total_projected_opr} Points")
        with metric_col2:
            st.metric(label="Mean Alliance Human Scout Score", value=f"{total_scout_score} / 100")
            
        st.dataframe(team_stats[["Team Number", "Main Strategy", "Live OPR (BlueAlliance)", "Composite Power Rating"]], use_container_width=True, hide_index=True)

# Right Bulletin Column displaying critical text parameters tied to team metrics
with notes_col:
    st.subheader("📌 Team Scouting Feed")
    st.markdown("Live updates sorted per team:")
    
    if st.session_state["important_notes"]:
        for item in st.session_state["important_notes"]:
            with st.container(border=True):
                st.markdown(f"**{item['Category']} | Team {item['Team']}**")
                st.write(item["Note"])
    else:
        st.info("No crucial notes logged for this event panel.")
