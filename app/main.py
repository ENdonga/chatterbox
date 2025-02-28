from fastapi import FastAPI

from .database import models
from .database.database import engine
from .exceptions.custom_exceptions import DatabaseIntegrityError
from .exceptions.exception_handler import custom_exception_handler
from .routers import post, user, authentication

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_exception_handler(Exception, custom_exception_handler)
app.add_exception_handler(DatabaseIntegrityError, custom_exception_handler)
# app.add_exception_handler(IntegrityError, handle_db_integrity_exception)
# app.add_exception_handler(HTTPException, handle_http_exception)
# app.add_exception_handler(Exception, handle_general_exception)

app.include_router(post.router)
app.include_router(user.router)

app.include_router(authentication.router)


@app.get("/")
async def root():
    return {"message": "Hello World!"}
