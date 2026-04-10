import os

class HybridVFS:
    def __init__(self):
        self.mounts = {
            "cloud": "/aura/cloud",
            "cache": "/aura/local/cache"
        }
        self.subdirs = [
            "/aura/cloud/images",
            "/aura/cloud/videos",
            "/aura/cloud/apk",
            "/aura/cloud/docs"
        ]

    def ensure_paths(self):
        for path in self.mounts.values():
            os.makedirs(path, exist_ok=True)
        for path in self.subdirs:
            os.makedirs(path, exist_ok=True)

    def list_mounts(self):
        return self.mounts
