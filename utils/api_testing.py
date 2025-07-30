from playwright.sync_api import Playwright

class APIUtils:
    def __init__(self, base_url="https://algo/api"):
        self.base_url = base_url
    
    def getToken(self, playwright:Playwright, email=None, password=None):
        api_request_context = playwright.request.new_context(base_url="https://algo/api/")
        payload = {
            "email": email if email else "emailexample@gmail.com",
            "password": password if password else "passwordExample"
        }
    
        response = api_request_context.post("api/auth/login",
                                            data=payload)
        
        assert response.ok, f"Login failed with status {response.status_code}: {response.text}"
        response_body = response.json()
        return response_body["data"]