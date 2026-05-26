import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt

JWT_SECRET = os.environ.get("JWT_SECRET", "supersecretjwtkeythatissecretdontshare")
JWT_ALGORITHM = "HS256"

def create_access_token(subject: str, role: str, tenant_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token for authentication."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=60 * 24)  # 24 hours

    to_encode: Dict[str, Any] = {
        "sub": subject,
        "role": role,
        "tenant_id": tenant_id,
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
