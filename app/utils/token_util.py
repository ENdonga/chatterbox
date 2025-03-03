import logging
from datetime import timedelta, datetime

import jwt
from fastapi import Depends
from starlette.requests import Request
from typing_extensions import Optional

from app.core.config import config
from app.exceptions.custom_exceptions import (
    InvalidTokenException,
    ExpiredTokenException,
    TokenSignatureException,
    InvalidAuthorizationHeaderException,
    EntityNotFoundException
)
from app.service.user_service import UserService

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


def get_token_from_header(request: Request) -> str:
    """
    Extracts the token from the Authorization header and validates its format.
    This raises appropriate exceptions if the header is missing or has an invalid format
    """
    auth_header: Optional[str] = request.headers.get("Authorization")
    if not auth_header:
        raise InvalidAuthorizationHeaderException(reason="Authorization header is missing.")
    parts = auth_header.split(" ")
    if len(parts) != 2 or not parts[0].lower() == "bearer":
        raise InvalidAuthorizationHeaderException(reason="Invalid Authorization header format. Use 'Bearer <token>'")
    return parts[1]


def get_current_user(token: str = Depends(get_token_from_header), user_service: UserService = Depends()) -> dict:
    """This is a dependency to get the current logged-in user from the access token."""
    if not token:
        raise InvalidAuthorizationHeaderException(reason="Token is required to access this resource.")
    payload = decode_access_token(token)
    if payload.get("refresh"):
        raise InvalidTokenException(reason="Please provide an access token.")
    user_data = payload.get("user")
    if not user_data:
        # id identifier is not accessible since there is no user, so use 0 since there will be no ID 0 in db
        raise EntityNotFoundException(entity_name="User", identifier=0)
    # Check if the user in the token still exists in the database
    user = user_service.get_user_by_id(user_data["id"])
    if not user:
        raise EntityNotFoundException(entity_name="User", identifier=user_data["id"])
    logging.info(f"Authenticated user: {user}")
    return user.model_dump()
