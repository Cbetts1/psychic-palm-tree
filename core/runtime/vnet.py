import socket

class VNet:
    def __init__(self):
        self.routes = []

    def add_route(self, name, target):
        self.routes.append({"name": name, "target": target})

    def list_routes(self):
        return self.routes

    def ping_cloud(self, host="8.8.8.8"):
        try:
            socket.gethostbyname(host)
            return True
        except:
            return False
