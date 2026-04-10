import os
from core.runtime.paths import aura_path


class HybridVFS:
    def __init__(self):
        self.mounts = {
            "cloud":    aura_path("cloud"),
            "cache":    aura_path("local", "cache"),
            "packages": aura_path("local", "packages"),
        }
        self._subdirs = [
            # cloud output buckets
            aura_path("cloud", "images"),
            aura_path("cloud", "videos"),
            aura_path("cloud", "apk"),
            aura_path("cloud", "docs"),
            aura_path("cloud", "models"),
            aura_path("cloud", "index"),
            aura_path("cloud", "search"),
            aura_path("cloud", "manifests"),
            # local cache layers
            aura_path("local", "cache", "models"),
            aura_path("local", "packages"),
        ]

    def ensure_paths(self):
        for path in list(self.mounts.values()) + self._subdirs:
            os.makedirs(path, exist_ok=True)

    def list_mounts(self):
        return self.mounts

    def list_paths(self):
        return list(self.mounts.values()) + self._subdirs

