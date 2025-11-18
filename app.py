import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
import base64

# -------------------------------------------------
# GitHub Config (from Streamlit Secrets)
# -------------------------------------------------
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]
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
# GitHub Functions
# -------------------------------------------------
def fetch_from_github(file_path):
    """Fetch file content from GitHub and save locally."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}?ref={BRANCH}"
    response = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    if response.status_code == 200:
        content = base64.b64decode(response.json()["content"]).decode("utf-8")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        st.warning(f"{file_path} not found in GitHub. Will create locally.")

def push_to_github(file_path, commit_message):
    """Push local file to GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"
    with open(file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")
    response = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    sha = response.json().get("sha")
    data = {
        "message": commit_message,
        "content": content,
        "branch": BRANCH
    }
    if sha:
        data["sha"] = sha
    r = requests.put(url, json=data, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    if r.status_code in [200, 201]:
        st.success(f"Pushed {file_path} to GitHub!")
    else:
        st.error(f"Failed to push {file_path}: {r.json()}")

# -------------------------------------------------
# Initialize Data
# -------------------------------------------------
# Sync Files from GitHub
for file in ["data/clients.csv", "data/hours.csv", "data/goals.csv", "data/categories.csv", "data/todos.csv"]:
    fetch_from_github(file)

# Ensure files exist locally
init_files = [
    (CLIENTS_FILE, ["Client"]),
    (HOURS_FILE, ["Date", "Client", "Hours", "Description"]),
    (GOALS_FILE, ["Month", "GoalHours"]),
    (CATEGORIES_FILE, ["Client", "Category"]),
    (TODOS_FILE, ["Client", "Category", "Task", "Priority", "DateCreated", "DateCompleted"])
]

for file, cols in init_files:
    if not os.path.exists(file):
        pd.DataFrame(columns=cols).to_csv(file, index=False)
        push_to_github(file, f"Created {file}")

# -------------------------------------------------
# Sidebar Navigation
# -------------------------------------------------
st.sidebar.title("Navigation")
pages = ["Data Entry", "To-Do", "Reports", "History"]
selected_page = st.sidebar.radio("Go to", pages)

# -------------------------------------------------
# Page: Data Entry
# -------------------------------------------------
if selected_page == "Data Entry":
    st.title("Data Entry")

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

# -------------------------------------------------
# Page: To-Do
# -------------------------------------------------
elif selected_page == "To-Do":
    st.title("To-Do List")

    # Load data
    df_clients = pd.read_csv(CLIENTS_FILE)
    df_categories = pd.read_csv(CATEGORIES_FILE)
    df_todos = pd.read_csv(TODOS_FILE)

    # -------------------------------
    # Add Category (One Line Layout)
    # -------------------------------
    st.subheader("Add Category")
    if len(df_clients) == 0:
        st.warning("Add clients first!")
    else:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            cat_client = st.selectbox("Client", df_clients["Client"].tolist(), key="cat_client")
        with col2:
            new_category = st.text_input("New Category", key="new_category")
        with col3:
            if st.button("Add Category"):
                if new_category.strip():
                    df_categories.loc[len(df_categories)] = [cat_client, new_category]
                    df_categories.to_csv(CATEGORIES_FILE, index=False)
                    st.success(f"Category '{new_category}' added for '{cat_client}'!")
                    push_to_github("data/categories.csv", "Updated categories list")
                    df_categories = pd.read_csv(CATEGORIES_FILE)
                else:
                    st.error("Please enter a valid category name.")

    # -------------------------------
    # Add To-Do Item (One Line Layout)
    # -------------------------------
    st.subheader("Add To-Do Item")
    if len(df_clients) == 0:
        st.warning("Add clients first!")
    else:
        col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 2, 1])
        with col1:
            todo_client = st.selectbox("Client", df_clients["Client"].tolist(), key="todo_client")
        with col2:
            client_categories = df_categories[df_categories["Client"] == todo_client]["Category"].tolist()
            todo_category = st.selectbox("Category", client_categories if client_categories else ["No categories"], key="todo_category")
        with col3:
            todo_task = st.text_input("Task", key="todo_task")
        with col4:
            priority = st.slider("Priority", 1, 5, 3, key="priority")
        with col5:
            if st.button("Add Task"):
                if todo_task.strip() and todo_category != "No categories":
                    df_todos.loc[len(df_todos)] = [
                        todo_client, todo_category, todo_task, priority,
                        str(datetime.today().date()), ""
                    ]
                    df_todos.to_csv(TODOS_FILE, index=False)
                    st.success("Task added successfully!")
                    push_to_github("data/todos.csv", "Updated To-Do list")
                    df_todos = pd.read_csv(TODOS_FILE)
                else:
                    st.error("Please enter a valid task and category.")

    # -------------------------------
    # Active To-Dos (Editable Tables)
    # -------------------------------
    st.subheader("Active To-Dos")
    active_todos = df_todos[df_todos["DateCompleted"].isna() | (df_todos["DateCompleted"] == "")].copy()

    if len(active_todos) == 0:
        st.info("No active tasks.")
    else:
        clients_with_tasks = active_todos["Client"].dropna().unique().tolist()
        selected_clients = st.multiselect("Filter by Client", clients_with_tasks, default=clients_with_tasks)

        if len(selected_clients) > 0:
            cols = st.columns(len(selected_clients))
            for i, client in enumerate(selected_clients):
                client_tasks = active_todos[active_todos["Client"] == client].sort_values(by="Priority", ascending=False)
                with cols[i]:
                    st.markdown(f"### {client}")
                    edited_table = st.data_editor(
                        client_tasks[["Category", "Task", "Priority", "DateCreated", "DateCompleted"]].reset_index(drop=True),
                        num_rows="dynamic",
                        width="stretch"
                    )

                    # Save changes button
                    if st.button(f"Save Changes for {client}"):
                        # Replace rows for this client with edited data
                        df_todos = df_todos[df_todos["Client"] != client]
                        edited_table["Client"] = client
                        df_todos = pd.concat([df_todos, edited_table], ignore_index=True)
                        df_todos.to_csv(TODOS_FILE, index=False)
                        push_to_github("data/todos.csv", "Updated To-Do list")
                        st.success(f"Changes saved for {client}!")
