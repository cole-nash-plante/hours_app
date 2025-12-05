import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
import base64
from datetime import datetime, date
import calendar
import plotly.graph_objects as go
import plotly.express as px
# -------------------------------------------------
# GitHub Config (from Streamlit Secrets)
# -------------------------------------------------

BRANCH = "main"

# -------------------------------------------------
# Data Setup
# -------------------------------------------------
DATA_DIR = "data"
CLIENTS_FILE = os.path.join(DATA_DIR, "clients.csv")
HOURS_FILE = os.path.join(DATA_DIR, "hours.csv")
GOALS_FILE = os.path.join(DATA_DIR, "goals.csv")
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.csv")
TODOS_FILE = os.path.join(DATA_DIR, "todos.csv")
os.makedirs(DATA_DIR, exist_ok=True)
st.set_page_config(layout="wide")

# -------------------------------------------------
# Custom CSS for Dark Theme and Boxed Forms
# -------------------------------------------------
# -------------------------------------------------
# Improved Dark Theme CSS
# -------------------------------------------------



# -------------------------------------------------
# GitHub Functions
# -------------------------------------------------

import streamlit as st
import pandas as pd
from datetime import datetime, date
import os, requests, base64, calendar
import plotly.graph_objects as go
import plotly.express as px

# -------------------------------------------------
# GitHub Config — public-safe defaults
# -------------------------------------------------
BRANCH = "main"

# Your public repo full name (owner/repo)
GITHUB_REPO = "cole-nash-plante/hours_app"

# Read token from Streamlit Cloud secrets if set.
# On a public repo, reads can be unauthenticated; writes need a token.
GITHUB_TOKEN = None
try:
    # You can store this in Streamlit Cloud → App → Settings → Edit secrets
    GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", None)
except Exception:
    GITHUB_TOKEN = None

# Build headers conditionally. Add 'Accept' for GitHub API v3.
BASE_HEADERS = {"Accept": "application/vnd.github.v3+json"}
AUTH_HEADERS = (
    {**BASE_HEADERS, "Authorization": f"token {GITHUB_TOKEN}"}
    if GITHUB_TOKEN
    else BASE_HEADERS
)

# -------------------------------------------------
# Data Setup
# -------------------------------------------------
DATA_DIR = "data"
CLIENTS_FILE = os.path.join(DATA_DIR, "clients.csv")
HOURS_FILE = os.path.join(DATA_DIR, "hours.csv")
GOALS_FILE = os.path.join(DATA_DIR, "goals.csv")
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.csv")
TODOS_FILE = os.path.join(DATA_DIR, "todos.csv")
os.makedirs(DATA_DIR, exist_ok=True)
st.set_page_config(layout="wide")

# -------------------------------------------------
# GitHub Functions
# -------------------------------------------------
def fetch_from_github(file_path: str):
    """
    Fetch file content from the public GitHub repo and save locally.
    Works without a token if the repo/content is public.
    """
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}?ref={BRANCH}"
    resp = requests.get(url, headers=AUTH_HEADERS)

    if resp.status_code == 200:
        j = resp.json()
        content_b64 = j.get("content", "")
        if content_b64:
            content = base64.b64decode(content_b64).decode("utf-8")
            # Ensure parent dirs exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            st.warning(f"No content for {file_path} in GitHub response.")
    elif resp.status_code == 404:
        # File not yet in repo; create locally and push later if desired
        st.info(f"'{file_path}' not found in GitHub (404). Will create locally.")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if file_path.endswith(".css"):
            # start with empty css if missing
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("")
        # For CSVs, they’ll be created below from init_files
    else:
        st.warning(
            f"Could not fetch '{file_path}' (HTTP {resp.status_code}). "
            f"Response: {resp.text[:200]}"
        )

