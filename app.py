import streamlit as st
import plotly.graph_objects as go
import time
from ticket_counter_simulator import TicketCounterSim

st.set_page_config(page_title="🎟️ Ticket Counter Simulator", layout="wide")

# ------------------ App State ------------------
if "sim" not in st.session_state:
    st.session_state.sim = TicketCounterSim(num_servers=2, arrival_rate=1.0, num_customers=50, service_time=5.0)
if "running" not in st.session_state:
    st.session_state.running = False
if "speed" not in st.session_state:
    st.session_state.speed = 0.5  # seconds per step

# ------------------ Sidebar Controls ------------------
st.sidebar.header("⚙️ Simulation Controls")

# --- User-adjustable parameters ---
num_servers = st.sidebar.number_input("Number of Servers", min_value=1, max_value=10, value=2, step=1)
arrival_rate = st.sidebar.number_input(
    "Customer Arrival Rate (customers per time unit)", 
    min_value=0.1, max_value=10.0, value=1.0, step=0.1
)
num_customers = st.sidebar.number_input("Total Number of Customers", min_value=5, max_value=500, value=50, step=5)
service_time = st.sidebar.number_input(
    "Average Service Time (time units per customer)",
    min_value=0.1, max_value=20.0, value=5.0, step=0.5
)

# --- Simulation buttons ---
colA, colB, colC = st.sidebar.columns(3)
with colA:
    if st.button("▶️ Play"):
        st.session_state.running = True
with colB:
    if st.button("⏸️ Pause"):
        st.session_state.running = False
with colC:
    if st.button("🔄 Reset"):
        st.session_state.sim = TicketCounterSim(
            num_servers=int(num_servers),
            arrival_rate=float(arrival_rate),
            num_customers=int(num_customers),
            service_time=float(service_time)  # <-- NEW
        )
        st.session_state.running = False

# --- Speed control ---
st.sidebar.slider("Speed (Slide RIGHT for SLOWER simulation)", 2.0, 0.01, key="speed")

# ------------------ Main Display ------------------
st.title("🎟️ Ticket Counter Simulation")
sim = st.session_state.sim

# Compute current stats
avg_wait = sim.metrics["total_wait_time"] / max(sim.metrics["num_served"], 1)
current_util = sim.utilization_history[-1] if sim.utilization_history else 0

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Current Time", f"{sim.current_time:.2f}")
    st.metric("Queue Length", len(sim.waiting_line))

with col2:
    st.metric("Customers Served", sim.metrics["num_served"])
    st.metric("Average Wait", f"{avg_wait:.2f}")

with col3:
    st.metric("Avg Server Utilization", f"{current_util*100:.1f}%")


fig = go.Figure()

# Queue Length
fig.add_trace(go.Scatter(
    x=sim.time_history, y=sim.queue_length_history,
    mode="lines", name="Queue Length", line=dict(color="royalblue")
))

# Instantaneous Utilization
fig.add_trace(go.Scatter(
    x=sim.time_history, y=sim.utilization_history,
    mode="lines", name="Instantaneous Utilization", line=dict(color="green", dash="dot")
))

# Cumulative Utilization (if available)
if hasattr(sim, "cumulative_utilization_history"):
    fig.add_trace(go.Scatter(
        x=sim.time_history, y=sim.cumulative_utilization_history,
        mode="lines", name="Cumulative Utilization", line=dict(color="firebrick")
    ))

fig.update_layout(
    title="System Metrics Over Time",
    xaxis_title="Time",
    yaxis_title="Value",
    template="plotly_white",
    legend=dict(x=0, y=1.1, orientation="h")
)

st.plotly_chart(fig, use_container_width=True)

# ------------------ Verification Section ------------------
if st.sidebar.checkbox("Show Calculation Verification", value=False):
    st.subheader("🔍 Calculation Verification")
    
    if sim.metrics["num_served"] > 0:
        verification_results = sim.verify_calculations()
        for result in verification_results:
            if "✓" in result:
                st.success(result)
            elif "✗" in result:
                st.error(result)
            else:
                st.info(result)
        
        # Also show Little's Law verification if you implement it
        if hasattr(sim, 'verify_conservation_laws'):
            st.subheader("📐 Conservation Laws")
            conservation_results = sim.verify_conservation_laws()
            for result in conservation_results:
                st.code(result)
    else:
        st.warning("Run the simulation first to verify calculations")


# ------------------ Simulation Loop ------------------
if st.session_state.running:
    step_success = sim.step()
    if not step_success:
        st.session_state.running = False
    time.sleep(st.session_state.speed)
    st.rerun()
