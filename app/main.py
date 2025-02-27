from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import IntegrityError

from .database import models
from .database.database import engine
from .exceptions.exceptions import handle_db_integrity_exception, handle_http_exception, handle_general_exception
from .routers import post, user, authentication

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_exception_handler(IntegrityError, handle_db_integrity_exception)
app.add_exception_handler(HTTPException, handle_http_exception)
app.add_exception_handler(Exception, handle_general_exception)

app.include_router(post.router)
app.include_router(user.router)

app.include_router(authentication.router)


@app.get("/")
async def root():
    return {"message": "Hello World!"}