def push_to_github(file_path: str, commit_message: str):
    """
    Push local file to GitHub. Requires GITHUB_TOKEN with 'repo' scope.
    """
    if not GITHUB_TOKEN:
        st.error(
            "GitHub token not set. Add GITHUB_TOKEN in Streamlit secrets to enable pushing."
        )
        return False

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    # Read local content
    with open(file_path, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode("utf-8")

    # Check if file exists to get SHA
    get_resp = requests.get(url, headers=AUTH_HEADERS)
    sha = None
    if get_resp.status_code == 200:
        sha = get_resp.json().get("sha")

    payload = {"message": commit_message, "content": content_b64, "branch": BRANCH}
    if sha:
        payload["sha"] = sha

    put_resp = requests.put(url, json=payload, headers=AUTH_HEADERS)
    if put_resp.status_code in (200, 201):
        return True
    st.error(
        f"Failed to push '{file_path}' (HTTP {put_resp.status_code}). "
        f"Response: {put_resp.text[:300]}"
    )
    return False

def apply_css_from_github(css_path="data/style.css"):
    """
    Fetch CSS from GitHub (public read) and apply to the Streamlit app.
    """
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{css_path}?ref={BRANCH}"
    resp = requests.get(url, headers=AUTH_HEADERS)
    if resp.status_code == 200:
        content = base64.b64decode(resp.json()["content"]).decode("utf-8")
        st.markdown(f"<style>{content}</style>", unsafe_allow_html=True)
    elif os.path.exists(css_path):
        # Fallback: local CSS
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS file '{css_path}' not found in GitHub or locally.")

# -------------------------------------------------
# Initialize Data
# -------------------------------------------------
def apply_css_from_github(css_path="data/style.css"):
    """Fetch CSS from GitHub using token and apply to Streamlit app."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{css_path}?ref={BRANCH}"
    response = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    
    if response.status_code == 200:
        # Decode base64 content
        content = base64.b64decode(response.json()["content"]).decode("utf-8")
        # Inject CSS into Streamlit
        st.markdown(f"<style>{content}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS file '{css_path}' not found in GitHub.")

# Call this early in your app (after st.set_page_config)
#apply_css_from_github()




# Sync Files from GitHub
for file in ["data/clients.csv", "data/hours.csv", "data/goals.csv", "data/categories.csv", "data/todos.csv", "data/style.css"]:
    fetch_from_github(file)

st.markdown('<link rel="stylesheet" href="YOUR_GITHUB_RAW_CSS_URL">', unsafe_allow_html=True)
# Ensure files exist locally

# Sync public files from GitHub
for file in [
    "data/clients.csv",
    "data/hours.csv",
    "data/goals.csv",
    "data/categories.csv",
    "data/todos.csv",
    "data/style.css",
]:
    fetch_from_github(file)

# Optionally apply CSS from the synced file


# Ensure files exist locally (create empty CSVs if missing, then attempt to push if you have a token)
init_files = [
    ("data/clients.csv", ["Client"]),
    ("data/hours.csv", ["Date", "Client", "Hours", "Description"]),
    ("data/goals.csv", ["Month", "GoalHours"]),
    ("data/categories.csv", ["Client", "Category"]),
    ("data/todos.csv", ["Client", "Category", "Task", "Priority", "DateCreated", "DateCompleted"]),
]
for file, cols in init_files:
    if not os.path.exists(file):
        os.makedirs(os.path.dirname(file), exist_ok=True)
        pd.DataFrame(columns=cols).to_csv(file, index=False)
        # Push only if token exists (safe on public)
        push_to_github(file, f"Initialize {file}")

# -------------------------------------------------
# Sidebar Navigation
# -------------------------------------------------
st.sidebar.title("Navigation")
pages = ["Home", "Meeting Notes", "Reports", "Data Entry", "Archive"]
selected_page = st.sidebar.radio("Go to", pages)



st.markdown("""
<style>
/* Dark Theme for Streamlit App */
:root {
  --bg-primary: #0f0f23;
  --bg-secondary: #1a1a2e;
  --bg-tertiary: #16213e;
  --text-primary: #FFFFFF;
  --text-secondary: #a1a1aa;
  --accent: #9333ea;
  --accent-hover: #a855f7;
  --border: #27272a;
  
  /* Priority Colors */
  --priority-high: #ef4444;
  --priority-medium: #f97316;
  --priority-low: #22c55e;
  
  /* Client Colors - Match these in your Streamlit app */
  --client-1: #3b82f6;
  --client-2: #10b981;
  --client-3: #f59e0b;
  --client-4: #ec4899;
  --client-5: #8b5cf6;
  --client-6: #06b6d4;
}



.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea textarea,
.stSelectbox > div > div,
.stDateInput > div > div > input {
    color: #FFFFFF !important; /* Force white text */
    font-size: 16px !important;
    padding: 0.75rem !important;
}
/* Main Background */
.stApp {
  background-color: var(--bg-primary) !important;
  color: var(--text-primary) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
  background-color: var(--bg-secondary) !important;
  border-right: 1px solid var(--border) !important;
}

/* Sidebar text and navigation */
section[data-testid="stSidebar"] * {
  color: var(--text-primary) !important;
}

section[data-testid="stSidebar"] label {
  color: var(--text-primary) !important;
  font-weight: 500 !important;
}

/* Radio buttons in sidebar navigation */
section[data-testid="stSidebar"] [role="radiogroup"] label {
  color: var(--text-primary) !important;
}

/* Selected navigation item */
section[data-testid="stSidebar"] [data-baseweb="radio"] input:checked ~ div {
  background-color: var(--accent) !important;
  border-color: var(--accent) !important;
}

/* Headers */
h1, h2, h3, h4, h5, h6 {
  color: var(--text-primary) !important;
  font-weight: 600 !important;
}

h1 {
  font-size: 2rem !important;
  margin-bottom: 1.5rem !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  background-color: var(--bg-secondary) !important;
  border-radius: 0.5rem !important;
  padding: 0.25rem !important;
  gap: 0.5rem !important;
}

.stTabs [data-baseweb="tab"] {
  background-color: transparent !important;
  color: var(--text-secondary) !important;
  border-radius: 0.375rem !important;
  padding: 0.5rem 1rem !important;
  transition: all 0.2s !important;
}

.stTabs [aria-selected="true"] {
  background-color: var(--accent) !important;
  color: white !important;
}

/* Input Fields */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea textarea,
.stSelectbox > div > div,
.stDateInput > div > div > input {
  background-color: var(--bg-tertiary) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border) !important;
  border-radius: 0.375rem !important;
  padding: 0.5rem !important;
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea textarea:focus,
.stSelectbox > div > div:focus,
.stDateInput > div > div > input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 1px var(--accent) !important;
}

/* Buttons */
.stButton > button {
  background-color: var(--accent) !important;
  color: white !important;
  border: none !important;
  border-radius: 0.375rem !important;
  padding: 0.5rem 1.5rem !important;
  font-weight: 500 !important;
  transition: all 0.2s !important;
}

.stButton > button:hover {
  background-color: var(--accent-hover) !important;
  transform: translateY(-1px) !important;
}

/* Data Editor / DataFrame */
.stDataFrame {
  background-color: var(--bg-secondary) !important;
  border-radius: 0.5rem !important;
  overflow: hidden !important;
}

.stDataFrame [data-testid="stDataFrameResizable"] {
  background-color: var(--bg-secondary) !important;
}



/* Priority Color Coding for To-Do List */
.todo-high {
  border-left: 4px solid var(--priority-high) !important;
  background-color: rgba(239, 68, 68, 0.1) !important;
  padding: 0.75rem !important;
  margin: 0.5rem 0 !important;
  border-radius: 0.375rem !important;
}

.todo-medium {
  border-left: 4px solid var(--priority-medium) !important;
  background-color: rgba(249, 158, 6, 0.1) !important;
  padding: 0.75rem !important;
  margin: 0.5rem 0 !important;
  border-radius: 0.375rem !important;
}

.todo-low {
  border-left: 4px solid var(--priority-low) !important;
  background-color: rgba(34, 197, 94, 0.1) !important;
  padding: 0.75rem !important;
  margin: 0.5rem 0 !important;
  border-radius: 0.375rem !important;
}

/* Priority Badges */
.priority-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.priority-high-badge {
  background-color: var(--priority-high);
  color: red;
}

.priority-medium-badge {
  background-color: var(--priority-medium);
  color: green;
}

.priority-low-badge {
  background-color: var(--priority-low);
  color: white;
}

.stMetric label {
  color: var(--text-secondary) !important;
}

.stMetric [data-testid="stMetricValue"] {
  color: var(--text-primary) !important;
}

/* Charts */
.js-plotly-plot .plotly {
  background-color: var(--bg-secondary) !important;
  border-radius: 0.5rem !important;
}

.js-plotly-plot .plotly .bg {
  fill: var(--bg-secondary) !important;
}


/* Success/Error Messages */
.stSuccess {
  background-color: rgba(34, 197, 94, 0.1) !important;
  border-left: 4px solid var(--priority-low) !important;
  color: var(--text-primary) !important;
}

