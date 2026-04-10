import os
from core.runtime.vfs import HybridVFS

def ls(path):
    try:
        return os.listdir(path)
    except:
        return ["Path not found"]

def cat(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except:
        return "Cannot read file"

def mounts():
    vfs = HybridVFS()
    return vfs.list_mounts()

def jobs(scheduler):
    return scheduler.status()["processes"]
