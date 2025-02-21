from typing import Optional

from fastapi import FastAPI, Request, Response, status, HTTPException
from pydantic import BaseModel

app = FastAPI()


class Post(BaseModel):
    id: int
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


app_posts = [
    {"id": 1, "title": "FastApi", "content": "Learning FastApi", "published": True, "rating": 1},
    {"id": 2, "title": "Python", "content": "Python for Beginners", "published": True, "rating": 2},
    {"id": 3, "title": "Spring Boot", "content": "Spring Boot for API development", "published": True, "rating": 3},
]


def find_post(id: int):
    for post in app_posts:
        if post["id"] == id:
            return post


def find_post_index(id: int):
    for i, post in enumerate(app_posts):
        if post["id"] == id:
            return i


@app.get("/")
async def root():
    return {"message": "Hello World!"}


@app.get("/posts")
async def get_posts():
    return {"posts": app_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_posts(post: Post):
    app_posts.append(post.dict())
    return {"data": post}


@app.get("/posts/{post_id}")
async def get_post(post_id: int, response: Response):
    post = find_post(post_id)
    if not post:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message': f"Post with id: {post_id} not found"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {post_id} not found")
    return {"data": post}


@app.delete("/posts/{post_id}")
async def delete_post(post_id: int):
    post = find_post(post_id)
    post_index = find_post_index(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {post_id} not found")
    app_posts.pop(post_index)
    return {"data": f'Post with id: {post_id} deleted'}


@app.put("/posts/{post_id}")
async def update_post(post_id: int, post: Post):
    post_index = find_post_index(post_id)
    if not post_index:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {post_id} not found")
    post_dict = post.dict()
    post_dict["id"] = post_id
    app_posts[post_index] = post_dict
    return {"data": post_dict}
