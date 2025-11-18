import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
import base64

# -----------------------------
# GitHub Config (from Streamlit Secrets)
# GitHub Config
# -----------------------------
print("Hello World")

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]
BRANCH = "main"

# -----------------------------
# Data Setup
# -----------------------------
DATA_DIR = "data"
CLIENTS_FILE = os.path.join(DATA_DIR, "clients.csv")
HOURS_FILE = os.path.join(DATA_DIR, "hours.csv")
GOALS_FILE = os.path.join(DATA_DIR, "goals.csv")
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.csv")
TODOS_FILE = os.path.join(DATA_DIR, "todos.csv")

os.makedirs(DATA_DIR, exist_ok=True)

# -----------------------------
# GitHub Functions
# -----------------------------
def fetch_from_github(file_path):
    """Fetch file content from GitHub and save locally."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}?ref={BRANCH}"
    response = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    if response.status_code == 200:
        content = base64.b64decode(response.json()["content"]).decode("utf-8")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        st.info(f"Fetched latest {file_path} from GitHub.")
    else:
        st.warning(f"{file_path} not found in GitHub. Will create it locally.")
        st.warning(f"{file_path} not found in GitHub. Will create locally.")

def push_to_github(file_path, commit_message):
    """Push local file to GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    with open(file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    # Check if file exists to get SHA
    response = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    sha = response.json().get("sha")

    data = {
        "message": commit_message,
        "content": content,
        "branch": BRANCH
    }
    data = {"message": commit_message, "content": content, "branch": BRANCH}
    if sha:
        data["sha"] = sha

    r = requests.put(url, json=data, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    if r.status_code in [200, 201]:
        st.success(f"Pushed {file_path} to GitHub!")
    else:
    if r.status_code not in [200, 201]:
        st.error(f"Failed to push {file_path}: {r.json()}")

# -----------------------------
# Initialize Data
# Sync Files from GitHub
# -----------------------------
for file in ["data/clients.csv", "data/hours.csv", "data/goals.csv"]:
for file in ["data/clients.csv", "data/hours.csv", "data/goals.csv", "data/categories.csv", "data/todos.csv"]:
    fetch_from_github(file)

# Ensure files exist locally
for file, cols in [
# Initialize files if missing
init_files = [
    (CLIENTS_FILE, ["Client"]),
    (HOURS_FILE, ["Date", "Client", "Hours", "Description"]),
    (GOALS_FILE, ["Month", "GoalHours"])
]:
    (GOALS_FILE, ["Month", "GoalHours"]),
    (CATEGORIES_FILE, ["Client", "Category"]),
    (TODOS_FILE, ["Client", "Category", "Task", "Priority", "DateCreated", "DateCompleted"])
]
for file, cols in init_files:
    if not os.path.exists(file):
        pd.DataFrame(columns=cols).to_csv(file, index=False)
        push_to_github(file, f"Created {file}")

# -----------------------------
# Sidebar Navigation
# -----------------------------
st.sidebar.title("Navigation")
pages = ["Data Entry", "Reports", "To-Do", "History"]
pages = ["Data Entry", "To-Do", "Reports", "History"]
selected_page = st.sidebar.radio("Go to", pages)

# -----------------------------
# Page: Data Entry
# -----------------------------
if selected_page == "Data Entry":
    st.title("Data Entry")

    # Form 1: Add New Client
    # Add Client
    st.subheader("Add New Client")
    new_client = st.text_input("Client Name")
    if st.button("Add Client"):
        if new_client.strip():
            df_clients = pd.read_csv(CLIENTS_FILE)
            if new_client not in df_clients["Client"].values:
                df_clients.loc[len(df_clients)] = [new_client]
                df_clients.to_csv(CLIENTS_FILE, index=False)
                st.success(f"Client '{new_client}' added!")
                push_to_github("data/clients.csv", "Updated clients list")
            else:
                st.warning("Client already exists.")
        else:
            st.error("Please enter a valid client name.")

    # Form 2: Log Hours
    # Log Hours
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
            push_to_github("data/hours.csv", "Updated hours log")

    # Form 3: Set Hour Goals
    # Set Goals
    st.subheader("Set Hour Goals")
    month = st.selectbox("Month", [f"{m:02d}" for m in range(1, 13)])
    goal_hours = st.number_input("Goal Hours", min_value=0.0, step=1.0)
    if st.button("Save Goal"):
        df_goals = pd.read_csv(GOALS_FILE)
        df_goals.loc[len(df_goals)] = [month, goal_hours]
        df_goals.to_csv(GOALS_FILE, index=False)
        st.success("Goal saved successfully!")
        push_to_github("data/goals.csv", "Updated goals list")

# -----------------------------
# Page: To-Do
# -----------------------------
elif selected_page == "To-Do":
    st.title("To-Do List")

    df_clients = pd.read_csv(CLIENTS_FILE)
    df_categories = pd.read_csv(CATEGORIES_FILE)
    df_todos = pd.read_csv(TODOS_FILE)

    # Add Category
    st.subheader("Add Category")
    if len(df_clients) == 0:
        st.warning("Add clients first!")
    else:
        cat_client = st.selectbox("Select Client for Category", df_clients["Client"].tolist())
        new_category = st.text_input("New Category")
        if st.button("Add Category"):
            if new_category.strip():
                df_categories.loc[len(df_categories)] = [cat_client, new_category]
                df_categories.to_csv(CATEGORIES_FILE, index=False)
                st.success(f"Category '{new_category}' added for client '{cat_client}'!")
                push_to_github("data/categories.csv", "Updated categories list")
            else:
                st.error("Please enter a valid category name.")

    # Add To-Do
    st.subheader("Add To-Do Item")
    if len(df_clients) == 0:
        st.warning("Add clients first!")
    else:
        todo_client = st.selectbox("Select Client", df_clients["Client"].tolist())
        client_categories = df_categories[df_categories["Client"] == todo_client]["Category"].tolist()
        if len(client_categories) == 0:
            st.warning("Add categories for this client first!")
        else:
            todo_category = st.selectbox("Select Category", client_categories)
            todo_task = st.text_input("Task Description")
            priority = st.slider("Priority (1=Low, 5=High)", 1, 5, 3)
            if st.button("Add Task"):
                df_todos.loc[len(df_todos)] = [todo_client, todo_category, todo_task, priority, str(datetime.today().date()), ""]
                df_todos.to_csv(TODOS_FILE, index=False)
                st.success("Task added successfully!")
                push_to_github("data/todos.csv", "Updated To-Do list")

    # Active To-Dos
    st.subheader("Active To-Dos")
    active_todos = df_todos[df_todos["DateCompleted"] == ""].copy()
    if len(active_todos) == 0:
        st.info("No active tasks.")
    else:
        active_todos = active_todos.sort_values(by="Priority", ascending=False)
        edited_todos = st.data_editor(active_todos, num_rows="dynamic", use_container_width=True)

        # Save edits
        if st.button("Save Changes"):
            df_todos.update(edited_todos)
            df_todos.to_csv(TODOS_FILE, index=False)
            st.success("Changes saved!")
            push_to_github("data/todos.csv", "Updated To-Do list")

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

