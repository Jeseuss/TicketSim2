# ticket_counter_simulator.py
import random
from collections import deque  # For efficient queue operations
from HeapPriorityQueue import HeapPriorityQueue  # Custom priority queue for event scheduling


# ------------------ Event Class ------------------
# Represents a discrete event in the simulation
class Event:
    def __init__(self, time, event_type, customer_id):
        self.time = time  # When the event occurs
        self.event_type = event_type  # Type: ARRIVAL, SERVICE_START, SERVICE_END
        self.customer_id = customer_id  # Which customer this event relates to

    def __repr__(self):
        # String representation for debugging
        return f"Event(time={self.time:.2f}, type={self.event_type}, id={self.customer_id})"


# ------------------ Main Simulation Class ------------------
class TicketCounterSim:
    def __init__(self, num_servers=2, arrival_rate=1/3, num_customers=30, service_time=5.0):
        # ------------------ Simulation Parameters ------------------
        self.num_servers = num_servers  # Number of ticket counter agents
        self.arrival_rate = arrival_rate  # Average arrivals per time unit (Poisson rate)
        self.num_customers = num_customers  # Total customers to simulate
        self.service_time = service_time  # Average time to serve one customer
        
        # ------------------ Simulation State ------------------
        # Future Events List (FEL) - stores upcoming events in chronological order
        self.future_events = HeapPriorityQueue()
        
        # Queue of customers waiting for service (FIFO)
        self.waiting_line = deque()
        
        # Server status: None = idle, customer_id = serving that customer
        self.servers = [None] * num_servers
        
        # Customer records: stores arrival and service start times for each customer
        self.customers = {}
        
        # ------------------ Performance Metrics ------------------
        self.metrics = {
            "total_wait_time": 0,  # Sum of all wait times
            "num_served": 0,  # Number of customers completed
            "server_busy_time": [0] * num_servers,  # Total busy time per server
            "simulation_end": 0  # Time when last customer finishes
        }
        
        # ------------------ Time-Series Data for Visualization ------------------
        self.current_time = 0  # Simulation clock
        self.queue_length_history = []  # Queue length at each event
        self.utilization_history = []  # Instantaneous utilization at each event
        self.time_history = []  # Time points for plotting
        
        # ------------------ Initialize Simulation ------------------
        self._schedule_initial_arrivals()  # Create initial arrival events

    # ------------------ Initialization Methods ------------------
    def _schedule_initial_arrivals(self):
        """Schedule arrival events for all customers using exponential interarrival times"""
        current_time = 0
        for i in range(self.num_customers):
            # Exponential distribution for interarrival times (Poisson process)
            interarrival = random.expovariate(self.arrival_rate)
            current_time += interarrival
            # Schedule arrival event in the future events list
            self.future_events.add(current_time, Event(current_time, "ARRIVAL", i))

    # ------------------ Simulation Stepping ------------------
    def step(self):
        """Process one event; return False if no events left"""
        # Check if simulation is complete (no more events)
        if self.future_events.is_empty():
            return False

        # Get the next event (smallest time first)
        time, event = self.future_events.remove_min()
        if event is None:  # Safety check for empty queue
            return False
            
        # Advance simulation clock to event time
        self.current_time = time

        # Process event based on type (discrete event simulation)
        if event.event_type == "ARRIVAL":
            self._arrival(event)
        elif event.event_type == "SERVICE_START":
            self._service_start(event)
        elif event.event_type == "SERVICE_END":
            self._service_end(event)

        # ------------------ Record Metrics After Event ------------------

        #  Instantaneous utilization: fraction of servers currently busy
        instant_busy = sum(1 for s in self.servers if s is not None)
        instant_util = instant_busy / self.num_servers

        #  Cumulative utilization: total busy time / total possible server time
        total_busy_time = sum(self.metrics["server_busy_time"])
        total_possible_time = self.num_servers * max(self.current_time, 1)  # Avoid division by zero
        cumulative_util = total_busy_time / total_possible_time if total_possible_time > 0 else 0

        #  Record values for time-series visualization
        self.time_history.append(self.current_time)
        self.queue_length_history.append(len(self.waiting_line))
        self.utilization_history.append(instant_util)
        
        # Initialize cumulative utilization history if needed
        if not hasattr(self, "cumulative_utilization_history"):
            self.cumulative_utilization_history = []
        self.cumulative_utilization_history.append(cumulative_util)
        
        return True  # Simulation continues

    # ------------------ Event Handlers ------------------
    def _arrival(self, event):
        """Handle customer arrival event"""
        # Record customer arrival time
        self.customers[event.customer_id] = {"arrival": self.current_time}

        # Try to assign customer to an idle server immediately
        for i, s in enumerate(self.servers):
            if s is None:  # Server is idle
                self.servers[i] = event.customer_id  # Assign customer to server
                # Schedule service start immediately
                self.future_events.add(
                    self.current_time, 
                    Event(self.current_time, "SERVICE_START", event.customer_id)
                )
                return  # Customer served immediately, no waiting

        # If all servers are busy, customer joins the waiting line (queue)
        self.waiting_line.append(event.customer_id)

    def _service_start(self, event):
        """Handle start of service event"""
        # Record when service actually begins (may be later than arrival if waiting)
        self.customers[event.customer_id]["service_start"] = self.current_time
        
        # Calculate wait time: time from arrival to service start
        wait = self.current_time - self.customers[event.customer_id]["arrival"]
        self.metrics["total_wait_time"] += wait

        # Use user-defined average service time
        # Option 1: Fixed service time (deterministic)
        service_duration = self.service_time
        
        # Option 2: Random service time (exponential distribution, commented out)
        # service_duration = random.expovariate(1 / self.service_time)

        # Schedule service end event
        end_time = self.current_time + service_duration
        self.future_events.add(
            end_time, 
            Event(end_time, "SERVICE_END", event.customer_id)
        )

    def _service_end(self, event):
        """Handle service completion event"""
        # Update metrics
        self.metrics["num_served"] += 1
        self.metrics["simulation_end"] = self.current_time

        # Find which server served this customer
        for i, s in enumerate(self.servers):
            if s == event.customer_id:
                # Free up the server
                self.servers[i] = None
                
                # Calculate and record server busy time
                service_time = self.current_time - self.customers[event.customer_id]["service_start"]
                self.metrics["server_busy_time"][i] += service_time
                
                # If customers are waiting, serve the next one immediately
                if self.waiting_line:
                    next_cust = self.waiting_line.popleft()  # FIFO: first come, first served
                    self.servers[i] = next_cust  # Assign to newly freed server
                    # Schedule service start for waiting customer
                    self.future_events.add(
                        self.current_time, 
                        Event(self.current_time, "SERVICE_START", next_cust)
                    )
                break  # Found the server, exit loop

    # ------------------ Sanity Check / Verification ------------------
    def verify_calculations(self):
        """Verify key calculations and return results for display"""
        results = []
        
        # Check 1: Utilization bounds (must be between 0 and 1)
        final_util = self.utilization_history[-1] if self.utilization_history else 0
        final_cumulative_util = self.cumulative_utilization_history[-1] if hasattr(self, 'cumulative_utilization_history') else 0
        
        results.append(f"Final Instant Utilization: {final_util:.3f} {'✓' if 0 <= final_util <= 1 else '✗ OUT OF RANGE'}")
        results.append(f"Final Cumulative Utilization: {final_cumulative_util:.3f} {'✓' if 0 <= final_cumulative_util <= 1 else '✗ OUT OF RANGE'}")
        
        # Check 2: Queue length consistency (should never be negative)
        max_queue = max(self.queue_length_history) if self.queue_length_history else 0
        results.append(f"Maximum Queue Length: {max_queue} {'✓' if max_queue >= 0 else '✗ NEGATIVE QUEUE'}")
        
        # Check 3: Time monotonicity (simulation time should always increase)
        time_increasing = all(self.time_history[i] <= self.time_history[i+1] 
                            for i in range(len(self.time_history)-1))
        results.append(f"Time Monotonically Increasing: {'✓' if time_increasing else '✗ TIME DECREASED'}")
        
        # Check 4: Server busy time consistency (each server's utilization should be 0-1)
        total_sim_time = self.metrics["simulation_end"]
        for i, busy_time in enumerate(self.metrics["server_busy_time"]):
            utilization = busy_time / total_sim_time if total_sim_time > 0 else 0
            status = "✓" if 0 <= utilization <= 1 else "✗"
            results.append(f"Server {i} utilization: {utilization:.3f} {status}")
        
        return results
    
    # ------------------ Basic Test Function ------------------
    def test_simulation(self):
        """Run basic tests to ensure functionality"""
        test_cases = [
            (1, 0.1, 10, 1.0),  # Light load: few arrivals, fast service
            (2, 1.0, 50, 5.0),  # Normal load: balanced arrival/service rates
            (1, 2.0, 100, 1.0), # Heavy load: arrivals faster than service
        ]
        
        for servers, arrival, customers, service in test_cases:
            # Create and run simulation to completion
            sim = TicketCounterSim(servers, arrival, customers, service)
            while sim.step():
                pass  # Run until no more events
            
            # Verify all customers were processed
            assert sim.metrics["num_served"] == customers
            print(f"✓ Test passed: {servers} servers, {customers} customers")

# ------------------ Test Runner ------------------
print("Running basic simulation tests...")
TicketCounterSim().test_simulation()

print("All tests completed.")
