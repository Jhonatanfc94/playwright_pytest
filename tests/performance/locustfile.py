from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def visit_homepage(self):
        try:
            response = self.client.get("/", timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"❌ Error accediendo al home: {e}")