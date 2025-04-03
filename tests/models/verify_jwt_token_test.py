import pytest
import jwt
import os
from fastapi import HTTPException
from app.services.verify_jwt_token import verify_jwt_token
from dotenv import load_dotenv

load_dotenv('.env.test')

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def create_jwt_token(payload, secret=SECRET_KEY, algorithm=ALGORITHM):
    return jwt.encode(payload, secret, algorithm=algorithm)


def test_verify_valid_jwt_token():
    payload = {"sub": "test_user"}
    token = create_jwt_token(payload)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    decoded_payload = verify_jwt_token(token)
    assert decoded_payload["sub"] == "test_user"


def test_verify_expired_jwt_token():
    expired_payload = {"sub": "test_user", "exp": 0}
    token = create_jwt_token(expired_payload)

    with pytest.raises(HTTPException) as exc_info:
        verify_jwt_token(token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"


def test_verify_invalid_jwt_token():
    payload = {"sub": "test_user"}
    invalid_token = create_jwt_token(
        payload, secret="wrong_secret_key")

    with pytest.raises(HTTPException) as exc_info:
        verify_jwt_token(invalid_token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"


def test_verify_malformed_jwt_token():
    malformed_token = "this.is.not.a.valid.token"

    with pytest.raises(HTTPException) as exc_info:
        verify_jwt_token(malformed_token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"
