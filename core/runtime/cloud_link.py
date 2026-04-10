import requests

class CloudLink:
    def __init__(self):
        self.url = "https://example-cloud-endpoint.com"
        self.online = False

    def connect(self):
        try:
            requests.get(self.url, timeout=2)
            self.online = True
        except:
            self.online = False
        return self.online

    def status(self):
        return {"cloud_online": self.online, "endpoint": self.url}