# -------------------------------------------------
# Placeholder Pages
# -------------------------------------------------
elif selected_page == "Reports":
    st.title("Reports")
    st.write("Coming soon: charts and summaries.")

elif selected_page == "History":
    st.title("History")

    # Load data
    df_hours = pd.read_csv(HOURS_FILE)
    df_todos = pd.read_csv(TODOS_FILE)

    # -------------------------------
    # Client Filter
    # -------------------------------
    all_clients = sorted(set(df_hours["Client"].dropna().tolist() + df_todos["Client"].dropna().tolist()))
    selected_clients = st.multiselect("Filter by Client", all_clients, default=all_clients)

    # Apply filter
    filtered_hours = df_hours[df_hours["Client"].isin(selected_clients)] if len(selected_clients) > 0 else df_hours
    filtered_todos = df_todos[df_todos["Client"].isin(selected_clients)] if len(selected_clients) > 0 else df_todos

    # -------------------------------
    # Layout: Editable Hours + To-Do History
    # -------------------------------
    col1, col2 = st.columns(2)

    # Editable Hours History
    with col1:
        st.subheader("Logged Hours History")
        if len(filtered_hours) == 0:
            st.info("No hours logged for selected client(s).")
        else:
            edited_hours = st.data_editor(
                filtered_hours[["Date", "Client", "Hours", "Description"]].reset_index(drop=True),
                num_rows="dynamic",
                width="stretch"
            )
            if st.button("Save Hours Changes"):
                df_hours = edited_hours
                df_hours.to_csv(HOURS_FILE, index=False)
                push_to_github("data/hours.csv", "Updated hours history")
                st.success("Hours history updated!")

    # Editable To-Do History
    with col2:
        st.subheader("To-Do History")
        if len(filtered_todos) == 0:
            st.info("No tasks recorded for selected client(s).")
        else:
            edited_todos = st.data_editor(
                filtered_todos[["Client", "Category", "Task", "Priority", "DateCreated", "DateCompleted"]].reset_index(drop=True),
                num_rows="dynamic",
                width="stretch"
            )
            if st.button("Save To-Do Changes"):
                df_todos = edited_todos
                df_todos.to_csv(TODOS_FILE, index=False)
                push_to_github("data/todos.csv", "Updated To-Do history")
                st.success("To-Do history updated!")



