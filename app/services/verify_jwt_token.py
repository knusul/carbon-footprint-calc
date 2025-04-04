import jwt
import os
from fastapi import HTTPException, status
from typing import Dict, Any

def verify_jwt_token(token: str) -> Any:
    SECRET_KEY = os.getenv("SECRET_KEY", '')
    ALGORITHM = os.getenv("ALGORITHM", '')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
