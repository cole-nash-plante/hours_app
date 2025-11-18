import streamlit as st
import sqlite3
from datetime import datetime

# -----------------------------
# Database Setup
# -----------------------------
DB_NAME = "charge_hours.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS charge_hours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            project TEXT,
            hours REAL,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_charge_hour(date, project, hours, notes):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO charge_hours (date, project, hours, notes)
        VALUES (?, ?, ?, ?)
    """, (date, project, hours, notes))
    conn.commit()
    conn.close()

def get_charge_hours():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT date, project, hours, notes FROM charge_hours ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Initialize DB
init_db()

# -----------------------------
# Sidebar Navigation
# -----------------------------
st.sidebar.title("Navigation")
pages = ["Track Hours", "Reports", "Settings", "Placeholder Page 1", "Placeholder Page 2"]
selected_page = st.sidebar.radio("Go to", pages)

# -----------------------------
# Page: Track Hours
# -----------------------------
if selected_page == "Track Hours":
    st.title("Track Your Charge Hours")

    st.subheader("Add New Entry")
    date = st.date_input("Date", datetime.today())
    project = st.text_input("Project Name")
    hours = st.number_input("Hours Worked", min_value=0.0, step=0.25)
    notes = st.text_area("Notes")

    if st.button("Save Entry"):
        add_charge_hour(str(date), project, hours, notes)
        st.success("Entry saved successfully!")

    st.subheader("Recent Entries")
    data = get_charge_hours()
    if data:
        st.table(data)
    else:
        st.info("No entries yet.")

# -----------------------------
# Page: Reports (Placeholder)
# -----------------------------
elif selected_page == "Reports":
    st.title("Reports")
    st.write("This page will show summaries, charts, and analytics. (Coming soon!)")

# -----------------------------
# Page: Settings (Placeholder)
# -----------------------------
elif selected_page == "Settings":
    st.title("Settings")
    st.write("Configure app preferences here. (Coming soon!)")

# -----------------------------
# Placeholder Pages
# -----------------------------
elif selected_page == "Placeholder Page 1":
    st.title("Placeholder Page 1")
    st.write("Content to be added later.")

elif selected_page == "Placeholder Page 2":
    st.title("Placeholder Page 2")
    st.write("Content to be added later.")