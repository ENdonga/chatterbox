from fastapi import FastAPI, HTTPException
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
app = FastAPI()

# Register exception handlers
app.add_exception_handler(ChatterBoxException, chatterbox_exception_handler)
app.add_exception_handler(UnknownHashException, unknown_hash_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(OperationalError, database_connection_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(authentication.router)


@app.get("/")
async def root():
    return {"message": "Hello World!"}