.stError {
  background-color: rgba(239, 68, 68, 0.1) !important;
  border-left: 4px solid var(--priority-high) !important;
  color: var(--text-primary) !important;
}

.stWarning {
  background-color: rgba(249, 158, 6, 0.1) !important;
  border-left: 4px solid var(--priority-medium) !important;
  color: var(--text-primary) !important;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-primary);
}

::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #3f3f46;
}

/* Radio Buttons and Checkboxes */
.stRadio > div,
.stCheckbox > div {
  color: var(--text-primary) !important;
}


/* Make all form labels white */
.stTextInput label,
.stDateInput label,
.stNumberInput label,
.stTextArea label,
.stSelectbox label,
.stSlider label {
    color: #FFFFFF !important;
    font-weight: 600; /* Optional: make them bold */
}

/* Override the problematic padding */
.stSelectbox > div > div {
    padding: 0 !important; /* Remove extra padding */
    display: flex !important;
    align-items: center !important;
}

/* Style the actual text inside the select box */
.stSelectbox div[data-baseweb="select"] span {
    color: #D3D3D3 !important;
    font-size: 16px !important;
    line-height: 1.4 !important;
}

/* Dropdown options */
ul[role="listbox"] li {
    color: #D3D3D3 !important;
    font-size: 16px !important;
}
</style>
""", unsafe_allow_html=True)



# Inject custom CSS for styling
st.markdown("""
<style>
/* Dark background for the entire app */
body {
    background-color: #121212;
    color: #e0e0e0;
}

/* Table styling */
[data-testid="stDataFrame"] table {
    border-collapse: collapse;
    width: 100%;
    background-color: #1e1e1e;
    color: #f5f5f5;
    border-radius: 8px;
    overflow: hidden;
}

/* Remove unnecessary borders */
[data-testid="stDataFrame"] table th, 
[data-testid="stDataFrame"] table td {
    border: none !important;
    padding: 8px 12px;
}

/* Header styling */
[data-testid="stDataFrame"] table th {
    font-size: 14px; /* Smaller headers */
    font-weight: 600;
    background-color: #2c2c2c;
    color: #ffffff;
    text-transform: uppercase;
}

/* Row hover effect */
[data-testid="stDataFrame"] table tr:hover {
    background-color: #333333;
}

/* Rounded corners for the table container */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Page: Data Entry
# -------------------------------------------------

if selected_page == "Home":
    # Load required data
    df_clients = pd.read_csv(CLIENTS_FILE)
    df_todos = pd.read_csv(TODOS_FILE)
    df_categories = pd.read_csv(CATEGORIES_FILE)
    df_hours = pd.read_csv(HOURS_FILE)

    # Ensure required columns exist in df_todos
    required_cols = ["Client", "Category", "Task", "Priority", "DateCreated", "DateCompleted", "Notes"]
    for col in required_cols:
        if col not in df_todos.columns:
            df_todos[col] = ""

    # -------------------------------
    # Log Hours Section
    # -------------------------------
    st.subheader("Log Hours")
    if len(df_clients) == 0:
        st.warning("Add clients first!")
    else:
        col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 3, 1])
        with col1:
            client = st.selectbox("Client", df_clients["Client"].tolist(), key="log_client")
        with col2:
            date_val = st.date_input("Date", datetime.today(), key="log_date")
        with col3:
            hours = st.number_input("Hours", min_value=0.0, step=0.25, key="log_hours")
        with col4:
            description = st.text_input("Description", key="log_description")
        with col5:
            if st.button("Save Hours", key="save_hours"):
                new_row = {"Date": str(date_val), "Client": client, "Hours": hours, "Description": description}
                df_hours = pd.concat([df_hours, pd.DataFrame([new_row])], ignore_index=True)
                df_hours.to_csv(HOURS_FILE, index=False)
                push_to_github("data/hours.csv", "Updated hours log")
                st.success("Hours logged successfully!")

    # -------------------------------
    # Add To-Do Item Section
    # -------------------------------
    st.subheader("Add To-Do Item")
    if len(df_clients) == 0:
        st.warning("Add clients first!")
    else:
        col_date, col_client, col_category, col_task, col_priority, col_btn = st.columns([0.8, 1.5, 1.5, 3, 1, 1])
        with col_date:
            todo_date = st.date_input("Date Created", datetime.today(), key="todo_date")
        with col_client:
            todo_client = st.selectbox("Client", df_clients["Client"].tolist(), key="todo_client")
        with col_category:
            client_categories = df_categories[df_categories["Client"] == todo_client]["Category"].tolist()
            todo_category = st.selectbox("Category", client_categories if client_categories else ["No categories"], key="todo_category")
        with col_task:
            todo_task = st.text_input("Task", key="todo_task")
        with col_priority:
            priority = st.slider("Priority", 1, 5, 3, key="todo_priority")
        with col_btn:
            if st.button("Add Task", key="add_task"):
                if todo_task.strip() and todo_category != "No categories":
                    df_todos.loc[len(df_todos)] = [todo_client, todo_category, todo_task, priority, str(todo_date), "", ""]
                    df_todos.to_csv(TODOS_FILE, index=False)
                    push_to_github("data/todos.csv", "Added new task")
                    st.success("Task added successfully!")
                else:
                    st.error("Please enter a valid task and category.")

    # -------------------------------
    # Active To-Dos Section
    # -------------------------------
    st.subheader("Active To-Dos")

    # Build dropdown from ALL clients (df_clients + df_todos)
    all_clients_with_tasks = sorted(set(df_clients["Client"].dropna().tolist() + df_todos["Client"].dropna().tolist()))
    if not all_clients_with_tasks:
        st.info("No clients available.")
    else:
        selected_clients = st.multiselect(
            "Filter by Client",
            all_clients_with_tasks,
            default=all_clients_with_tasks,
            key="filter_clients"
        )

        # Filter active todos for selected clients
        active_todos = df_todos[
            ((df_todos["DateCompleted"].isna()) | (df_todos["DateCompleted"] == "")) &
            (df_todos["Client"].isin(selected_clients))
        ].copy()

        if len(active_todos) == 0:
            st.info("No active tasks for selected clients.")
        else:
            cols = st.columns(len(selected_clients))
            for i, client in enumerate(selected_clients):
                with cols[i]:
                    color = df_clients.loc[df_clients["Client"] == client, "Color"].values[0] if "Color" in df_clients.columns else "#333333"
                    st.markdown(f"<div style='background-color:{color}; padding:10px; border-radius:5px;'><h4 style='color:white; font-size:20px;'>{client}</h4></div>", unsafe_allow_html=True)
                    client_tasks = active_todos[active_todos["Client"] == client].sort_values(by="Priority", ascending=False)
                    for idx, row in client_tasks.iterrows():
                        with st.expander(f"{row['Task']} (Priority: {row['Priority']})", expanded=False):
                            st.markdown(f"### Task: {row['Task']}")
                            st.write(f"Category: {row['Category']}")
                            st.write(f"Created: {row['DateCreated']}")
                            new_priority = st.slider("Priority", 1, 5, int(row['Priority']), key=f"priority_{client}_{idx}")
                            new_notes = st.text_area("Notes", value=row.get("Notes", ""), key=f"notes_{client}_{idx}")
                            if st.button("Save Changes", key=f"save_{client}_{idx}"):
                                df_todos.at[row.name, "Priority"] = new_priority
                                df_todos.at[row.name, "Notes"] = new_notes
                                df_todos.to_csv(TODOS_FILE, index=False)
                                push_to_github("data/todos.csv", "Updated task notes and priority")
                                st.success("Changes saved!")
                            if st.button("Mark as Complete", key=f"complete_{client}_{idx}"):
                                df_todos.at[row.name, "DateCompleted"] = str(datetime.today().date())
                                df_todos.to_csv(TODOS_FILE, index=False)
                                push_to_github("data/todos.csv", "Marked task as complete")
                                st.success("Task marked as complete!")
                            if st.button("Delete Task", key=f"delete_{client}_{idx}"):
                                df_todos = df_todos.drop(index=row.name)
                                df_todos.to_csv(TODOS_FILE, index=False)
                                push_to_github("data/todos.csv", "Deleted a task")
                                st.success("Task deleted!")

    # -------------------------------
    # Today's Hours Section
    # -------------------------------
    st.subheader("Today's Hours")
    today_str = datetime.today().strftime("%Y-%m-%d")
    df_today = df_hours[df_hours["Date"] == today_str]
    new_row = {"Date": today_str, "Client": "", "Hours": 0.0, "Description": ""}
    df_today_with_blank = pd.concat([df_today, pd.DataFrame([new_row])], ignore_index=True)
    edited_hours = st.data_editor(df_today_with_blank, num_rows="dynamic", key="editor_today")
    if st.button("Save Hours", key="save_hours_today"):
        edited_hours = edited_hours.dropna(subset=["Client"])
        edited_hours = edited_hours[edited_hours["Client"].str.strip() != ""]
        df_hours = df_hours[df_hours["Date"] != today_str]
        df_hours = pd.concat([df_hours, edited_hours], ignore_index=True)
        df_hours.to_csv(HOURS_FILE, index=False)
        push_to_github("data/hours.csv", "Updated today's hours")





