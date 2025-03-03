import logging
from datetime import timedelta, datetime

import jwt

from app.core.config import config
from app.exceptions.custom_exceptions import InvalidTokenException, ExpiredTokenException, TokenSignatureException

SECRET_KEY = config.SECRET_KEY
JWT_ALGORITHM = config.ALGORITHM
EXPIRY_TIME_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRY_DAY = config.REFRESH_TOKEN_EXPIRE_DAYS


def create_access_token(user_data: dict, expiry: timedelta = None, refresh_token: bool = False) -> str:
    """Generates an access or refresh token for authentication."""
    payload = {
        "user": user_data,
        "exp": (datetime.now() + (expiry if expiry else timedelta(minutes=EXPIRY_TIME_MINUTES))).timestamp(),
        "iat": datetime.now().timestamp(),
        "refresh": refresh_token
    }
    access_token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=JWT_ALGORITHM)
    return access_token


def create_refresh_token(user_data: dict) -> str:
    """Generates a refresh token for authentication."""
    return create_access_token(user_data, expiry=timedelta(days=REFRESH_TOKEN_EXPIRY_DAY), refresh_token=True)


def decode_access_token(token: str) -> dict:
    """Decodes and validates an access token."""
    try:
        token_data = jwt.decode(token, key=SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return token_data
    except jwt.ExpiredSignatureError:
        logging.exception("Token has expired")
        raise ExpiredTokenException(reason="Token has expired. Please log in again.")
    except jwt.InvalidTokenError:
        logging.exception("Invalid token")
        raise TokenSignatureException(reason="Invalid authentication token.")
    except jwt.PyJWTError:
        logging.exception(f"Invalid token: {token}")
        raise InvalidTokenException()
