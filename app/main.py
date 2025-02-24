from fastapi import FastAPI

from . import models
from .database import engine
from .routers import post, user

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app_posts = [
    {"id": 1, "title": "FastApi", "content": "Learning FastApi", "published": True, "rating": 1},
    {"id": 2, "title": "Python", "content": "Python for Beginners", "published": True, "rating": 2},
    {"id": 3, "title": "Spring Boot", "content": "Spring Boot for API development", "published": True, "rating": 3},
]


def find_post(post_id: int):
    for post in app_posts:
        if post["id"] == post_id:
            return post


def find_post_index(post_id: int):
    for i, post in enumerate(app_posts):
        if post["id"] == post_id:
            return i


app.include_router(post.router)
app.include_router(user.router)


@app.get("/")
async def root():
    return {"message": "Hello World!"}
