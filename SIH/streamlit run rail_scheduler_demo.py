import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

st.set_page_config(page_title="AI-Assisted Train Scheduler", layout="wide")

st.title("🚆 AI-Assisted Hybrid Railway Traffic Management Prototype")

st.markdown("""
This prototype demonstrates a simple **train scheduling system**.
- Input trains with arrival times and priorities
- System assigns section entry times
- Visualize results in a **Gantt chart**
""")

# -------------------------
# Input Data
# -------------------------
st.subheader("📥 Enter Train Timetable")

default_data = {
    "train_id": ["T1", "T2", "T3"],
    "arrival_sec": [0, 120, 240],
    "priority": [2, 1, 3],
}

df_init = pd.DataFrame(default_data)
edited = st.data_editor(df_init, num_rows="dynamic")

if st.button("Run Scheduler"):
    st.subheader("📊 Optimized Schedule")

    # -------------------------
    # Simple Greedy Scheduling
    # -------------------------
    trains = edited.copy()
    trains["arrival_sec"] = pd.to_numeric(trains["arrival_sec"], errors="coerce").fillna(0).astype(int)
    trains["priority"] = pd.to_numeric(trains["priority"], errors="coerce").fillna(1).astype(int)

    # Sort trains by arrival, then by priority
    trains = trains.sort_values(by=["arrival_sec", "priority"], ascending=[True, False]).reset_index(drop=True)

    section_time = 180  # seconds each train occupies the section
    current_time = 0
    schedule = []

    for _, row in trains.iterrows():
        arrival = int(row["arrival_sec"])
        start_time = max(arrival, current_time)
        exit_time = start_time + section_time
        schedule.append({
            "train_id": row["train_id"],
            "arrival_sec": arrival,
            "priority": int(row["priority"]),
            "entry": start_time,
            "exit": exit_time
        })
        current_time = exit_time

    schedule_df = pd.DataFrame(schedule)
    st.dataframe(schedule_df)

    # -------------------------
    # Visualization: Gantt Chart
    # -------------------------
    st.subheader("📈 Schedule Visualization")

    fig, ax = plt.subplots(figsize=(10, 4))
    plot_df = schedule_df.copy()

    for idx, row in plot_df.iterrows():
        start = int(row["entry"])
        exit_time = int(row["exit"])
        duration = exit_time - start
        arrival = int(row["arrival_sec"])
        priority = int(row["priority"])

        # Draw section block
        ax.add_patch(Rectangle((float(start), float(idx - 0.3)), float(duration), 0.6, color="tab:blue"))

        # Add label in the center of the block
        ax.text(
            float(start + duration/2), float(idx),
            f"{row['train_id']} (p={priority})",
            va='center', ha='center', fontsize=9, color='white'
        )

        # Show actual arrival as a marker
        ax.plot([float(arrival)], [float(idx)], marker='v', color="red")

    ax.set_xlabel("Time (sec)")
    ax.set_ylabel("Trains")
    ax.set_yticks(range(len(plot_df)))
    ax.set_yticklabels(plot_df["train_id"].tolist())
    ax.set_title("Train Section Allocation (Gantt Chart)")
    st.pyplot(fig)