#----------------------------------------------------
# Meeting Notes
#---------------------------------------------------
elif selected_page == "Meeting Notes":
    st.title("Meeting Notes")

    MEETINGS_FILE = os.path.join(DATA_DIR, "meetings.csv")
    if not os.path.exists(MEETINGS_FILE):
        pd.DataFrame(columns=["Date", "Client", "Meeting", "Notes"]).to_csv(MEETINGS_FILE, index=False)
        push_to_github("data/meetings.csv", "Created meetings file")

    df_meetings = pd.read_csv(MEETINGS_FILE)
    df_clients = pd.read_csv(CLIENTS_FILE)
    df_categories = pd.read_csv(CATEGORIES_FILE)
    df_todos = pd.read_csv(TODOS_FILE)

    if len(df_clients) == 0:
        st.warning("Add clients first!")
    else:
        # Select Client
        selected_client = st.selectbox("Select Client", df_clients["Client"].tolist(), key="meeting_client")

        # Header with color coding
        client_color = df_clients.loc[df_clients["Client"] == selected_client, "Color"].values[0]
        st.markdown(f"<div style='background-color:{client_color}; padding:10px; border-radius:5px;'><h4 style='color:white; font-size:20px;'>Meeting Notes for {selected_client}</h4></div>", unsafe_allow_html=True)

        # New Meeting Form (all on one line)
        st.subheader("New Meeting")
        col_date, col_title, col_btn = st.columns([1.2, 3, 1])
        with col_date:
            meeting_date = st.date_input("Date", datetime.today().date(), key="meeting_date")
        with col_title:
            meeting_title = st.text_input("Meeting Title", key="meeting_title")
        with col_btn:
            if st.button("Save Meeting", key="save_meeting"):
                if meeting_title.strip():
                    new_row = {"Date": str(meeting_date), "Client": selected_client, "Meeting": meeting_title, "Notes": ""}
                    df_meetings = pd.concat([df_meetings, pd.DataFrame([new_row])], ignore_index=True)
                    df_meetings.to_csv(MEETINGS_FILE, index=False)
                    push_to_github("data/meetings.csv", "Added new meeting")
                    st.success("Meeting saved successfully!")
                else:
                    st.error("Please enter a meeting title.")

        # Navigation for meetings
        client_meetings = df_meetings[df_meetings["Client"] == selected_client]
        if len(client_meetings) == 0:
            st.info("No meetings for this client yet.")
        else:
            st.subheader("Select a Meeting")
            meeting_options = client_meetings.apply(lambda row: f"{row['Date']} - {row['Meeting']}", axis=1).tolist()
            selected_meeting = st.selectbox("Meetings", meeting_options, key="meeting_select")

            meeting_index = meeting_options.index(selected_meeting)
            notes_key = f"notes_{meeting_index}"
            current_notes = client_meetings.iloc[meeting_index]["Notes"]

            # Notes editor
            st.subheader("Meeting Notes")
            updated_notes = st.text_area("Notes", value=current_notes, height=300, key=notes_key)

            col_save, col_delete = st.columns([1, 1])
            with col_save:
                if st.button("Save Notes", key="save_notes"):
                    df_meetings.at[client_meetings.index[meeting_index], "Notes"] = updated_notes
                    df_meetings.to_csv(MEETINGS_FILE, index=False)
                    push_to_github("data/meetings.csv", "Updated meeting notes")
                    st.success("Notes saved successfully!")
            with col_delete:
                if st.button("Delete Meeting", key="delete_meeting"):
                    df_meetings = df_meetings.drop(index=client_meetings.index[meeting_index])
                    df_meetings.to_csv(MEETINGS_FILE, index=False)
                    push_to_github("data/meetings.csv", "Deleted meeting")
                    st.success("Meeting deleted successfully!")

        # Add To-Do Item (with priority slider)
        st.subheader("Add To-Do Item")
        client_categories = df_categories[df_categories["Client"] == selected_client]["Category"].tolist()
        col_cat, col_task, col_notes, col_priority, col_btn = st.columns([1.5, 2, 3, 1, 1])
        with col_cat:
            todo_category = st.selectbox("Category", client_categories if client_categories else ["No categories"], key="todo_category_meeting")
        with col_task:
            todo_task = st.text_input("Task", key="todo_task_meeting")
        with col_notes:
            todo_notes = st.text_area("Notes", key="todo_notes_meeting", height=100)
        with col_priority:
            priority = st.slider("Priority", 1, 5, 3, key="todo_priority_meeting")
        with col_btn:
            if st.button("Add Task", key="add_task_meeting"):
                if todo_task.strip() and todo_category != "No categories":
                    df_todos.loc[len(df_todos)] = [selected_client, todo_category, todo_task, priority, str(datetime.today().date()), "", todo_notes]
                    df_todos.to_csv(TODOS_FILE, index=False)
                    push_to_github("data/todos.csv", "Added new task from meeting notes")
                    st.success("Task added successfully!")
                else:
                    st.error("Please enter a valid category and task.")








