import hashlib

def sha256(s: str):
    return hashlib.sha256(s.encode()).hexdigest()
