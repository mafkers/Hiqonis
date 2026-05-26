import hashlib
import os

def hash_password(password: str) -> str:
    """Hash password using native memory-hard scrypt algorithm."""
    salt = os.urandom(16)
    # n=16384 (CPU/memory cost), r=8 (block size), p=1 (parallelization)
    key = hashlib.scrypt(password.encode('utf-8'), salt=salt, n=16384, r=8, p=1)
    return f"scrypt:{salt.hex()}:{key.hex()}"

def verify_password(password: str, hashed: str) -> bool:
    """Verify password match against stored scrypt hash."""
    try:
        parts = hashed.split(":")
        if len(parts) != 3 or parts[0] != "scrypt":
            return False
        salt = bytes.fromhex(parts[1])
        expected_key = bytes.fromhex(parts[2])
        key = hashlib.scrypt(password.encode('utf-8'), salt=salt, n=16384, r=8, p=1)
        return key == expected_key
    except Exception:
        return False
