# Import necessary libraries
import streamlit as st  # Web application framework for creating interactive dashboards
import plotly.graph_objects as go  # Library for creating interactive visualizations
import time  # For controlling simulation speed with time delays
from ticket_counter_simulator import TicketCounterSim  # Custom simulation logic module

# Configure the Streamlit page with title and layout
st.set_page_config(page_title="🎟️ Ticket Counter Simulator", layout="wide")

# ------------------ App State Initialization ------------------
# Store simulation state in Streamlit's session_state to persist across reruns
if "sim" not in st.session_state:
    # Create a new simulation instance with default parameters
    st.session_state.sim = TicketCounterSim(num_servers=2, arrival_rate=1.0, num_customers=50, service_time=5.0)
    
if "running" not in st.session_state:
    # Track whether the simulation is currently running
    st.session_state.running = False
    
if "speed" not in st.session_state:
    # Control simulation speed: lower values = faster, higher = slower
    st.session_state.speed = 0.5  # seconds per step (default: 0.5 seconds between steps)

# ------------------ Sidebar Controls ------------------
# Create a sidebar for user inputs and controls
st.sidebar.header("⚙️ Simulation Controls")

# --- User-adjustable simulation parameters ---
# These allow users to customize the simulation before or during runtime

# Number of ticket counter servers/agents
num_servers = st.sidebar.number_input("Number of Servers", min_value=1, max_value=10, value=2, step=1)

# Rate at which new customers arrive (Poisson process parameter)
arrival_rate = st.sidebar.number_input(
    "Customer Arrival Rate (customers per time unit)", 
    min_value=0.1, max_value=10.0, value=1.0, step=0.1
)

# Total number of customers to simulate
num_customers = st.sidebar.number_input("Total Number of Customers", min_value=5, max_value=500, value=50, step=5)

# Average time it takes to serve one customer
service_time = st.sidebar.number_input(
    "Average Service Time (time units per customer)",
    min_value=0.1, max_value=20.0, value=5.0, step=0.5
)

# --- Simulation control buttons ---
# Create three columns for side-by-side buttons
colA, colB, colC = st.sidebar.columns(3)

with colA:
    # Start the simulation
    if st.button("▶️ Play"):
        st.session_state.running = True
        
with colB:
    # Pause the simulation
    if st.button("⏸️ Pause"):
        st.session_state.running = False
        
with colC:
    # Reset the simulation with current parameters
    if st.button("🔄 Reset"):
        # Create a fresh simulation instance with user's current settings
        st.session_state.sim = TicketCounterSim(
            num_servers=int(num_servers),
            arrival_rate=float(arrival_rate),
            num_customers=int(num_customers),
            service_time=float(service_time)  # <-- NEW parameter
        )
        st.session_state.running = False  # Ensure reset state is paused

# --- Simulation speed control ---
# Slider for adjusting simulation playback speed
# Note: Higher values mean SLOWER simulation (more delay between steps)
st.sidebar.slider("Speed (Slide RIGHT for SLOWER simulation)", 2.0, 0.01, key="speed")

# ------------------ Main Display Area ------------------
# Primary content area showing metrics and visualizations
st.title("🎟️ Ticket Counter Simulation")

# Get reference to the current simulation instance
sim = st.session_state.sim

# Compute real-time statistics from the simulation

# Calculate average wait time (total wait time divided by number served)
avg_wait = sim.metrics["total_wait_time"] / max(sim.metrics["num_served"], 1)  # Avoid division by zero

# Get the most recent server utilization value (percentage of servers busy)
current_util = sim.utilization_history[-1] if sim.utilization_history else 0

# Display metrics in a three-column layout
col1, col2, col3 = st.columns(3)

with col1:
    # Show current simulation time
    st.metric("Current Time", f"{sim.current_time:.2f}")
    # Show current number of customers waiting in line
    st.metric("Queue Length", len(sim.waiting_line))

with col2:
    # Show how many customers have been served so far
    st.metric("Customers Served", sim.metrics["num_served"])
    # Show average wait time for served customers
    st.metric("Average Wait", f"{avg_wait:.2f}")

with col3:
    # Show current server utilization percentage
    st.metric("Avg Server Utilization", f"{current_util*100:.1f}%")

# ------------------ Time-Series Visualization ------------------
# Create a Plotly figure to show how metrics evolve over time
fig = go.Figure()

# Add queue length trace (blue line)
fig.add_trace(go.Scatter(
    x=sim.time_history,  # X-axis: simulation time points
    y=sim.queue_length_history,  # Y-axis: queue length at each time point
    mode="lines", 
    name="Queue Length", 
    line=dict(color="royalblue")
))

# Add instantaneous utilization trace (green dotted line)
fig.add_trace(go.Scatter(
    x=sim.time_history,  # X-axis: simulation time points
    y=sim.utilization_history,  # Y-axis: utilization at each time point
    mode="lines", 
    name="Instantaneous Utilization", 
    line=dict(color="green", dash="dot")
))

# Add cumulative utilization trace if available (red line)
if hasattr(sim, "cumulative_utilization_history"):
    fig.add_trace(go.Scatter(
        x=sim.time_history,  # X-axis: simulation time points
        y=sim.cumulative_utilization_history,  # Y-axis: cumulative average utilization
        mode="lines", 
        name="Cumulative Utilization", 
        line=dict(color="firebrick")
    ))

# Configure the chart layout
fig.update_layout(
    title="System Metrics Over Time",
    xaxis_title="Time",
    yaxis_title="Value",
    template="plotly_white",  # Clean, white background theme
    legend=dict(x=0, y=1.1, orientation="h")  # Horizontal legend at top
)

# Display the chart in the main area
st.plotly_chart(fig, use_container_width=True)

# ------------------ Verification Section ------------------
# Optional advanced section for validating simulation calculations
if st.sidebar.checkbox("Show Calculation Verification", value=False):
    st.subheader("🔍 Calculation Verification")
    
    # Only show verification if some customers have been served
    if sim.metrics["num_served"] > 0:
        # Get verification results from the simulation
        verification_results = sim.verify_calculations()
        
        # Display each result with appropriate styling
        for result in verification_results:
            if "✓" in result:  # Success/Correct
                st.success(result)
            elif "✗" in result:  # Error/Incorrect
                st.error(result)
            else:  # Informational
                st.info(result)
        
        # Show conservation laws verification if available (e.g., Little's Law)
        if hasattr(sim, 'verify_conservation_laws'):
            st.subheader("📐 Conservation Laws")
            conservation_results = sim.verify_conservation_laws()
            for result in conservation_results:
                st.code(result)  # Display as code block for readability
    else:
        st.warning("Run the simulation first to verify calculations")

# ------------------ Simulation Loop ------------------
# This section handles the automatic advancement of the simulation
if st.session_state.running:
    # Advance the simulation by one time step
    step_success = sim.step()  # Returns False when simulation is complete
    
    # Stop simulation if step() indicates completion
    if not step_success:
        st.session_state.running = False
    
    # Control simulation speed by pausing execution
    time.sleep(st.session_state.speed)
    
    # Rerun the entire app to update displays with new simulation state
    st.rerun()
