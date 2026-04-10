import os


class HybridVFS:
    def __init__(self):
        self.mounts = {
            "cloud":     "/aura/cloud",
            "cache":     "/aura/local/cache",
            "packages":  "/aura/local/packages",
        }
        self._subdirs = [
            # cloud output buckets
            "/aura/cloud/images",
            "/aura/cloud/videos",
            "/aura/cloud/apk",
            "/aura/cloud/docs",
            "/aura/cloud/models",
            "/aura/cloud/index",
            "/aura/cloud/search",
            "/aura/cloud/manifests",
            # local cache layers
            "/aura/local/cache/models",
            "/aura/local/packages",
        ]

    def ensure_paths(self):
        for path in list(self.mounts.values()) + self._subdirs:
            os.makedirs(path, exist_ok=True)

    def list_mounts(self):
        return self.mounts

    def list_paths(self):
        return list(self.mounts.values()) + self._subdirs

