from locust import HttpUser, task, between
import os

API_KEY = os.getenv("SZ_API_KEY")
DEFAULT_HOST = os.getenv("LOCUST_HOST", os.getenv("HOST", "http://localhost:8000"))


class SystemZeroUser(HttpUser):
    wait_time = between(0.1, 0.5)
    host = DEFAULT_HOST

    def _headers(self):
        headers = {"Accept": "application/json"}
        if API_KEY:
            headers["X-API-Key"] = API_KEY
        return headers

    @task(3)
    def status(self):
        self.client.get("/status", headers=self._headers())

    @task(3)
    def health(self):
        self.client.get("/health", headers=self._headers())

    @task(2)
    def templates(self):
        self.client.get("/templates", headers=self._headers())

    @task(1)
    def dashboard(self):
        self.client.get("/dashboard", headers=self._headers())
