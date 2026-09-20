St.set_page_config(page_title=”Wirewolves Strategy Dashboard”, layout=”wide”)

St.title(“🐺 FRC Strategic Scouting Dashboard & Picklist Generator”)
St.markdown(“---“)
# 1. Load the spreadsheet data safely using Pandascsv_filename = “scouting_data.csv”
If os.path.exists(csv_filename):
    # Read CSV and make sure Team Number doesn’t lose formatting
    Df = pd.read_csv(csv_filename)
    Df[“Team Number”] = df[“Team Number”].astype(str)else:
    St.error(f”Could not find {csv_filename}. Please ensure it is in the repository.”)
    Df = pd.DataFrame()
# 2. Build the Strategic Sidebar Framework
St.sidebar.header(“📊 Strategic Control Panel”)
# Strategy Dropdown Selectorstrategy_focus = st.sidebar.selectbox(
    “Select Alliance Team Role:”,
    [“Full Leaderboard”, “Offensive Focus”, “Defensive Focus”]
)

St.sidebar.markdown(“---“)
St.sidebar.header(“📝 Input New Scouting Data”)
# Professional Input Formwith st.sidebar.form(key=”scouting_form”, clear_on_submit=True):
    New_team = st.text_input(“Team Number*”)
    New_strategy = st.selectbox(“Main Strategy”, [“Shooter”, “Gatherer”, “Defense”, “Did nothing”])
    New_movement = st.text_input(“Strategy / Movement Notes”)
    
    Submit_button = st.form_submit_with_rows = st.form_submit_button(label=”📥 Save Team Data”)
# Handle form submission and append to CSV datasetif submit_button:
    If new_team:
        # Create a dictionary matching the CSV data structure
        New_row = {col: “” for col in df.columns}
        New_row[“Team Number”] = str(new_team)
        New_row[“Main strategy”] = new_strategy
        New_row[“Strategy / Movement”] = new_movement
        
        # Convert dictionary to data frame row and append
        New_df = pd.DataFrame([new_row])
        Updated_df = pd.concat([df, new_df], ignore_index=True)
        Updated_df.to_csv(csv_filename, index=False)
        St.sidebar.success(f”Team {new_team} added successfully! Refreshing data…”)
        St.rerun()
    Else:
        St.sidebar.error(“Team Number is required!”)
# 3. Process High-Quality Filtering & Sorting Logicif not df.empty:
    Filtered_df = df.copy()
    
    If strategy_focus == “Offensive Focus”:
        St.subheader(“🎯 Custom Offensive Picklist (Ranked by High-Yield Shooters)”)
        # Filter out teams that aren’t offensive
        Filtered_df = filtered_df[filtered_df[“Main strategy”].str.contains(“Shooter|Offense”, case=False, na=False)]
        # Professional sorting logic handling range metrics elegantly
        Filtered_df = filtered_df.sort_values(by=”Robot Points / Shots per match”, ascending=False)
        
    Elif strategy_focus == “Defensive Focus”:
        St.subheader(“🛡️ Custom Defensive Picklist (Ranked by Lockdown Defenders)”)
        # Filter for high-impact defensive ratings
        Filtered_df = filtered_df[
            (filtered_df[“Defensive Bot”].str.contains(“Yes”, case=False, na=False)) | 
            (filtered_df[“How effective? (Defense)”].str.contains(“High|Medium”, case=False, na=False))
        ]
    Else:
        St.subheader(“📋 Overall Event Standings”)

    # 4. Display the clean data frame table beautifully on screen
    St.dataframe(filtered_df, use_container_width=True, hide_index=True)
