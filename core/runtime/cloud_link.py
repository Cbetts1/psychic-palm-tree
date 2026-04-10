import requests

_ENDPOINTS = [
    "https://example-cloud-endpoint.com",
    "https://backup-cloud-endpoint.com",
]

class CloudLink:
    def __init__(self):
        self.endpoints = list(_ENDPOINTS)
        self.active_endpoint = self.endpoints[0]
        self.state = "offline"  # online / offline / degraded

    def connect(self):
        for endpoint in self.endpoints:
            try:
                requests.get(endpoint, timeout=2)
                self.active_endpoint = endpoint
                self.state = "online" if endpoint == self.endpoints[0] else "degraded"
                return self.state
            except requests.RequestException:
                continue
        self.state = "offline"
        return self.state

    def status(self):
        return {
            "state": self.state,
            "endpoint": self.active_endpoint,
        }
