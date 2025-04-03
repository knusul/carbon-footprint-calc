import jwt
from datetime import datetime, timedelta

# Secret key used in your FastAPI app
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"

# Payload for the JWT
def create_jwt_token(user_id: str):
    expiration_time = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
    payload = {
        "sub": user_id,  # subject (typically the user ID or username)
        "exp": expiration_time
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Example usage:
token = create_jwt_token("user123")
print(token)
