# ticket_counter_simulator.py
import random
from collections import deque
from HeapPriorityQueue import HeapPriorityQueue


class Event:
    def __init__(self, time, event_type, customer_id):
        self.time = time
        self.event_type = event_type
        self.customer_id = customer_id

    def __repr__(self):
        return f"Event(time={self.time:.2f}, type={self.event_type}, id={self.customer_id})"


class TicketCounterSim:
    def __init__(self, num_servers=2, arrival_rate=1/3, num_customers=30, service_time=5.0):
        self.num_servers = num_servers
        self.arrival_rate = arrival_rate
        self.num_customers = num_customers
        self.service_time = service_time 
        self.future_events = HeapPriorityQueue()
        self.waiting_line = deque()
        self.servers = [None] * num_servers
        self.customers = {}
        self.metrics = {"total_wait_time": 0, "num_served": 0,
                        "server_busy_time": [0]*num_servers, "simulation_end": 0}
        self.current_time = 0
        self.queue_length_history = []
        self.utilization_history = []
        self.time_history = []

        self._schedule_initial_arrivals()

    # ----------------- Initialization -----------------
    def _schedule_initial_arrivals(self):
        current_time = 0
        for i in range(self.num_customers):
            interarrival = random.expovariate(self.arrival_rate)
            current_time += interarrival
            self.future_events.add(current_time, Event(current_time, "ARRIVAL", i))

    # ----------------- Step Simulation -----------------
    def step(self):
        """Process one event; return False if no events left"""
        if self.future_events.is_empty():
            return False

        time, event = self.future_events.remove_min()
        if event is None:  # Add this safety check
            return False
        self.current_time = time

        if event.event_type == "ARRIVAL":
            self._arrival(event)
        elif event.event_type == "SERVICE_START":
            self._service_start(event)
        elif event.event_type == "SERVICE_END":
            self._service_end(event)

        # -------------------- Record Metrics --------------------

        # 1️⃣ Instantaneous utilization (how many servers are currently busy)
        instant_busy = sum(1 for s in self.servers if s is not None)
        instant_util = instant_busy / self.num_servers

        # 2️⃣ Cumulative utilization (total busy time / total possible server time)
        total_busy_time = sum(self.metrics["server_busy_time"])
        total_possible_time = self.num_servers * max(self.current_time, 1)
        cumulative_util = total_busy_time / total_possible_time if total_possible_time > 0 else 0

        # 3️⃣ Record values
        self.time_history.append(self.current_time)
        self.queue_length_history.append(len(self.waiting_line))
        self.utilization_history.append(instant_util)
        # NEW:
        if not hasattr(self, "cumulative_utilization_history"):
            self.cumulative_utilization_history = []
        self.cumulative_utilization_history.append(cumulative_util)
        return True

    # ----------------- Event Handlers -----------------
    def _arrival(self, event):
        self.customers[event.customer_id] = {"arrival": self.current_time}

        for i, s in enumerate(self.servers):
            if s is None:
                self.servers[i] = event.customer_id
                self.future_events.add(self.current_time, Event(self.current_time, "SERVICE_START", event.customer_id))
                return

        self.waiting_line.append(event.customer_id)

    def _service_start(self, event):
        self.customers[event.customer_id]["service_start"] = self.current_time
        wait = self.current_time - self.customers[event.customer_id]["arrival"]
        self.metrics["total_wait_time"] += wait

        # ✅ Use user-defined average service time
        # If you want variability, use exponential randomization
        #service_duration = random.expovariate(1 / self.service_time)
        # If you prefer fixed service time instead, comment above and use:
        service_duration = self.service_time

        end_time = self.current_time + service_duration
        self.future_events.add(end_time, Event(end_time, "SERVICE_END", event.customer_id))


    def _service_end(self, event):
        self.metrics["num_served"] += 1
        self.metrics["simulation_end"] = self.current_time

        for i, s in enumerate(self.servers):
            if s == event.customer_id:
                self.servers[i] = None
                service_time = self.current_time - self.customers[event.customer_id]["service_start"]
                self.metrics["server_busy_time"][i] += service_time
                if self.waiting_line:
                    next_cust = self.waiting_line.popleft()
                    self.servers[i] = next_cust
                    self.future_events.add(self.current_time, Event(self.current_time, "SERVICE_START", next_cust))
                break

# ----------------- End of ticket_counter_simulator.py -----------------
#Sanity check of math
    def verify_calculations(self):
        """Verify key calculations and return results for display"""
        results = []
        
        # Check 1: Utilization bounds
        final_util = self.utilization_history[-1] if self.utilization_history else 0
        final_cumulative_util = self.cumulative_utilization_history[-1] if hasattr(self, 'cumulative_utilization_history') else 0
        
        results.append(f"Final Instant Utilization: {final_util:.3f} {'✓' if 0 <= final_util <= 1 else '✗ OUT OF RANGE'}")
        results.append(f"Final Cumulative Utilization: {final_cumulative_util:.3f} {'✓' if 0 <= final_cumulative_util <= 1 else '✗ OUT OF RANGE'}")
        
        # Check 2: Queue length consistency
        max_queue = max(self.queue_length_history) if self.queue_length_history else 0
        results.append(f"Maximum Queue Length: {max_queue} {'✓' if max_queue >= 0 else '✗ NEGATIVE QUEUE'}")
        
        # Check 3: Time monotonicity
        time_increasing = all(self.time_history[i] <= self.time_history[i+1] 
                            for i in range(len(self.time_history)-1))
        results.append(f"Time Monotonically Increasing: {'✓' if time_increasing else '✗ TIME DECREASED'}")
        
        # Check 4: Server busy time consistency
        total_sim_time = self.metrics["simulation_end"]
        for i, busy_time in enumerate(self.metrics["server_busy_time"]):
            utilization = busy_time / total_sim_time if total_sim_time > 0 else 0
            status = "✓" if 0 <= utilization <= 1 else "✗"
            results.append(f"Server {i} utilization: {utilization:.3f} {status}")
        
        return results
    
    #BASIC TEST
    def test_simulation(self):
        """Run basic tests to ensure functionality"""
        test_cases = [
            (1, 0.1, 10, 1.0),  # Light load
            (2, 1.0, 50, 5.0),  # Normal load  
            (1, 2.0, 100, 1.0), # Heavy load
        ]
        
        for servers, arrival, customers, service in test_cases:
            sim = TicketCounterSim(servers, arrival, customers, service)
            while sim.step():
                pass
            # Verify all customers were processed
            assert sim.metrics["num_served"] == customers
            print(f"✓ Test passed: {servers} servers, {customers} customers")

print("Running basic simulation tests...")
TicketCounterSim().test_simulation()
print("All tests completed.")


