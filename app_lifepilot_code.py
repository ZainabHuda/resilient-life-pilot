#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    layout="wide",
    page_title="The Resilient Life-Pilot"
)




# In[2]:


# Custom CSS for a clean, modern look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid #007bff;
        color: #007bff;
        background-color: #ffffff;
        font-weight: bold;
    }
    .stButton>button:hover {
        color: #ffffff;
        background-color: #007bff;
    }
    .thinking-box {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        font-weight: bold;
    }
    .fragile-thinking {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeeba;
    }
    .resilient-adapting {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("✈️ The Resilient Life-Pilot: Navigating Your Day with AI")
st.markdown("### Experience the Stability-Optimality Paradox in Personal Planning")

st.write("This interactive demo showcases how different AI strategies handle unexpected chaos in your daily schedule. Witness the difference between a **Fragile AI** (Global Re-planning) and a **Resilient AI** (Inhibitory Control) when plans go awry.")


# In[3]:


# --- Simulation Setup ---

def initialize_schedule():
    return [
        {"id": 1, "name": "Morning Routine", "duration": 60, "start_time": "08:00", "type": "fixed"},
        {"id": 2, "name": "Commute to Office", "duration": 30, "start_time": "09:00", "type": "travel"},
        {"id": 3, "name": "Meeting with Client A", "duration": 90, "start_time": "09:30", "type": "meeting"},
        {"id": 4, "name": "Lunch Break", "duration": 60, "start_time": "11:00", "type": "break"},
        {"id": 5, "name": "Project Work Session", "duration": 120, "start_time": "12:00", "type": "work"},
        {"id": 6, "name": "Meeting with Client B", "duration": 60, "start_time": "14:00", "type": "meeting"},
        {"id": 7, "name": "Commute Home", "duration": 45, "start_time": "16:00", "type": "travel"},
        {"id": 8, "name": "Dinner with Friends", "duration": 90, "start_time": "18:00", "type": "social"},
    ]

def calculate_times(schedule):
    current_time_minutes = 8 * 60 # Start at 8:00 AM
    for task in schedule:
        task["actual_start_minutes"] = current_time_minutes
        task["actual_end_minutes"] = current_time_minutes + task["duration"]
        current_time_minutes = task["actual_end_minutes"]
    return schedule

def format_minutes_to_time(minutes):
    hours = (minutes // 60) % 24
    mins = minutes % 60
    return f"{int(hours):02d}:{int(mins):02d}"

def calculate_total_duration(schedule):
    """Calculate total duration of the day in minutes"""
    if not schedule:
        return 0
    return schedule[-1]["actual_end_minutes"] - schedule[0]["actual_start_minutes"]

def calculate_optimality_score(current_duration, original_duration):
    """
    Optimality Score: How close is the current schedule to the original ideal?
    100% = Same as original (Fragile AI tries to maintain this)
    < 100% = Slightly longer (Resilient AI accepts this trade-off)
    """
    if original_duration == 0:
        return 100.0
    # Optimality is the ratio of original duration to current duration
    # If current duration is longer, optimality decreases
    optimality = (original_duration / current_duration) * 100
    return min(100.0, optimality)


# In[4]:


# --- Agent Logic ---

def fragile_ai_replan(current_schedule, affected_task_index, chaos_impact_minutes, original_duration):
    # O(n^2) cost simulation - tries to maintain optimality
    cost = (len(current_schedule) - affected_task_index) ** 2 * 150 
    st.session_state.fragile_latency += cost
    
    new_schedule = [task.copy() for task in current_schedule]
    if affected_task_index < len(new_schedule):
        new_schedule[affected_task_index]["duration"] += chaos_impact_minutes
        if new_schedule[affected_task_index]["duration"] < 0:
            new_schedule.pop(affected_task_index)

    # Fragile AI "Optimizes": It tries to squeeze other tasks to keep the day short
    # For demo purposes, we simulate this by reducing subsequent task durations slightly
    for i in range(affected_task_index + 1, len(new_schedule)):
        if chaos_impact_minutes > 0:
            reduction = min(5, new_schedule[i]["duration"] - 15) # Don't reduce below 15 mins
            new_schedule[i]["duration"] -= reduction
    
    new_schedule = calculate_times(new_schedule)
    current_duration = calculate_total_duration(new_schedule)
    optimality = calculate_optimality_score(current_duration, original_duration)
    return new_schedule, cost, optimality

def resilient_ai_detour(current_schedule, affected_task_index, chaos_impact_minutes, original_duration):
    # O(n) cost simulation - local adjustment only
    cost = (1 + np.random.rand()) * 100 
    st.session_state.resilient_latency += cost

    new_schedule = [task.copy() for task in current_schedule]
    if affected_task_index < len(new_schedule):
        new_schedule[affected_task_index]["duration"] += chaos_impact_minutes
        if new_schedule[affected_task_index]["duration"] < 0:
            new_schedule.pop(affected_task_index)
    
    # Resilient AI "Satisfices": It just pushes everything forward without re-optimizing
    new_schedule = calculate_times(new_schedule)
    
    current_duration = calculate_total_duration(new_schedule)
    # Optimality is naturally lower because we didn't "squeeze" the schedule
    optimality = calculate_optimality_score(current_duration, original_duration)
    return new_schedule, cost, optimality


# In[5]:


# --- Streamlit UI State --- 

if 'fragile_schedule' not in st.session_state:
    st.session_state.fragile_schedule = calculate_times(initialize_schedule())
    st.session_state.resilient_schedule = calculate_times(initialize_schedule())
    st.session_state.original_duration = calculate_total_duration(st.session_state.fragile_schedule)
    st.session_state.fragile_latency = 0
    st.session_state.resilient_latency = 0
    st.session_state.fragile_optimality = 100.0
    st.session_state.resilient_optimality = 100.0
    st.session_state.chaos_log = []
    st.session_state.last_fragile_cost = 0
    st.session_state.last_resilient_cost = 0


# In[6]:


# --- Chaos Injection --- 

st.subheader("🚀 Inject Chaos into Your Day!")
st.write("Click a button to trigger a real-world conflict and see how the agents react.")

chaos_col1, chaos_col2, chaos_col3, chaos_col4 = st.columns(4)

chaos_event = None
impact = 0
idx = 0

with chaos_col1:
    if st.button("✈️ Flight Delayed (+120m)"):
        chaos_event, impact, idx = "Flight Delayed (+120m)", 120, 0
with chaos_col2:
    if st.button("⏰ Meeting Overruns (+30m)"):
        chaos_event, impact, idx = "Meeting Overruns (+30m)", 30, 2
with chaos_col3:
    if st.button("🚗 Traffic Jam (+45m)"):
        chaos_event, impact, idx = "Traffic Jam (+45m)", 45, 6
with chaos_col4:
    if st.button("❌ Lunch Cancelled (-60m)"):
        chaos_event, impact, idx = "Lunch Cancelled (-60m)", -60, 3

if chaos_event:
    st.session_state.chaos_log.append(chaos_event)
    
    # Run Fragile AI
    st.session_state.fragile_schedule, cost_f, opt_f = fragile_ai_replan(
        st.session_state.fragile_schedule, idx, impact, st.session_state.original_duration
    )
    st.session_state.last_fragile_cost = cost_f
    st.session_state.fragile_optimality = opt_f
    
    # Run Resilient AI
    st.session_state.resilient_schedule, cost_r, opt_r = resilient_ai_detour(
        st.session_state.resilient_schedule, idx, impact, st.session_state.original_duration
    )
    st.session_state.last_resilient_cost = cost_r
    st.session_state.resilient_optimality = opt_r

st.markdown("--- ")


# In[7]:


# --- Schedule Display --- 

st.subheader("📅 Your Resilient Day vs. The Fragile Day")

fragile_col, resilient_col = st.columns(2)

with fragile_col:
    st.markdown("#### 🤖 Fragile AI (Global Re-planning)")
    if chaos_event:
        st.markdown(f'<div class="thinking-box fragile-thinking">⚠️ Fragile AI: Recalculating entire day... (+{st.session_state.last_fragile_cost:.0f}ms)</div>', unsafe_allow_html=True)
    
    f_df = pd.DataFrame(st.session_state.fragile_schedule)
    f_df["Time"] = f_df.apply(lambda x: f"{format_minutes_to_time(x['actual_start_minutes'])} - {format_minutes_to_time(x['actual_end_minutes'])}", axis=1)
    st.table(f_df[["name", "Time", "duration"]].rename(columns={"name": "Activity", "duration": "Mins"}))

with resilient_col:
    st.markdown("#### 🧠 Resilient AI (Inhibitory Control)")
    if chaos_event:
        st.markdown(f'<div class="thinking-box resilient-adapting">✅ Resilient AI: Local detour applied instantly! (+{st.session_state.last_resilient_cost:.0f}ms)</div>', unsafe_allow_html=True)
    
    r_df = pd.DataFrame(st.session_state.resilient_schedule)
    r_df["Time"] = r_df.apply(lambda x: f"{format_minutes_to_time(x['actual_start_minutes'])} - {format_minutes_to_time(x['actual_end_minutes'])}", axis=1)
    st.table(r_df[["name", "Time", "duration"]].rename(columns={"name": "Activity", "duration": "Mins"}))

st.markdown("--- ")


# In[8]:


# --- Metrics and Explanation ---

st.subheader("📊 The Stability-Optimality Trade-off")

# Calculate System Efficiency
fragile_efficiency = (st.session_state.fragile_optimality / max(st.session_state.fragile_latency, 1)) * 100
resilient_efficiency = (st.session_state.resilient_optimality / max(st.session_state.resilient_latency, 1)) * 100

m1, m2, m3, m4, m5, m6 = st.columns(6)

with m1:
    st.metric("Fragile Optimality", f"{st.session_state.fragile_optimality:.1f}%", help="How close to the original ideal schedule")
with m2:
    st.metric("Fragile Latency", f"{st.session_state.fragile_latency:.0f} ms", delta=f"+{st.session_state.last_fragile_cost:.0f}ms", delta_color="inverse")
with m3:
    st.metric("Fragile Efficiency", f"{fragile_efficiency:.1f}", help="Optimality / Latency ratio")

with m4:
    st.metric("Resilient Optimality", f"{st.session_state.resilient_optimality:.1f}%", help="How close to the original ideal schedule")
with m5:
    st.metric("Resilient Latency", f"{st.session_state.resilient_latency:.0f} ms", delta=f"+{st.session_state.last_resilient_cost:.0f}ms", delta_color="normal")
with m6:
    st.metric("Resilient Efficiency", f"{resilient_efficiency:.1f}", help="Optimality / Latency ratio")


# In[9]:


# --- Trade-off Visualization ---

st.subheader("📈 The Paradox Visualized: Optimality vs. Latency")

fig, ax = plt.subplots(figsize=(10, 6))

# Create a scatter plot showing the trade-off
fragile_point = [st.session_state.fragile_latency, st.session_state.fragile_optimality]
resilient_point = [st.session_state.resilient_latency, st.session_state.resilient_optimality]

ax.scatter([fragile_point[0]], [fragile_point[1]], s=500, color='#0077B6', marker='o', label='Fragile AI', zorder=3)
ax.scatter([resilient_point[0]], [resilient_point[1]], s=500, color='#E67E22', marker='s', label='Resilient AI', zorder=3)

# Draw an arrow between them
ax.annotate('', xy=(resilient_point[0], resilient_point[1]), xytext=(fragile_point[0], fragile_point[1]),
            arrowprops=dict(arrowstyle='<->', color='gray', lw=2, linestyle='--'))

ax.set_xlabel("Latency (ms)", fontsize=12, fontweight='bold')
ax.set_ylabel("Optimality (%)", fontsize=12, fontweight='bold')
ax.set_title("The Stability-Optimality Paradox: The Trade-off", fontsize=14, fontweight='bold')
ax.legend(fontsize=11, loc='upper left')
ax.grid(True, linestyle='--', alpha=0.5)
ax.set_ylim([min(70, st.session_state.resilient_optimality - 5), 105])

st.pyplot(fig)

st.markdown("""
### 🧠 The Stability-Optimality Paradox Explained:

**The Core Insight:** In dynamic, stochastic environments, **pursuing mathematical optimality leads to catastrophic fragility.**

**Fragile AI (Global Re-planning):** 
- Tries to find the *perfect* schedule every time chaos strikes.
- Achieves very high **Optimality** by re-optimizing all subsequent tasks.
- But suffers from **extreme Latency** due to $O(n^2)$ re-calculation cost.
- **System Efficiency is LOW**

**Resilient AI (Inhibitory Control):**
- Accepts a slightly "sub-optimal" path to maintain stability.
- Achieves slightly lower **Optimality** because it doesn't re-optimize the entire day.
- But maintains **low, predictable Latency** through $O(n)$ local adjustments.
- **System Efficiency is HIGH** because the user gets instant decisions with minimal sacrifice.

**The Paradox:** The "perfect" system is fragile. The "good enough" system is robust.

In real-world applications (like Perplexity's Answer Engine or autonomous vehicles), **Resilience often trumps Optimality.**
""")

st.markdown("--- ")
st.subheader("📜 Chaos History")
if st.session_state.chaos_log:
    for event in reversed(st.session_state.chaos_log):
        st.write(f"- {event}")
else:
    st.write("No chaos yet. Click a button above to start!")

if st.button("🔄 Reset Schedule"):
    st.session_state.fragile_schedule = calculate_times(initialize_schedule())
    st.session_state.resilient_schedule = calculate_times(initialize_schedule())
    st.session_state.original_duration = calculate_total_duration(st.session_state.fragile_schedule)
    st.session_state.fragile_latency = 0
    st.session_state.resilient_latency = 0
    st.session_state.fragile_optimality = 100.0
    st.session_state.resilient_optimality = 100.0
    st.session_state.chaos_log = []
    st.session_state.last_fragile_cost = 0
    st.session_state.last_resilient_cost = 0
    st.rerun()

st.markdown("---")
st.markdown("""
### 📚 Research Status
**Status:** Research Hypothesis & Proof of Concept. This framework is based on stochastic simulations comparing $O(n^2)$ global re-planning against $O(n)$ local inhibitory control in dynamic environments. Currently being formalized for peer review.

**Author:** Zainab Huda | **Research Focus:** Stability-Optimality Paradox in Agentic AI
""")


# In[ ]:




