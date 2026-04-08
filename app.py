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
DAYS_OFF_FILE = os.path.join(DATA_DIR, "days_off.csv")
UNENTERED_HOURS_FILE = os.path.join(DATA_DIR, "unentered_hours.csv")
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
PERIOD_FILE = os.path.join(DATA_DIR, "period_settings.csv")
os.makedirs(DATA_DIR, exist_ok=True)
st.set_page_config(layout="wide")

# -------------------------------------------------
# GitHub Functions
# -------------------------------------------------
def fetch_from_github(file_path: str):
    """
    Fetch file content from the public GitHub repo and save loly.
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
        # File not yet in repo; create loly and push later if desired
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
for file in ["data/clients.csv", "data/period_settings.csv","data/hours.csv", "data/goals.csv", "data/days_off.csv", "data/categories.csv", "data/todos.csv", "data/style.css"]:
    fetch_from_github(file)

st.markdown('<link rel="stylesheet" href="YOUR_GITHUB_RAW_CSS_URL">', unsafe_allow_html=True)
# Ensure files exist locally

# Sync public files from GitHub
for file in [
    "data/clients.csv",
    "data/hours.csv",
    "data/goals.csv",
    "data/categories.csv",
    "data/unentered_hours.csv",
    "data/todos.csv",
    "data/style.css",
    "data/period_settings.csv"
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
    ("data/days_off.csv", ["Date"]),
    ("data/period_settings.csv", ["StartDate", "EndDate", "HoursGoal"]),
    ("data/unentered_hours.csv", ["Date", "Client", "Hours", "Description"]),
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
pages = ["Home", "Reports", "Data Entry", "Archive"]
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

    # normalize headers + values
    df_clients.columns = df_clients.columns.str.strip()
    df_clients["Client"] = df_clients["Client"].str.strip()
    df_clients["Color"] = df_clients["Color"].str.strip()
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
                new_row = {
                    "Date": str(date_val),
                    "Client": client,
                    "Hours": hours,
                    "Description": description
                }
            
                # Load unentered hours
                if os.path.exists(UNENTERED_HOURS_FILE):
                    unentered_df = pd.read_csv(UNENTERED_HOURS_FILE)
                else:
                    unentered_df = pd.DataFrame(
                        columns=["Date", "Client", "Hours", "Description"]
                    )
            
                unentered_df = pd.concat(
                    [unentered_df, pd.DataFrame([new_row])],
                    ignore_index=True
                )
            
                unentered_df.to_csv(UNENTERED_HOURS_FILE, index=False)
                push_to_github(
                    "data/unentered_hours.csv",
                    "Added new unentered hours"
                )
            
                st.success("Hours added to unentered backlog.")
            

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
    # Unentered Hours (Persistent Backlog)
    # -------------------------------
    st.subheader("Unentered Hours")
    
    # Ensure file exists
    if not os.path.exists(UNENTERED_HOURS_FILE):
        pd.DataFrame(columns=["Date", "Client", "Hours", "Description"]).to_csv(
            UNENTERED_HOURS_FILE, index=False
        )
    
    raw = pd.read_csv(UNENTERED_HOURS_FILE)
    
    # Ensure required columns exist (defensive)
    for col in ["Date", "Client", "Hours", "Description"]:
        if col not in raw.columns:
            raw[col] = "" if col != "Hours" else 0
    
    # Normalize types
    raw["Client"] = raw["Client"].astype(str).str.strip()
    raw["Description"] = raw["Description"].astype(str).fillna("").str.strip()
    raw["Hours"] = pd.to_numeric(raw["Hours"], errors="coerce").fillna(0)
    
    # Parse dates -> keep as date (not timestamp)
    raw["Date"] = pd.to_datetime(raw["Date"], errors="coerce").dt.date
    
    # IMPORTANT: Strip any previously-saved TOTAL rows (cleans “polluted” files)
    is_total = raw["Description"].str.upper().eq("TOTAL")
    stale_total_count = int(is_total.sum())
    raw = raw[~is_total].copy()
    
    if stale_total_count > 0:
        st.info(
            f"Found {stale_total_count} stale TOTAL row(s) in unentered_hours.csv. "
            "They will not be used and will be removed next time you save."
        )
    
    # Drop empty rows
    raw = raw.dropna(subset=["Date"])
    raw = raw[raw["Client"] != ""].copy()
    
    # Detail rows (for editing)
    detail = raw.copy()
    detail["Date"] = pd.to_datetime(detail["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    detail = detail.sort_values(by=["Client", "Date"]).reset_index(drop=True)
    
    # Computed totals (for display only)
    totals = (
        raw.groupby(["Client", "Date"], as_index=False)["Hours"]
        .sum()
        .sort_values(by=["Client", "Date"])
        .reset_index(drop=True)
    )
    totals["Description"] = "TOTAL"
    totals["Date"] = pd.to_datetime(totals["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    
    # Display = details first, totals at bottom
    unentered_display = pd.concat([detail, totals], ignore_index=True)
    
    edited_unentered = st.data_editor(
        unentered_display,
        num_rows="dynamic",
        hide_index=True,
        key="unentered_hours_editor"
    )
    
    col_save, col_mark = st.columns([1, 1])
    
    # -----------------
    # Save edits (ONLY real rows; totals are recomputed)
    # -----------------
    with col_save:
        if st.button("Save Unentered Changes"):
            cleaned = edited_unentered.dropna(how="all").copy()
    
            # Normalize again from edited grid
            for col in ["Date", "Client", "Hours", "Description"]:
                if col not in cleaned.columns:
                    cleaned[col] = "" if col != "Hours" else 0
    
            cleaned["Client"] = cleaned["Client"].astype(str).str.strip()
            cleaned["Description"] = cleaned["Description"].astype(str).fillna("").str.strip()
            cleaned["Hours"] = pd.to_numeric(cleaned["Hours"], errors="coerce").fillna(0)
            cleaned["Date"] = pd.to_datetime(cleaned["Date"], errors="coerce")
    
            # Keep ONLY detail rows (exclude totals robustly)
            cleaned = cleaned[~cleaned["Description"].str.upper().eq("TOTAL")].copy()
    
            # Drop junk rows
            cleaned = cleaned.dropna(subset=["Date"])
            cleaned = cleaned[cleaned["Client"] != ""].copy()
    
            # Store canonical date format
            cleaned["Date"] = cleaned["Date"].dt.strftime("%Y-%m-%d")
    
            # Save ONLY real rows
            cleaned[["Date", "Client", "Hours", "Description"]].to_csv(
                UNENTERED_HOURS_FILE, index=False
            )
            push_to_github("data/unentered_hours.csv", "Updated unentered hours backlog")
            st.success("Unentered hours saved (totals are computed, not stored).")
    
    # -----------------
    # Mark as entered (by client) — ONLY real rows
    # -----------------
    with col_mark:
        # Build client dropdown from detail rows only (exclude totals)
        detail_only = edited_unentered.copy()
        detail_only["Client"] = detail_only["Client"].astype(str).str.strip()
        detail_only["Description"] = detail_only["Description"].astype(str).fillna("").str.strip()
        detail_only = detail_only[~detail_only["Description"].str.upper().eq("TOTAL")].copy()
        detail_only = detail_only[detail_only["Client"] != ""].copy()
    
        clients_in_table = sorted(detail_only["Client"].dropna().unique().tolist())
    
        if clients_in_table:
            selected_client = st.selectbox("Mark entries as entered (by client)", clients_in_table)
    
            if st.button("Mark as Entered"):
                to_post = detail_only[detail_only["Client"] == selected_client].copy()
                remaining = detail_only[detail_only["Client"] != selected_client].copy()
    
                # Normalize posted rows
                to_post["Hours"] = pd.to_numeric(to_post["Hours"], errors="coerce").fillna(0)
                to_post["Date"] = pd.to_datetime(to_post["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    
                # Append to hours.csv
                hours_df = pd.read_csv(HOURS_FILE)
                for col in ["Date", "Client", "Hours", "Description"]:
                    if col not in hours_df.columns:
                        hours_df[col] = "" if col != "Hours" else 0
    
                combined = pd.concat(
                    [hours_df[["Date", "Client", "Hours", "Description"]],
                     to_post[["Date", "Client", "Hours", "Description"]]],
                    ignore_index=True
                )
    
                # Canonicalize dates in hours.csv too
                combined["Date"] = pd.to_datetime(combined["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
                combined["Hours"] = pd.to_numeric(combined["Hours"], errors="coerce").fillna(0)
    
                combined.to_csv(HOURS_FILE, index=False)
                push_to_github("data/hours.csv", f"Entered hours for {selected_client}")
    
                # Save remaining unentered (detail rows only)
                remaining["Date"] = pd.to_datetime(remaining["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
                remaining["Hours"] = pd.to_numeric(remaining["Hours"], errors="coerce").fillna(0)
    
                remaining[["Date", "Client", "Hours", "Description"]].to_csv(
                    UNENTERED_HOURS_FILE, index=False
                )
                push_to_github("data/unentered_hours.csv", f"Cleared unentered hours for {selected_client}")
    
                st.success(f"Hours for {selected_client} marked as entered.")
        else:
            st.info("No unentered hours.")

    
elif selected_page == "Reports":
    st.title("Reports")

    # ----------------------------
    # Helpers (local to Reports)
    # ----------------------------
    from datetime import timedelta

    def _safe_read_csv(path, cols=None):
        """Read CSV if it exists; otherwise return empty DF with optional cols."""
        if os.path.exists(path):
            try:
                return pd.read_csv(path)
            except Exception:
                return pd.DataFrame(columns=cols or [])
        return pd.DataFrame(columns=cols or [])

    def _to_date_series(s):
        """Convert a pandas Series to python date objects; invalid -> NaT dropped."""
        if s is None or len(s) == 0:
            return pd.Series([], dtype="object")
        return pd.to_datetime(s, errors="coerce").dt.date.dropna()

    def _is_workday(d: date) -> bool:
        # Mon=0 ... Sun=6
        return d.weekday() < 5

    def _count_remaining_workdays_from_tomorrow(end_d: date, days_off: set[date]) -> int:
        """Count workdays from tomorrow through end_d, excluding weekends and days_off."""
        start = date.today() + timedelta(days=1)
        if end_d is None or start > end_d:
            return 0

        n = 0
        cur = start
        while cur <= end_d:
            if _is_workday(cur) and cur not in days_off:
                n += 1
            cur += timedelta(days=1)
        return n

    def _avg_required(goal_hours: float, actual_hours: float, end_d: date, days_off: set[date]) -> float:
        """Avg hours/day required from tomorrow to end_d."""
        remaining = max(float(goal_hours) - float(actual_hours), 0.0)
        remaining_days = _count_remaining_workdays_from_tomorrow(end_d, days_off)
        return (remaining / remaining_days) if remaining_days > 0 else 0.0

    def _sum_hours_between(df_hours, start_d: date, end_d: date) -> float:
        if df_hours.empty:
            return 0.0
        dts = pd.to_datetime(df_hours.get("Date", pd.Series([])), errors="coerce").dt.date
        hrs = pd.to_numeric(df_hours.get("Hours", pd.Series([])), errors="coerce").fillna(0.0)
        mask = (dts >= start_d) & (dts <= end_d)
        return float(hrs[mask].sum()) if mask.any() else 0.0

    # ----------------------------
    # Load data
    # ----------------------------
    df_hours = _safe_read_csv(HOURS_FILE, cols=["Date", "Client", "Hours", "Description"])
    df_goals = _safe_read_csv(GOALS_FILE, cols=["Month", "GoalHours"])
    df_period = _safe_read_csv(PERIOD_FILE, cols=["StartDate", "EndDate", "HoursGoal"])
    df_days_off = _safe_read_csv(DAYS_OFF_FILE, cols=["Date"])

    # Normalize dates
    days_off = set(_to_date_series(df_days_off.get("Date", pd.Series([]))).tolist())

    today = date.today()

    # ----------------------------
    # Define report windows
    # ----------------------------
    # Week window: Monday -> Sunday
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    # Month window: 1st -> last day
    month_start = date(today.year, today.month, 1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    month_end = date(today.year, today.month, last_day)

    # Period window: from period_settings.csv if present, else default to current month
    period_start = month_start
    period_end = month_end
    period_goal = 0.0

    if not df_period.empty:
        try:
            ps = df_period.iloc[-1]  # last row wins
            period_start = pd.to_datetime(ps.get("StartDate"), errors="coerce").date()
            period_end = pd.to_datetime(ps.get("EndDate"), errors="coerce").date()
            period_goal = float(ps.get("HoursGoal", 0.0) or 0.0)
        except Exception:
            period_start, period_end, period_goal = month_start, month_end, 0.0

    # Month goal from goals.csv (matches "Month" as YYYY-MM or similar). If missing, 0.
    month_goal = 0.0
    if not df_goals.empty:
        # Try common formats: "YYYY-MM", "YYYY-MM-01", or month name.
        m = str(today.strftime("%Y-%m"))
        try:
            df_goals["Month_str"] = df_goals["Month"].astype(str)
            hit = df_goals[df_goals["Month_str"].str.contains(m, na=False)]
            if not hit.empty:
                month_goal = float(pd.to_numeric(hit.iloc[-1].get("GoalHours", 0), errors="coerce") or 0.0)
        except Exception:
            month_goal = 0.0

    # Week goal: pro-rate month goal by workdays in week vs workdays in month (fallback to 0)
    def _workdays_in_range(start_d: date, end_d: date, days_off: set[date]) -> int:
        if start_d > end_d:
            return 0
        n = 0
        cur = start_d
        while cur <= end_d:
            if _is_workday(cur) and cur not in days_off:
                n += 1
            cur += timedelta(days=1)
        return n

    month_workdays = _workdays_in_range(month_start, month_end, days_off)
    week_workdays = _workdays_in_range(week_start, week_end, days_off)
    week_goal = (month_goal * (week_workdays / month_workdays)) if (month_goal and month_workdays) else 0.0

    # ----------------------------
    # Actual hours in each window
    # ----------------------------
    week_actual = _sum_hours_between(df_hours, week_start, week_end)
    month_actual = _sum_hours_between(df_hours, month_start, month_end)
    period_actual = _sum_hours_between(df_hours, period_start, period_end)

    # ----------------------------
    # Required average (FROM TOMORROW!)
    # ----------------------------
    week_avg_req = _avg_required(week_goal, week_actual, week_end, days_off)
    month_avg_req = _avg_required(month_goal, month_actual, month_end, days_off)
    period_avg_req = _avg_required(period_goal, period_actual, period_end, days_off)

    # ----------------------------
    # Render UI
    # ----------------------------
    st.subheader("WEEK")
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Hours / Day (Required)", f"{week_avg_req:.2f}")
    c2.metric("Goal Hours", f"{week_goal:.2f}")
    c3.metric("Actual Hours", f"{week_actual:.2f}")

    st.divider()

    st.subheader("MONTH")
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Hours / Day (Required)", f"{month_avg_req:.2f}")
    c2.metric("Goal Hours", f"{month_goal:.2f}")
    c3.metric("Actual Hours", f"{month_actual:.2f}")

    st.divider()

    st.subheader("PERIOD")
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Hours / Day (Required)", f"{period_avg_req:.2f}")
    c2.metric("Goal Hours", f"{period_goal:.2f}")
    c3.metric("Actual Hours", f"{period_actual:.2f}")

    # Small debug expander (optional but helpful)
    with st.expander("Debug: calculation inputs", expanded=False):
        st.write({
            "today": str(today),
            "week_start": str(week_start), "week_end": str(week_end),
            "month_start": str(month_start), "month_end": str(month_end),
            "period_start": str(period_start), "period_end": str(period_end),
            "week_goal": week_goal, "week_actual": week_actual, "week_avg_req": week_avg_req,
            "month_goal": month_goal, "month_actual": month_actual, "month_avg_req": month_avg_req,
            "period_goal": period_goal, "period_actual": period_actual, "period_avg_req": period_avg_req,
            "days_off_count": len(days_off),
        })




elif selected_page == "Data Entry":
    st.title("History")

    # Load data
    df_hours = pd.read_csv(HOURS_FILE)
    df_todos = pd.read_csv(TODOS_FILE)
    df_clients = pd.read_csv(CLIENTS_FILE)
    df_categories = pd.read_csv(CATEGORIES_FILE)

    # Convert date columns for compatibility
    df_hours["Date"] = pd.to_datetime(df_hours["Date"], errors="coerce")
    df_todos["DateCreated"] = pd.to_datetime(df_todos["DateCreated"], errors="coerce")
    df_todos["DateCompleted"] = pd.to_datetime(df_todos["DateCompleted"], errors="coerce")

    df_hours = df_hours.sort_values(by = ['Date','Client'])

    #--------------------------
    # Enter data
    #--------------------------
    #--------------------------
    # Enter data
    #--------------------------
    st.subheader("Add Client")
    # --- Load clients ---
    df_clients = pd.read_csv(CLIENTS_FILE)
    
    if "Color" not in df_clients.columns:
        df_clients["Color"] = "#1f77b4"
    
    # --- Inputs ---
    new_client = st.text_input("Client name", key="new_client_name")
    new_color = st.color_picker("Client color", "#1f77b4", key="new_client_color")
    
    # --- Save button (same pattern as Time Off / Category) ---
    if st.button("Add Client"):
        if new_client.strip() == "":
            st.warning("Client name is required.")
        elif new_client.strip() in df_clients["Client"].values:
            st.warning("Client already exists.")
        else:
            df_clients = pd.concat(
                [
                    df_clients,
                    pd.DataFrame([{
                        "Client": new_client.strip(),
                        "Color": new_color
                    }])
                ],
                ignore_index=True
            )
    
            df_clients.to_csv(CLIENTS_FILE, index=False)
            st.write("TOKEN present:", bool(GITHUB_TOKEN))
            st.write("CLIENTS_FILE:", CLIENTS_FILE)
            st.write("Local clients.csv exists:", os.path.exists(CLIENTS_FILE))
            st.write("Local clients.csv size:", os.path.getsize(CLIENTS_FILE) if os.path.exists(CLIENTS_FILE) else None)
            
            # After you write df to csv:
            st.write("Last 5 rows after add:")
            st.dataframe(pd.read_csv(CLIENTS_FILE).tail())
            push_to_github("data/clients.csv", "Updated upcoming time off (editable table)")

    
            st.success(f"Client '{new_client}' added")
            

    st.subheader("Add Client Category")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        category_client = st.selectbox(
            "Client",
            df_clients["Client"].tolist(),
            key="de_category_client"   # unique key (avoid collisions with other pages)
        )
    
    with col2:
        category_name = st.text_input(
            "Category",
            key="de_category_name"
        )
    
    with col3:
        if st.button("Save Category", key="de_save_category"):
            if str(category_name).strip() == "":
                st.error("Category cannot be blank.")
            else:
                # Only store what categories.csv actually needs: Client + Category
                new_row = {"Client": str(category_client), "Category": str(category_name).strip()}
                df_categories = pd.concat([df_categories, pd.DataFrame([new_row])], ignore_index=True)
    
                # Optional: prevent duplicates (same client/category)
                df_categories = df_categories.drop_duplicates(subset=["Client", "Category"]).reset_index(drop=True)
    
                # Save correct dataframe -> correct file
                df_categories.to_csv(CATEGORIES_FILE, index=False)
    
                # Push correct file
                push_to_github("data/categories.csv", "Added/updated category")
    
                st.success("Hours logged successfully!")

    # -------------------------
    # Client Filter
    # -------------------------
    st.markdown('\n', unsafe_allow_html=True)
    # -------------------------
    # Time Off (PTO) Section
    # -------------------------
    st.markdown("\n", unsafe_allow_html=True)
    st.subheader("Time Off")
    
    # Load or initialize days_off.csv (keeps schema: Date only)
    if not os.path.exists(DAYS_OFF_FILE):
        pd.DataFrame(columns=["Date"]).to_csv(DAYS_OFF_FILE, index=False)
    
    days_off_df = pd.read_csv(DAYS_OFF_FILE)
    if "Date" not in days_off_df.columns:
        # Safety: keep structure minimal + compatible with Reports
        days_off_df = pd.DataFrame(columns=["Date"])
    
    # Parse existing dates safely
    days_off_df["Date"] = pd.to_datetime(days_off_df["Date"], errors="coerce")
    days_off_df = days_off_df.dropna(subset=["Date"]).copy()
    
    left_col, right_col = st.columns(2)
    
    with left_col:
        st.markdown("### Add Time Off")
    
        start_date = st.date_input("Start Date", value=date.today(), key="pto_start_date")
        end_date = st.date_input("End Date", value=date.today(), key="pto_end_date")
        weekdays_only = st.checkbox("Weekdays only (Mon–Fri)", value=True, key="pto_weekdays_only")
    
        if start_date > end_date:
            st.error("Start Date must be on or before End Date.")
        else:
            if st.button("Save Time Off", key="save_time_off"):
                # Expand range into individual dates (stored as one row per date)
                rng = pd.date_range(start=start_date, end=end_date, freq="D")
                if weekdays_only:
                    rng = [d for d in rng if d.weekday() < 5]  # Mon-Fri only
    
                new_dates = pd.DataFrame({"Date": [d.strftime("%Y-%m-%d") for d in rng]})
    
                # Combine + de-duplicate
                combined = pd.concat(
                    [days_off_df.assign(Date=days_off_df["Date"].dt.strftime("%Y-%m-%d")), new_dates],
                    ignore_index=True
                ).drop_duplicates(subset=["Date"])
    
                # Save back (keep schema: Date)
                combined = combined.sort_values("Date").reset_index(drop=True)
                combined.to_csv(DAYS_OFF_FILE, index=False)
    
                # Push to GitHub (optional; uses your existing helper)
                push_to_github("data/days_off.csv", "Updated days off / time off")
    
                st.success("Time off saved!")
    
    with right_col:
        st.markdown("### Upcoming Time Off (Editable)")
    
        # Build an editable view of upcoming time off dates
        today_dt = pd.to_datetime(date.today())
        upcoming_df = days_off_df[days_off_df["Date"] >= today_dt].copy()
        upcoming_df = upcoming_df.sort_values("Date").reset_index(drop=True)
    
        # Display as strings for editing consistency
        upcoming_display = upcoming_df.copy()
        upcoming_display["Date"] = upcoming_display["Date"].dt.strftime("%Y-%m-%d")
    
        edited_upcoming = st.data_editor(
            upcoming_display[["Date"]],
            num_rows="dynamic",        # allows delete rows + add rows
            hide_index=True,
            key="pto_upcoming_editor"
        )
    
        col_save, col_delete = st.columns([1, 1])
    
        with col_save:
            if st.button("Save Upcoming Changes", key="pto_save_upcoming"):
                # Clean + validate
                cleaned = edited_upcoming.dropna(how="all").copy()
                cleaned["Date"] = cleaned["Date"].astype(str).str.strip()
                cleaned["Date"] = pd.to_datetime(cleaned["Date"], errors="coerce")
                cleaned = cleaned.dropna(subset=["Date"]).copy()
    
                # Enforce weekdays only
                cleaned = cleaned[cleaned["Date"].dt.weekday < 5].copy()
    
                # Merge back with past time-off dates (so editing upcoming doesn't wipe history)
                past_df = days_off_df[days_off_df["Date"] < today_dt].copy()
                combined = pd.concat([past_df, cleaned], ignore_index=True)
    
                # De-dupe + sort
                combined["Date"] = combined["Date"].dt.strftime("%Y-%m-%d")
                combined = combined.drop_duplicates(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    
                combined.to_csv(DAYS_OFF_FILE, index=False)
                push_to_github("data/days_off.csv", "Updated upcoming time off (editable table)")
                st.success("Upcoming time off updated!")
    
        with col_delete:
            # Optional: quick multi-delete without editing rows
            if len(upcoming_display) > 0:
                to_delete = st.multiselect(
                    "Delete selected dates",
                    upcoming_display["Date"].tolist(),
                    key="pto_delete_dates"
                )
                if st.button("Delete Selected", key="pto_delete_selected"):
                    if to_delete:
                        remaining = days_off_df.copy()
                        remaining["DateStr"] = remaining["Date"].dt.strftime("%Y-%m-%d")
                        remaining = remaining[~remaining["DateStr"].isin(to_delete)].copy()
                        remaining = remaining.drop(columns=["DateStr"])
                        remaining["Date"] = remaining["Date"].dt.strftime("%Y-%m-%d")
                        remaining = remaining.drop_duplicates(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    
                        remaining.to_csv(DAYS_OFF_FILE, index=False)
                        push_to_github("data/days_off.csv", "Deleted selected time off dates")
                        st.success("Selected dates deleted!")
                    else:
                        st.info("No dates selected.")
            else:
                st.info("No upcoming time off saved.")

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

    # =========================================================
    # Period Settings (Bottom of Data Entry)
    # =========================================================
    st.markdown("\n", unsafe_allow_html=True)
    st.subheader("Performance Period Settings")
    
    # Ensure the file exists with the expected columns
    if not os.path.exists(PERIOD_FILE):
        pd.DataFrame(columns=["StartDate", "EndDate", "HoursGoal"]).to_csv(PERIOD_FILE, index=False)
    
    period_df = pd.read_csv(PERIOD_FILE)
    
    # Normalize column names (handles your " HoursGoal" header)
    period_df.columns = [c.strip() for c in period_df.columns]
    
    # Ensure required columns exist
    for col in ["StartDate", "EndDate", "HoursGoal"]:
        if col not in period_df.columns:
            period_df[col] = ""
    
    # Coerce dates safely for UI defaults
    period_df["StartDate"] = pd.to_datetime(period_df["StartDate"], errors="coerce")
    period_df["EndDate"] = pd.to_datetime(period_df["EndDate"], errors="coerce")
    
    # Coerce HoursGoal to numeric safely (handles " 653")
    period_df["HoursGoal"] = pd.to_numeric(period_df["HoursGoal"], errors="coerce")
    
    # Default values (use first row if it exists)
    default_start = period_df["StartDate"].iloc[0].date() if len(period_df) > 0 and pd.notna(period_df["StartDate"].iloc[0]) else date.today()
    default_end = period_df["EndDate"].iloc[0].date() if len(period_df) > 0 and pd.notna(period_df["EndDate"].iloc[0]) else date.today()
    default_goal = float(period_df["HoursGoal"].iloc[0]) if len(period_df) > 0 and pd.notna(period_df["HoursGoal"].iloc[0]) else 0.0
    
    # Quick entry row (start/end/hours + save)
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    with c1:
        ps_start = st.date_input("Start Date", value=default_start, key="ps_start")
    with c2:
        ps_end = st.date_input("End Date", value=default_end, key="ps_end")
    with c3:
        ps_goal = st.number_input("Hours Goal", min_value=0.0, step=1.0, value=default_goal, key="ps_goal")
    with c4:
        if st.button("Save Period", key="ps_save_period", use_container_width=True):
            if ps_start > ps_end:
                st.error("Start Date must be on or before End Date.")
            else:
                # Store as a single-row settings file (overwrite row 0)
                new_settings = pd.DataFrame([{
                    "StartDate": ps_start.strftime("%Y-%m-%d"),
                    "EndDate": ps_end.strftime("%Y-%m-%d"),
                    "HoursGoal": ps_goal
                }])
    
                new_settings.to_csv(PERIOD_FILE, index=False)
                push_to_github("data/period_settings.csv", "Updated period settings (dates + hours goal)")
                st.success("Period settings saved!")
    
    # Editable view (for quick edits)
    st.markdown("### Edit period_settings.csv")
    editable = period_df.copy()
    # Convert back to strings for display/editing
    editable["StartDate"] = editable["StartDate"].dt.strftime("%Y-%m-%d")
    editable["EndDate"] = editable["EndDate"].dt.strftime("%Y-%m-%d")
    editable["HoursGoal"] = editable["HoursGoal"].fillna(0)
    
    edited_period = st.data_editor(
        editable[["StartDate", "EndDate", "HoursGoal"]],
        num_rows="dynamic",
        hide_index=True,
        key="ps_editor"
    )
    
    if st.button("Save Period Settings Changes", key="ps_save_editor"):
        cleaned = edited_period.dropna(how="all").copy()
    
        # Strip whitespace
        for col in ["StartDate", "EndDate"]:
            cleaned[col] = cleaned[col].astype(str).str.strip()
    
        # Validate and coerce
        cleaned["StartDate"] = pd.to_datetime(cleaned["StartDate"], errors="coerce")
        cleaned["EndDate"] = pd.to_datetime(cleaned["EndDate"], errors="coerce")
        cleaned["HoursGoal"] = pd.to_numeric(cleaned["HoursGoal"], errors="coerce").fillna(0)
    
        cleaned = cleaned.dropna(subset=["StartDate", "EndDate"])
    
        # Validate date order per row
        bad_rows = cleaned[cleaned["StartDate"] > cleaned["EndDate"]]
        if len(bad_rows) > 0:
            st.error("One or more rows have StartDate after EndDate. Fix and try again.")
        else:
            # Save in consistent format
            cleaned["StartDate"] = cleaned["StartDate"].dt.strftime("%Y-%m-%d")
            cleaned["EndDate"] = cleaned["EndDate"].dt.strftime("%Y-%m-%d")
            cleaned = cleaned[["StartDate", "EndDate", "HoursGoal"]].reset_index(drop=True)
    
            cleaned.to_csv(PERIOD_FILE, index=False)
            push_to_github("data/period_settings.csv", "Edited period settings table")
            st.success("period_settings.csv updated!")




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

            # Remove from active files
            df_clients = df_clients[df_clients["Client"] != selected_client]
            df_categories = df_categories[df_categories["Client"] != selected_client]
            df_todos = df_todos[df_todos["Client"] != selected_client]

            # Save all files
            df_clients.to_csv(CLIENTS_FILE, index=False)
            df_categories.to_csv(CATEGORIES_FILE, index=False)
            df_todos.to_csv(TODOS_FILE, index=False)
            df_hours.to_csv(HOURS_FILE, index=False)
            df_archive_clients.to_csv(ARCHIVE_CLIENTS, index=False)
            df_archive_categories.to_csv(ARCHIVE_CATEGORIES, index=False)
            df_archive_todos.to_csv(ARCHIVE_TODOS, index=False)

            # Push to GitHub
            push_to_github("data/clients.csv", "Archived client")
            push_to_github("data/categories.csv", "Archived client categories")
            push_to_github("data/todos.csv", "Archived client todos")
            push_to_github("data/hours.csv", "Archived client hours")
            push_to_github("data/archive_clients.csv", "Updated archive clients")
            push_to_github("data/archive_categories.csv", "Updated archive categories")
            push_to_github("data/archive_todos.csv", "Updated archive todos")

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
                default_color = (
                    row["Color"]
                    if isinstance(row["Color"], str) and row["Color"].startswith("#") and len(row["Color"]) == 7
                    else "#1f77b4"
                )
                
                new_color = st.color_picker("", default_color, key=f"color_{i}")
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






































































