# -------------------------------------------------
# Placeholder Pages
# -------------------------------------------------
elif selected_page == "Reports":
    st.title("Reports")

    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    # File paths
    HOURS_FILE = os.path.join(DATA_DIR, "hours.csv")
    GOALS_FILE = os.path.join(DATA_DIR, "goals.csv")
    DAYS_OFF_FILE = os.path.join(DATA_DIR, "days_off.csv")
    CLIENTS_FILE = os.path.join(DATA_DIR, "clients.csv")
    PERIOD_FILE = os.path.join(DATA_DIR, "period_settings.csv")

    # Load data
    hours_df = pd.read_csv(HOURS_FILE)
    goals_df = pd.read_csv(GOALS_FILE)
    days_off_df = pd.read_csv(DAYS_OFF_FILE)
    df_clients = pd.read_csv(CLIENTS_FILE)

    # ✅ Safe date conversion
    hours_df["Date"] = pd.to_datetime(hours_df["Date"], errors="coerce")
    days_off_df["Date"] = pd.to_datetime(days_off_df["Date"], errors="coerce")

    # Drop invalid dates
    hours_df = hours_df.dropna(subset=["Date"])
    days_off_df = days_off_df.dropna(subset=["Date"])

    now = datetime.today()
    today = now.date()

    # Load or Initialize Performance Period
    if not os.path.exists(PERIOD_FILE):
        default_start = date(now.year, 1, 1)
        default_end = date(now.year, 12, 31)
        pd.DataFrame({"StartDate": [str(default_start)], "EndDate": [str(default_end)]}).to_csv(PERIOD_FILE, index=False)

    period_settings = pd.read_csv(PERIOD_FILE)
    saved_start = pd.to_datetime(period_settings["StartDate"].iloc[0]).date()
    saved_end = pd.to_datetime(period_settings["EndDate"].iloc[0]).date()

    # Performance Period Selection
    st.markdown('<div class="form-box">', unsafe_allow_html=True)
    col_start, col_end, col_btn = st.columns([1, 1, 1])
    with col_start:
        period_start = st.date_input("Performance Period Start", saved_start)
    with col_end:
        period_end = st.date_input("Performance Period End", saved_end)
    with col_btn:
        if st.button("Update Performance Period", use_container_width=True):
            pd.DataFrame({"StartDate": [str(period_start)], "EndDate": [str(period_end)]}).to_csv(PERIOD_FILE, index=False)
            push_to_github("data/period_settings.csv", "Updated performance period")
            st.success("Performance period updated!")
    st.markdown('</div>', unsafe_allow_html=True)

    # BAN Calculations
    period_hours_df = hours_df[(hours_df["Date"].dt.date >= period_start) & (hours_df["Date"].dt.date <= period_end)]
    period_goals_df = goals_df.copy()
    period_hours_df["Month"] = period_hours_df["Date"].dt.strftime("%Y-%m")
    period_goals_df["Month"] = period_goals_df["Month"].apply(lambda m: f"{now.year}-{int(m):02d}")

    monthly_actual_period = period_hours_df.groupby("Month")["Hours"].sum().reset_index()
    monthly_actual_period.rename(columns={"Hours": "ActualHours"}, inplace=True)

    all_months_period = pd.DataFrame({"Month": sorted(set(period_hours_df["Month"]).union(set(period_goals_df["Month"])))})

    merged_period = (
        all_months_period
        .merge(period_goals_df, on="Month", how="left")
        .merge(monthly_actual_period, on="Month", how="left")
        .fillna(0)
    )

    total_goal_hours = merged_period["GoalHours"].sum()
    total_actual_hours = merged_period["ActualHours"].sum()
    remaining_hours_period = max(total_goal_hours - total_actual_hours, 0)

    remaining_days_period = pd.date_range(start=max(now, pd.to_datetime(period_start)), end=pd.to_datetime(period_end), freq="B")
    days_off_period = days_off_df[(days_off_df["Date"].dt.date >= period_start) & (days_off_df["Date"].dt.date <= period_end)]
    remaining_weekdays_period = len(remaining_days_period) - len(days_off_period)
    avg_hours_left_period = remaining_hours_period / remaining_weekdays_period if remaining_weekdays_period > 0 else 0
    todays_hours = hours_df.loc[hours_df["Date"].dt.date == today, "Hours"].sum()

    # Display BAN Metrics
    st.markdown('<div class="form-box">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1: st.metric("Avg Hours Left/Day", f"{avg_hours_left_period:.2f}")
    with col2: st.metric("Goal Hours", f"{total_goal_hours:.2f}")
    with col3: st.metric("Actual Hours", f"{total_actual_hours:.2f}")
    with col4: st.metric("Today's Hours", f"{todays_hours:.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Weekly Snapshot Chart
    st.markdown('<div class="form-box">', unsafe_allow_html=True)
    if "week_offset" not in st.session_state:
        st.session_state.week_offset = 0
    today_ts = pd.Timestamp.today()
    start_of_week = (today_ts + pd.Timedelta(weeks=st.session_state.week_offset)).normalize() - pd.Timedelta(days=today_ts.weekday())
    end_of_week = start_of_week + pd.Timedelta(days=6)
    week_label = f"{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d')}"
    st.subheader(f"Weekly Snapshot: Billed Hours by Client ({week_label})")
    nav_col1, nav_col2 = st.columns([1, 1])
    with nav_col1:
        if st.button("⬅ Previous Week"):
            st.session_state.week_offset -= 1
    with nav_col2:
        if st.button("Next Week ➡"):
            st.session_state.week_offset += 1

    weekly_data = hours_df[(hours_df["Date"] >= start_of_week) & (hours_df["Date"] <= end_of_week)]
    client_colors = {row["Client"]: row["Color"] for _, row in df_clients.iterrows()}

    weekdays = pd.date_range(start_of_week, end_of_week, freq="D")
    weekdays = [d for d in weekdays if d.weekday() < 5]

    fig_weekly = go.Figure()
    for client in weekly_data["Client"].unique():
        client_df = weekly_data[weekly_data["Client"] == client].groupby("Date")["Hours"].sum().reindex(weekdays, fill_value=0)
        fig_weekly.add_trace(go.Scatter(
            x=[d.strftime("%a") for d in weekdays], y=client_df.values,
            mode="lines+markers", name=client,
            line=dict(color=client_colors.get(client, "#FFFFFF"), width=4),
            marker=dict(size=10),
            hovertemplate="Client: " + client + "<br>Day: %{x}<br>Hours: %{y}<extra></extra>"
        ))

    fig_weekly.update_layout(
        plot_bgcolor="#0f0f23",
        paper_bgcolor="#0f0f23",
        font=dict(color="#FFFFFF", size=14),
        xaxis=dict(title="Day of Week", color="#FFFFFF", tickfont=dict(color="#FFFFFF"), showgrid=True, gridcolor="#FFFFFF"),
        yaxis=dict(title="Hours", color="#FFFFFF", tickfont=dict(color="#FFFFFF"), showgrid=True, gridcolor="#FFFFFF"),
        legend=dict(font=dict(color="#FFFFFF", size=18, family="Arial Bold"), orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        margin=dict(l=40, r=40, t=40, b=80)
    )
    st.plotly_chart(fig_weekly, use_container_width=True)

    # Date Range Filter for Bottom Charts
    st.markdown('<div class="form-box">', unsafe_allow_html=True)
    st.subheader("Filter for Monthly & Client Charts")
    col_start, col_end = st.columns([1, 1])
    with col_start:
        chart_start = st.date_input("Chart Start Date", date(now.year, max(now.month - 4, 1), 1))
    with col_end:
        chart_end = st.date_input("Chart End Date", date(now.year, now.month, calendar.monthrange(now.year, now.month)[1]))

    filtered_hours = hours_df[(hours_df["Date"] >= pd.to_datetime(chart_start)) & (hours_df["Date"] <= pd.to_datetime(chart_end))]
    filtered_merged = merged_period[
        (pd.to_datetime(merged_period["Month"] + "-01") >= pd.to_datetime(chart_start)) &
        (pd.to_datetime(merged_period["Month"] + "-01") <= pd.to_datetime(chart_end))
    ]
    filtered_merged["MonthDate"] = pd.to_datetime(filtered_merged["Month"] + "-01")
    filtered_merged = filtered_merged.sort_values("MonthDate")
    filtered_merged["MonthLabel"] = filtered_merged["MonthDate"].dt.strftime("%b %Y")

    # Monthly & Pie Charts
    col1, col2 = st.columns([2, 1])
    chart_bg = "#0f0f23"
    text_color = "#FFFFFF"
    with col1:
        st.subheader("Monthly Actual vs Planned Hours")
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=filtered_merged["MonthLabel"], y=filtered_merged["GoalHours"],
            mode="lines+markers", name="Planned Hours",
            line=dict(color="#ff0000", width=3), marker=dict(color="#ff0000", size=8)
        ))
        fig_line.add_trace(go.Scatter(
            x=filtered_merged["MonthLabel"], y=filtered_merged["ActualHours"],
            mode="lines+markers", name="Actual Hours",
            line=dict(color="#00ff2f", width=3), marker=dict(color="#00ff2f", size=8)
        ))
        fig_line.update_layout(
            showlegend=False,
            plot_bgcolor=chart_bg,
            paper_bgcolor=chart_bg,
            font=dict(color=text_color, size=14),
            xaxis=dict(type="category", title="Month", color=text_color, tickfont=dict(color=text_color), showgrid=True, gridcolor=text_color),
            yaxis=dict(color=text_color, tickfont=dict(color=text_color), showgrid=True, gridcolor=text_color),
            autosize=True,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_line, use_container_width=True)
    with col2:
        st.subheader("Hours by Client")
        if len(filtered_hours) > 0:
            pie_fig = px.pie(filtered_hours, names="Client", values="Hours", color="Client", color_discrete_map=client_colors)
            pie_fig.update_layout(
                showlegend=True,
                plot_bgcolor=chart_bg,
                paper_bgcolor=chart_bg,
                font=dict(color=text_color, size=14),
                legend=dict(font=dict(color=text_color, size=16), orientation="v", x=1.05, y=0.5, bgcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(pie_fig, use_container_width=True)
        else:
            st.info("No hours logged in this range.")
    st.markdown('</div>', unsafe_allow_html=True)




















elif selected_page == "Data Entry":
    st.title("History")

    # Load data
    df_hours = pd.read_csv(HOURS_FILE)
    df_todos = pd.read_csv(TODOS_FILE)

    # Convert date columns for compatibility
    df_hours["Date"] = pd.to_datetime(df_hours["Date"], errors="coerce")
    df_todos["DateCreated"] = pd.to_datetime(df_todos["DateCreated"], errors="coerce")
    df_todos["DateCompleted"] = pd.to_datetime(df_todos["DateCompleted"], errors="coerce")

    #--------------------------
    # Enter data
    #--------------------------
    st.subheader("Add Client Category")

    col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 3])
    with col1:
        client = st.selectbox("Client", df_clients["Client"].tolist(), key="log_client")
    with col2:
        category = st.text_input("Category", key="todo_task")
    with col5:
        if st.button("Save Hours", key="save_hours"):
            new_row = {"Client": str(client), "Category": category, "Hours": hours, "Description": description}
            df_categories = pd.concat([df_categories, pd.DataFrame([new_row])], ignore_index=True)
            df_hours.to_csv(CATEGORIES_FILE, index=False)
            push_to_github("data/hours.csv", "Updated hours log")
            st.success("Hours logged successfully!")

    # -------------------------
    # Client Filter
    # -------------------------
    st.markdown('\n', unsafe_allow_html=True)
    st.subheader("Filter by Client")
    all_clients = sorted(set(df_hours["Client"].dropna().tolist() + df_todos["Client"].dropna().tolist()))
    selected_clients = st.multiselect("Select Clients", all_clients, default=all_clients)
    st.markdown('\n', unsafe_allow_html=True)

    # Apply client filter
    filtered_hours = df_hours[df_hours["Client"].isin(selected_clients)] if len(selected_clients) > 0 else df_hours
    filtered_todos = df_todos[df_todos["Client"].isin(selected_clients)] if len(selected_clients) > 0 else df_todos

    # -------------------------
    # Search Filter
    # -------------------------
    st.markdown('\n', unsafe_allow_html=True)
    search_query = st.text_input("Search (applies to both tables):").strip().lower()

    if search_query:
        # Filter hours table
        filtered_hours = filtered_hours[
            filtered_hours.apply(lambda row: row.astype(str).str.lower().str.contains(search_query).any(), axis=1)
        ]
        # Filter todos table
        filtered_todos = filtered_todos[
            filtered_todos.apply(lambda row: row.astype(str).str.lower().str.contains(search_query).any(), axis=1)
        ]

    # -------------------------
    # Editable Hours + To-Do History
    # -------------------------
    st.markdown('\n', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    # Editable Hours History
    with col1:
        st.subheader("Logged Hours History")
        if len(filtered_hours) == 0:
            st.info("No hours logged for selected client(s) or search term.")
        else:
            sort_hours_by = st.selectbox("Sort Hours By", ["Date (Newest)", "Date (Oldest)", "Hours (High to Low)", "Hours (Low to High)"])
            if sort_hours_by == "Date (Newest)":
                filtered_hours = filtered_hours.sort_values(by="Date", ascending=False)
            elif sort_hours_by == "Date (Oldest)":
                filtered_hours = filtered_hours.sort_values(by="Date", ascending=True)
            elif sort_hours_by == "Hours (High to Low)":
                filtered_hours = filtered_hours.sort_values(by="Hours", ascending=False)
            elif sort_hours_by == "Hours (Low to High)":
                filtered_hours = filtered_hours.sort_values(by="Hours", ascending=True)

            edited_hours = st.data_editor(
                filtered_hours[["Date", "Client", "Hours", "Description"]].reset_index(drop=True),
                num_rows="dynamic", width="stretch", hide_index=True
            )

            if st.button("Save Hours Changes"):
                cleaned_hours = edited_hours.dropna(how="all")
                cleaned_hours = cleaned_hours[(cleaned_hours != "").any(axis=1)]
                cleaned_hours.to_csv(HOURS_FILE, index=False)
                push_to_github("data/hours.csv", "Updated hours history (removed empty rows)")
                st.success("Hours history updated! Empty rows deleted.")

    # Editable To-Do History
    with col2:
        st.subheader("To-Do History")
        if len(filtered_todos) == 0:
            st.info("No tasks recorded for selected client(s) or search term.")
        else:
            sort_todos_by = st.selectbox("Sort To-Dos By", ["Priority (High to Low)", "Priority (Low to High)", "Date Created (Newest)", "Date Created (Oldest)"])
            if sort_todos_by == "Priority (High to Low)":
                filtered_todos = filtered_todos.sort_values(by="Priority", ascending=False)
            elif sort_todos_by == "Priority (Low to High)":
                filtered_todos = filtered_todos.sort_values(by="Priority", ascending=True)
            elif sort_todos_by == "Date Created (Newest)":
                filtered_todos = filtered_todos.sort_values(by="DateCreated", ascending=False)
            elif sort_todos_by == "Date Created (Oldest)":
                filtered_todos = filtered_todos.sort_values(by="DateCreated", ascending=True)

            edited_todos = st.data_editor(
                filtered_todos[["Client", "Category", "Task", "Priority", "DateCreated", "DateCompleted", "Notes"]].reset_index(drop=True),
                num_rows="dynamic", width="stretch", hide_index=True
            )

            if st.button("Save To-Do Changes"):
                cleaned_todos = edited_todos.dropna(how="all")
                cleaned_todos = cleaned_todos[(cleaned_todos != "").any(axis=1)]
                cleaned_todos.to_csv(TODOS_FILE, index=False)
                push_to_github("data/todos.csv", "Updated To-Do history (removed empty rows)")
                st.success("To-Do history updated! Empty rows deleted.")





    

elif selected_page == "Archive":
    st.title("Archive Clients")

    # Load active data
    df_clients = pd.read_csv(CLIENTS_FILE)
    df_categories = pd.read_csv(CATEGORIES_FILE)
    df_todos = pd.read_csv(TODOS_FILE)
    df_hours = pd.read_csv(HOURS_FILE)

    # Archive file paths
    ARCHIVE_CLIENTS = os.path.join(DATA_DIR, "archive_clients.csv")
    ARCHIVE_CATEGORIES = os.path.join(DATA_DIR, "archive_categories.csv")
    ARCHIVE_TODOS = os.path.join(DATA_DIR, "archive_todos.csv")
    ARCHIVE_HOURS = os.path.join(DATA_DIR, "archive_hours.csv")

    # Ensure archive files exist
    archive_files = [
        (ARCHIVE_CLIENTS, ["Client", "Color"]),
        (ARCHIVE_CATEGORIES, ["Client", "Category"]),
        (ARCHIVE_TODOS, ["Client", "Category", "Task", "Priority", "DateCreated", "DateCompleted"]),
        (ARCHIVE_HOURS, ["Date", "Client", "Hours", "Description"])
    ]
    for file, cols in archive_files:
        if not os.path.exists(file):
            pd.DataFrame(columns=cols).to_csv(file, index=False)

    # Load archive data
    df_archive_clients = pd.read_csv(ARCHIVE_CLIENTS)
    df_archive_categories = pd.read_csv(ARCHIVE_CATEGORIES)
    df_archive_todos = pd.read_csv(ARCHIVE_TODOS)
    df_archive_hours = pd.read_csv(ARCHIVE_HOURS)

    # -------------------------------
    # Archive Client Action
    # -------------------------------
    st.markdown('<div class="form-box">', unsafe_allow_html=True)
    st.subheader("Archive a Client")
    if len(df_clients) == 0:
        st.warning("No clients available to archive.")
    else:
        selected_client = st.selectbox("Select Client to Archive", df_clients["Client"].tolist(), key="archive_client")
        if st.button("Archive Client"):
            # Move data to archive
            df_archive_clients = pd.concat([df_archive_clients, df_clients[df_clients["Client"] == selected_client]], ignore_index=True)
            df_archive_categories = pd.concat([df_archive_categories, df_categories[df_categories["Client"] == selected_client]], ignore_index=True)
            df_archive_todos = pd.concat([df_archive_todos, df_todos[df_todos["Client"] == selected_client]], ignore_index=True)
            df_archive_hours = pd.concat([df_archive_hours, df_hours[df_hours["Client"] == selected_client]], ignore_index=True)

            # Remove from active files
            df_clients = df_clients[df_clients["Client"] != selected_client]
            df_categories = df_categories[df_categories["Client"] != selected_client]
            df_todos = df_todos[df_todos["Client"] != selected_client]
            df_hours = df_hours[df_hours["Client"] != selected_client]

            # Save all files
            df_clients.to_csv(CLIENTS_FILE, index=False)
            df_categories.to_csv(CATEGORIES_FILE, index=False)
            df_todos.to_csv(TODOS_FILE, index=False)
            df_hours.to_csv(HOURS_FILE, index=False)
            df_archive_clients.to_csv(ARCHIVE_CLIENTS, index=False)
            df_archive_categories.to_csv(ARCHIVE_CATEGORIES, index=False)
            df_archive_todos.to_csv(ARCHIVE_TODOS, index=False)
            df_archive_hours.to_csv(ARCHIVE_HOURS, index=False)

            # Push to GitHub
            push_to_github("data/clients.csv", "Archived client")
            push_to_github("data/categories.csv", "Archived client categories")
            push_to_github("data/todos.csv", "Archived client todos")
            push_to_github("data/hours.csv", "Archived client hours")
            push_to_github("data/archive_clients.csv", "Updated archive clients")
            push_to_github("data/archive_categories.csv", "Updated archive categories")
            push_to_github("data/archive_todos.csv", "Updated archive todos")
            push_to_github("data/archive_hours.csv", "Updated archive hours")

            st.success(f"Client '{selected_client}' archived successfully!")
    st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------
    # Undo Archive Client Action
    # -------------------------------
    st.markdown('<div class="form-box">', unsafe_allow_html=True)
    st.subheader("Undo Archive")
    if len(df_archive_clients) == 0:
        st.warning("No archived clients available.")
    else:
        undo_client = st.selectbox("Select Archived Client to Restore", df_archive_clients["Client"].tolist(), key="undo_client")
        if st.button("Restore Client"):
            # Move data back to active
            df_clients = pd.concat([df_clients, df_archive_clients[df_archive_clients["Client"] == undo_client]], ignore_index=True)
            df_categories = pd.concat([df_categories, df_archive_categories[df_archive_categories["Client"] == undo_client]], ignore_index=True)
            df_todos = pd.concat([df_todos, df_archive_todos[df_archive_todos["Client"] == undo_client]], ignore_index=True)
            df_hours = pd.concat([df_hours, df_archive_hours[df_archive_hours["Client"] == undo_client]], ignore_index=True)

            # Remove from archive files
            df_archive_clients = df_archive_clients[df_archive_clients["Client"] != undo_client]
            df_archive_categories = df_archive_categories[df_archive_categories["Client"] != undo_client]
            df_archive_todos = df_archive_todos[df_archive_todos["Client"] != undo_client]
            df_archive_hours = df_archive_hours[df_archive_hours["Client"] != undo_client]

            # Save all files
            df_clients.to_csv(CLIENTS_FILE, index=False)
            df_categories.to_csv(CATEGORIES_FILE, index=False)
            df_todos.to_csv(TODOS_FILE, index=False)
            df_hours.to_csv(HOURS_FILE, index=False)
            df_archive_clients.to_csv(ARCHIVE_CLIENTS, index=False)
            df_archive_categories.to_csv(ARCHIVE_CATEGORIES, index=False)
            df_archive_todos.to_csv(ARCHIVE_TODOS, index=False)
            df_archive_hours.to_csv(ARCHIVE_HOURS, index=False)

            # Push to GitHub
            push_to_github("data/clients.csv", "Restored client")
            push_to_github("data/categories.csv", "Restored client categories")
            push_to_github("data/todos.csv", "Restored client todos")
            push_to_github("data/hours.csv", "Restored client hours")
            push_to_github("data/archive_clients.csv", "Updated archive clients after restore")
            push_to_github("data/archive_categories.csv", "Updated archive categories after restore")
            push_to_github("data/archive_todos.csv", "Updated archive todos after restore")
            push_to_github("data/archive_hours.csv", "Updated archive hours after restore")

            st.success(f"Client '{undo_client}' restored successfully!")
    st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------
    # Edit Client Colors
    # -------------------------------
    st.markdown('<div class="form-box">', unsafe_allow_html=True)
    st.subheader("Edit Client Colors")
    if len(df_clients) > 0:
        for i, row in df_clients.iterrows():
            col1, col2 = st.columns([2, 1])
            with col1:
                st.text(row["Client"])
            with col2:
                new_color = st.color_picker("", row["Color"], key=f"color_{i}")
                df_clients.at[i, "Color"] = new_color
        if st.button("Save Color Changes"):
            df_clients.to_csv(CLIENTS_FILE, index=False)
            st.success("Client colors updated!")
    st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------
    # Show Archive History Tables
    # -------------------------------
    st.markdown('<div class="form-box">', unsafe_allow_html=True)
    st.subheader("Archive History")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Archived Hours")
        st.dataframe(df_archive_hours.sort_values(by="Date", ascending=False).reset_index(drop=True), width="stretch", hide_index=True)
    with col2:
        st.markdown("### Archived To-Dos")
        st.dataframe(df_archive_todos.sort_values(by="DateCreated", ascending=False)[
            ["Client", "Category", "Task", "Priority", "DateCreated", "DateCompleted"]
        ].reset_index(drop=True), width="stretch", hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)































































































