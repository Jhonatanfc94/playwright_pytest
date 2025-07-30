from locust import HttpUser, task, between, LoadTestShape

class CayalaVisitor(HttpUser):
    wait_time = between(2, 5)
    host = "https://example.com"

    def on_start(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "es-GT,es;q=0.9",
        }

    @task(10)
    def visit_homepage(self):
        with self.client.get("/", headers=self.headers, catch_response=True) as response:
            if "text expected" not in response.text:
                response.failure("The title isn't displayed correctly")
            if response.status_code != 200:
                    response.failure(f"page not available")
            if response.elapsed.total_seconds() > 2.5:
                response.failure("Time response is > 2.5s")

    @task(8)
    def explore_sections(self):
        sections = [
            "/home"
        ]
        for section in sections:
            with self.client.get(section, headers=self.headers, name="/[sección]", catch_response=True) as response:
                if "text expected" not in response.text:
                    response.failure("The title isn't displayed correctly")
                if response.status_code != 200:
                    response.failure(f"Sección {section} no disponible")
                if response.elapsed.total_seconds() > 2.5:
                    response.failure("Time response is > 2.5s")

class DailyTrafficShape(LoadTestShape):
    stages = [
        {"duration": 180, "users": 15, "spawn_rate": 1},
        {"duration": 900, "users": 15, "spawn_rate": 5},
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
            run_time -= stage["duration"]

        return None