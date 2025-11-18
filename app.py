import streamlit as st
import pandas as pd
from datetime import datetime
import os

# -----------------------------
# Data Setup
# -----------------------------
DATA_DIR = "data"
CLIENTS_FILE = os.path.join(DATA_DIR, "clients.csv")
HOURS_FILE = os.path.join(DATA_DIR, "hours.csv")
GOALS_FILE = os.path.join(DATA_DIR, "goals.csv")

os.makedirs(DATA_DIR, exist_ok=True)

# Initialize CSVs if they don't exist
for file, cols in [
    (CLIENTS_FILE, ["Client"]),
    (HOURS_FILE, ["Date", "Client", "Hours", "Description"]),
    (GOALS_FILE, ["Month", "GoalHours"])
]:
    if not os.path.exists(file):
        pd.DataFrame(columns=cols).to_csv(file, index=False)

# -----------------------------
# Sidebar Navigation
# -----------------------------
st.sidebar.title("Navigation")
pages = ["Data Entry", "Reports", "To-Do", "History"]
selected_page = st.sidebar.radio("Go to", pages)

# -----------------------------
# Page: Data Entry
# -----------------------------
if selected_page == "Data Entry":
    st.title("Data Entry")

    # Form 1: Add New Client
    st.subheader("Add New Client")
    new_client = st.text_input("Client Name")
    if st.button("Add Client"):
        if new_client.strip():
            df_clients = pd.read_csv(CLIENTS_FILE)
            if new_client not in df_clients["Client"].values:
                df_clients.loc[len(df_clients)] = [new_client]
                df_clients.to_csv(CLIENTS_FILE, index=False)
                st.success(f"Client '{new_client}' added!")
            else:
                st.warning("Client already exists.")
        else:
            st.error("Please enter a valid client name.")

    # Form 2: Log Hours
    st.subheader("Log Hours")
    df_clients = pd.read_csv(CLIENTS_FILE)
    if len(df_clients) == 0:
        st.warning("Add clients first!")
    else:
        client = st.selectbox("Select Client", df_clients["Client"].tolist())
        date = st.date_input("Date", datetime.today())
        hours = st.number_input("Hours Worked", min_value=0.0, step=0.25)
        description = st.text_area("Description of Work")
        if st.button("Save Hours"):
            df_hours = pd.read_csv(HOURS_FILE)
            df_hours.loc[len(df_hours)] = [str(date), client, hours, description]
            df_hours.to_csv(HOURS_FILE, index=False)
            st.success("Hours logged successfully!")

    # Form 3: Set Hour Goals
    st.subheader("Set Hour Goals")
    month = st.selectbox("Month", [f"{m:02d}" for m in range(1, 13)])
    goal_hours = st.number_input("Goal Hours", min_value=0.0, step=1.0)
    if st.button("Save Goal"):
        df_goals = pd.read_csv(GOALS_FILE)
        df_goals.loc[len(df_goals)] = [month, goal_hours]
        df_goals.to_csv(GOALS_FILE, index=False)
        st.success("Goal saved successfully!")

# -----------------------------
# Placeholder Pages
# -----------------------------
elif selected_page == "Reports":
    st.title("Reports")
    st.write("Coming soon: charts and summaries.")

elif selected_page == "To-Do":
    st.title("To-Do")
    st.write("Coming soon: task management.")

elif selected_page == "History":
    st.title("History")
    st.write("Coming soon: view past entries.")
