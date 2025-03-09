from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from sqlalchemy.exc import IntegrityError, OperationalError

from .database import models
from .database.database import engine
from .exceptions.custom_exceptions import ChatterBoxException, DatabaseException
from .exceptions.exception_handler import (
    chatterbox_exception_handler,
    integrity_error_handler,
    database_connection_error_handler,
    general_exception_handler,
    database_exception_handler
)
from .routers import post, user, authentication

models.Base.metadata.create_all(bind=engine)
app = FastAPI()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="FastAPI application",
        version="1.0.0",
        description="JWT Authentication and Authorization",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    openapi_schema['tags'] = [
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
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Register exception handlers
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(DatabaseException, database_exception_handler)
app.add_exception_handler(OperationalError, database_connection_error_handler)
app.add_exception_handler(ChatterBoxException, chatterbox_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(post.router, tags=["Posts"])
app.include_router(user.router, tags=["Users"])
app.include_router(authentication.router, tags=["Authentication"])
