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
# Custom CSS for Dark Theme and Boxed Forms
# -------------------------------------------------
# -------------------------------------------------
# Improved Dark Theme CSS
# -------------------------------------------------



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
        True
    else:
        st.error(f"Failed to push {file_path}: {r.json()}")

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
apply_css_from_github()




# Sync Files from GitHub
for file in ["data/clients.csv", "data/hours.csv", "data/goals.csv", "data/categories.csv", "data/todos.csv", "data/style.css"]:
    fetch_from_github(file)

st.markdown('<link rel="stylesheet" href="YOUR_GITHUB_RAW_CSS_URL">', unsafe_allow_html=True)
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
pages = ["Home", "Reports", "Data Entry", "Archive"]
selected_page = st.sidebar.radio("Go to", pages)



st.markdown("""
<style>
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
# Load To-Dos
df_todos = pd.read_csv(TODOS_FILE)

# Ensure required columns exist
required_cols = ["Client", "Category", "Task", "Priority", "DateCreated", "DateCompleted", "Notes"]
for col in required_cols:
    if col not in df_todos.columns:
        df_todos[col] = ""

# -----------------------------
# Log Hours
# -----------------------------
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
            df_hours = pd.read_csv(HOURS_FILE)
            new_row = {
                "Date": str(date_val),
                "Client": client,
                "Hours": hours,
                "Description": description
            }
            df_hours = pd.concat([df_hours, pd.DataFrame([new_row])], ignore_index=True)
            df_hours.to_csv(HOURS_FILE, index=False)
            push_to_github("data/hours.csv", "Updated hours log")
            st.success("Hours logged successfully!")

# -----------------------------
# Add To-Do Item
# -----------------------------
st.subheader("Add To-Do Item")
if len(df_clients) == 0:
    st.warning("Add clients first!")
else:
    col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 2, 1])
    with col1:
        todo_date = st.date_input("Date Created", datetime.today(), key="todo_date")
        todo_client = st.selectbox("Client", df_clients["Client"].tolist(), key="todo_client")
    with col2:
        client_categories = df_categories[df_categories["Client"] == todo_client]["Category"].tolist()
        todo_category = st.selectbox("Category", client_categories if client_categories else ["No categories"], key="todo_category")
    with col3:
        todo_task = st.text_input("Task", key="todo_task")
    with col4:
        priority = st.slider("Priority", 1, 5, 3, key="todo_priority")
    with col5:
        if st.button("Add Task", key="add_task"):
            if todo_task.strip() and todo_category != "No categories":
                df_todos.loc[len(df_todos)] = [todo_client, todo_category, todo_task, priority, str(todo_date), "", ""]
                df_todos.to_csv(TODOS_FILE, index=False)
                push_to_github("data/todos.csv", "Added new task with DateCreated")
                st.success("Task added successfully!")
            else:
                st.error("Please enter a valid task and category.")
    st.markdown('\\n', unsafe_allow_html=True)

# -----------------------------
# Active To-Dos with Expanders
# -----------------------------
st.subheader("Active To-Dos")
active_todos = df_todos[(df_todos["DateCompleted"].isna()) | (df_todos["DateCompleted"] == "")].copy()
if len(active_todos) == 0:
    st.info("No active tasks.")
else:
    clients_with_tasks = active_todos["Client"].dropna().unique().tolist()
    selected_clients = st.multiselect("Filter by Client", clients_with_tasks, default=clients_with_tasks, key="filter_clients")
    cols = st.columns(len(selected_clients))
    for i, client in enumerate(selected_clients):
        with cols[i]:
            color = df_clients.loc[df_clients["Client"] == client, "Color"].values[0]
            st.markdown(f"<div style='background-color:{color}; padding:10px; border-radius:5px;'><h4 style='color:white; font-size:20px;'>{client}</h4></div>", unsafe_allow_html=True)
            client_tasks = active_todos[active_todos["Client"] == client].sort_values(by="Priority", ascending=False)
            for idx, row in client_tasks.iterrows():
                with st.expander(f"{row['Task']} (Priority: {row['Priority']})", expanded=False):
                    st.markdown(f"### Task: {row['Task']}")
                    st.write(f"Category: {row['Category']}")
                    created_date = row["DateCreated"]
                    st.write(f"Created: {created_date}")
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

# -----------------------------
# Today's Hours (Single Table)
# -----------------------------
st.subheader("Today's Hours")
df_hours = pd.read_csv(HOURS_FILE)
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
    st.success("Hours saved successfully!")





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

    # Convert dates
    hours_df["Date"] = pd.to_datetime(hours_df["Date"])
    days_off_df["Date"] = pd.to_datetime(days_off_df["Date"])
    now = datetime.today()
    today = now.date()

    # -------------------------
    # Load or Initialize Performance Period
    # -------------------------
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

    # -------------------------
    # BAN Calculations
    # -------------------------
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

    # -------------------------
    # Weekly Snapshot Chart (Weekdays Only)
    # -------------------------
    st.markdown('<div class="form-box">', unsafe_allow_html=True)

    if "week_offset" not in st.session_state:
        st.session_state.week_offset = 0

    today = pd.Timestamp.today()
    start_of_week = (today + pd.Timedelta(weeks=st.session_state.week_offset)).normalize() - pd.Timedelta(days=today.weekday())
    end_of_week = start_of_week + pd.Timedelta(days=6)

    # Dynamic title with date range
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

    # Only Monday-Friday
    weekdays = pd.date_range(start_of_week, end_of_week, freq="D")
    weekdays = [d for d in weekdays if d.weekday() < 5]  # 0=Mon, 4=Fri

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

    # -------------------------
    # Date Range Filter for Bottom Charts
    # -------------------------
    st.markdown('<div class="form-box">', unsafe_allow_html=True)
    st.subheader("Filter for Monthly & Client Charts")
    col_start, col_end = st.columns([1, 1])
    with col_start:
        chart_start = st.date_input("Chart Start Date", date(now.year, max(now.month - 4, 1), 1))
    with col_end:
        chart_end = st.date_input("Chart End Date", date(now.year, now.month, calendar.monthrange(now.year, now.month)[1]))

    filtered_hours = hours_df[(hours_df["Date"] >= pd.to_datetime(chart_start)) & (hours_df["Date"] <= pd.to_datetime(chart_end))]
    filtered_merged = merged_period[(pd.to_datetime(merged_period["Month"] + "-01") >= pd.to_datetime(chart_start)) &
                                    (pd.to_datetime(merged_period["Month"] + "-01") <= pd.to_datetime(chart_end))]
    filtered_merged["MonthDate"] = pd.to_datetime(filtered_merged["Month"] + "-01")
    filtered_merged = filtered_merged.sort_values("MonthDate")
    filtered_merged["MonthLabel"] = filtered_merged["MonthDate"].dt.strftime("%b %Y")

    # -------------------------
    # Monthly & Pie Charts
    # -------------------------
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
            pie_fig = px.pie(filtered_hours, names="Client", values="Hours",
                             color="Client", color_discrete_map=client_colors)
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

    # -------------------------------
    # Client Filter
    # -------------------------------
    st.markdown('<div class="form-box">', unsafe_allow_html=True)
    st.subheader("Filter by Client")
    all_clients = sorted(set(df_hours["Client"].dropna().tolist() + df_todos["Client"].dropna().tolist()))
    selected_clients = st.multiselect("Select Clients", all_clients, default=all_clients)
    st.markdown('</div>', unsafe_allow_html=True)

    # Apply filter
    filtered_hours = df_hours[df_hours["Client"].isin(selected_clients)] if len(selected_clients) > 0 else df_hours
    filtered_todos = df_todos[df_todos["Client"].isin(selected_clients)] if len(selected_clients) > 0 else df_todos

    # -------------------------------
    # Editable Hours + To-Do History
    # -------------------------------
    st.markdown('<div class="form-box">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    # Editable Hours History
    with col1:
        st.subheader("Logged Hours History")
        if len(filtered_hours) == 0:
            st.info("No hours logged for selected client(s).")
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
                num_rows="dynamic",
                width="stretch",
                hide_index=True
            )

            if st.button("Save Hours Changes"):
                # Remove rows where all columns are empty
                cleaned_hours = edited_hours.dropna(how="all")
                cleaned_hours = cleaned_hours[(cleaned_hours != "").any(axis=1)]
                cleaned_hours.to_csv(HOURS_FILE, index=False)
                push_to_github("data/hours.csv", "Updated hours history (removed empty rows)")
                st.success("Hours history updated! Empty rows deleted.")

    # Editable To-Do History
    with col2:
        st.subheader("To-Do History")
        if len(filtered_todos) == 0:
            st.info("No tasks recorded for selected client(s).")
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
                num_rows="dynamic",
                width="stretch",
                hide_index=True
            )

            if st.button("Save To-Do Changes"):
                # Remove rows where all columns are empty
                cleaned_todos = edited_todos.dropna(how="all")
                cleaned_todos = cleaned_todos[(cleaned_todos != "").any(axis=1)]
                cleaned_todos.to_csv(TODOS_FILE, index=False)
                push_to_github("data/todos.csv", "Updated To-Do history (removed empty rows)")
                st.success("To-Do history updated! Empty rows deleted.")

    st.markdown('</div>', unsafe_allow_html=True)
    # -------------------------
    # Add New Client (Middle)
    # -------------------------
    st.markdown('<div class="form-box">', unsafe_allow_html=True)
    st.subheader("Add New Client")
    new_client = st.text_input("Client Name")
    client_color = st.color_picker("Pick Client Color", "#FFFFFF")
    if st.button("Add Client"):
        if new_client.strip():
            df_clients = pd.read_csv(CLIENTS_FILE)
    
            # Ensure both columns exist
            if "Color" not in df_clients.columns:
                df_clients["Color"] = ""  # Add empty Color column if missing
    
            if new_client not in df_clients["Client"].values:
                # Append new row safely
                new_row = pd.DataFrame([[new_client, client_color]], columns=["Client", "Color"])
                df_clients = pd.concat([df_clients, new_row], ignore_index=True)
    
                # Save and push
                df_clients.to_csv(CLIENTS_FILE, index=False)
                st.success(f"Client '{new_client}' added with color {client_color}!")
                push_to_github("data/clients.csv", "Updated clients list")
            else:
                st.warning("Client already exists.")
        else:
            st.error("Please enter a valid client name.")
    st.markdown('</div>', unsafe_allow_html=True)



    # -------------------------
    # Set Hour Goals (Bottom)
    # -------------------------
    st.markdown('<div class="form-box">', unsafe_allow_html=True)
    st.subheader("Set Hour Goals")
    month = st.selectbox("Month", [f"{m:02d}" for m in range(1, 13)])
    goal_hours = st.number_input("Goal Hours", min_value=0.0, step=1.0)
    if st.button("Save Goal"):
        df_goals = pd.read_csv(GOALS_FILE)
        df_goals.loc[len(df_goals)] = [month, goal_hours]
        df_goals.to_csv(GOALS_FILE, index=False)
        st.success("Goal saved successfully!")
        push_to_github("data/goals.csv", "Updated goals list")
    st.markdown('</div>', unsafe_allow_html=True)

    #----------------------------------
    #Days Off
    #-----------------------------------
    # File path
    DAYS_OFF_FILE = os.path.join(DATA_DIR, "days_off.csv")

    # Ensure file exists
    if not os.path.exists(DAYS_OFF_FILE):
        pd.DataFrame(columns=["Date", "Reason"]).to_csv(DAYS_OFF_FILE, index=False)

    # Load data
    df_days_off = pd.read_csv(DAYS_OFF_FILE)

    # -------------------------------
    # Add New Day Off
    # -------------------------------
    st.markdown('<div class="form-box">', unsafe_allow_html=True)
    st.subheader("Add a Day Off")
    new_date = st.date_input("Select Date")
    new_reason = st.text_input("Reason for Day Off")
    if st.button("Add Day Off"):
        if new_reason.strip():
            df_days_off.loc[len(df_days_off)] = [str(new_date), new_reason]
            df_days_off.to_csv(DAYS_OFF_FILE, index=False)
            push_to_github("data/days_off.csv", "Added new day off")
            st.success("Day off added successfully!")
        else:
            st.error("Please enter a reason.")
    st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------------
    # Editable Days Off Table
    # -------------------------------
    st.markdown('<div class="form-box">', unsafe_allow_html=True)
    st.subheader("Manage Days Off")
    edited_days_off = st.data_editor(
        df_days_off.reset_index(drop=True),
        num_rows="dynamic",
        width="stretch"
    )

    if st.button("Save Changes"):
        df_days_off = edited_days_off
        df_days_off.to_csv(DAYS_OFF_FILE, index=False)
        push_to_github("data/days_off.csv", "Updated days off list")
        st.success("Changes saved!")
    st.markdown('</div>', unsafe_allow_html=True)

 # Today's Hours
    # -----------------------
    HOURS_FILE = "data/hours.csv"
    df_hours = pd.read_csv(HOURS_FILE)
    today_str = datetime.today().strftime("%Y-%m-%d")
    df_today = df_hours[df_hours["Date"] == today_str]
    new_row = {"Date": today_str, "Client": "", "Hours": 0.0, "Description": ""}
    df_today_with_blank = pd.concat([df_today, pd.DataFrame([new_row])], ignore_index=True)
    half = len(df_today_with_blank) // 2
    df_left = df_today_with_blank.iloc[:half+1]
    df_right = df_today_with_blank.iloc[half+1:]
    col1, col2 = st.columns(2)
    with col1:
        edited_left = st.data_editor(df_left, num_rows="dynamic", key="editor_left")
    with col2:
        edited_right = st.data_editor(df_right, num_rows="dynamic", key="editor_right")

    edited_hours = pd.concat([edited_left, edited_right], ignore_index=True)

    st.markdown('\n', unsafe_allow_html=True)

    # -----------------------
    # Unified Save Button
    # -----------------------
    if st.button("Save All Hours Changes"):

       
        # Save Hours edits
        edited_hours = edited_hours.dropna(subset=["Client"])
        edited_hours = edited_hours[edited_hours["Client"].str.strip() != ""]
        df_hours = pd.read_csv(HOURS_FILE)
        df_hours = df_hours[df_hours["Date"] != today_str]
        df_hours = pd.concat([df_hours, edited_hours], ignore_index=True)

        # Remove rows with empty Client
        df_hours = df_hours[df_hours["Client"].notna() & (df_hours["Client"].str.strip() != "")]

        df_hours.to_csv(HOURS_FILE, index=False)

        # Push updates
        push_to_github("data/todos.csv", "Updated To-Do list")
        push_to_github("data/hours.csv", "Updated hours log")

        st.success("All changes saved successfully!")


    st.markdown('\n', unsafe_allow_html=True)





    

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









































































