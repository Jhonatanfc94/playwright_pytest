import random
import logging
from locust import HttpUser, SequentialTaskSet, task, between, LoadTestShape

logging.basicConfig(level=logging.INFO)

class UserBehavior(SequentialTaskSet):
    """
    Automated user lifecycle.
    Define your task sequence here.
    """
    def on_start(self):
        """Initialization for each virtual user."""
        self.user_id = random.randint(1000, 9999)
        logging.info(f"Starting session for user {self.user_id}")

    @task
    def phase_1_explore(self):
        """Example: GET request to a public listing."""
        with self.client.get("/", catch_response=True, name="1. GET /") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status: {response.status_code}")

    @task
    def phase_2_action(self):
        """Example: POST request to an action endpoint."""
        # Replace with actual endpoint and payload
        payload = {"data": "test_value"}
        with self.client.post("/api/action", 
                             json=payload, 
                             catch_response=True, 
                             name="2. POST /api/action") as response:
            # Logic to validate success
            response.success()

    @task
    def finish_lifecycle(self):
        """Stops the task execution for this user."""
        self.interrupt()

class ApiLoadTester(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 4) 

# ==========================================
# 🚦 AUTOMATED TRAFFIC CONTROLLER (STAGES)
# ==========================================
class AutomatedTrafficShape(LoadTestShape):
    """
    Simulates a realistic traffic pattern with stages.
    """
    stages = [
        {"duration": 10, "users": 5, "spawn_rate": 2},    # Stage 1: Warmup
        {"duration": 20, "users": 15, "spawn_rate": 5},   # Stage 2: Peak
        {"duration": 30, "users": 2, "spawn_rate": 2},    # Stage 3: Cooldown
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data

        return None # Stop test automatically when stages end