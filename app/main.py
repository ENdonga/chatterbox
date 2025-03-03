from fastapi import FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import IntegrityError, OperationalError

from .database import models
from .database.database import engine
from .exceptions.custom_exceptions import ChatterBoxException, UnknownHashException
from .exceptions.exception_handler import (
    chatterbox_exception_handler,
    http_exception_handler,
    integrity_error_handler,
    database_connection_error_handler,
    general_exception_handler,
    unknown_hash_exception_handler
)
from starlette.exceptions import HTTPException as StarletteHTTPException
from .routers import post, user, authentication

models.Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="My API",
    description="This API provides authentication and user management services.",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Endpoints for user authentication, including login and token generation.\nAfter successful login, an access token is provided, which is required for accessing secured endpoints.\nUse this token in the Authorization header as 'Bearer <token>' to authenticate requests. 🔐"
        },
        {
            "name": "Users",
            "description": "Endpoints for managing user accounts, such as creating new users, retrieving user details, and updating user information.\nOnly authenticated users can access protected routes. 👤"
        },
        {
            "name": "Posts",
            "description": "Endpoints for creating, retrieving, updating, and deleting posts.\nUsers can publish content, fetch posts, and interact with posts based on their permissions. ✍️"
        }
    ]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Register exception handlers
app.add_exception_handler(ChatterBoxException, chatterbox_exception_handler)
app.add_exception_handler(UnknownHashException, unknown_hash_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(OperationalError, database_connection_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(post.router, tags=["Posts"])
app.include_router(user.router, tags=["Users"])
app.include_router(authentication.router, tags=["Authentication"])
