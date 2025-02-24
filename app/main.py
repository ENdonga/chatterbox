from typing import List

from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy.orm import Session

from . import models
from .database import engine, get_db
from .schemas import Post, BaseResponse, PostResponse

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

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


@app.get("/posts", response_model=BaseResponse[List[PostResponse]])
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    if not posts:
        BaseResponse.error("Request Failed", "Could retrieve posts", status_code=status.HTTP_404_NOT_FOUND)
    return BaseResponse.success(
        data=[PostResponse.model_validate(post) for post in posts],
        message="Posts retrieved successfully"
    )


@app.post("/posts", response_model=BaseResponse[PostResponse], status_code=status.HTTP_201_CREATED)
async def create_posts(post: Post, db: Session = Depends(get_db)):
    try:
        new_post = models.Post(**post.model_dump())
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return BaseResponse.success(data=PostResponse.model_validate(new_post), message="Post created successfully",
                                    status_code=status.HTTP_201_CREATED)
    except Exception as e:
        db.rollback()  # Rollback changes if an error occurs
        return BaseResponse.error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to create post",
            reason=str(e)
        )


@app.get("/posts/{post_id}", response_model=BaseResponse[PostResponse])
async def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        BaseResponse.error("Request Failed", f"Post with id: {post_id} not found",
                           status_code=status.HTTP_404_NOT_FOUND)
    return BaseResponse.success(data=PostResponse.model_validate(post), message="Post retrieved successfully",
                                status_code=status.HTTP_200_OK)


@app.delete("/posts/{post_id}", response_model=BaseResponse[PostResponse])
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        BaseResponse.error("Request Failed", f"Post with id: {post_id} not found",
                           status_code=status.HTTP_404_NOT_FOUND)
    db.delete(post)
    db.commit()
    return BaseResponse.success(data=None, message="Post deleted successfully")


@app.put("/posts/{post_id}", response_model=BaseResponse[PostResponse])
async def update_post(post_id: int, updated_post: Post, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        BaseResponse.error("Request Failed", f"Post with id: {post_id} not found",
                           status_code=status.HTTP_404_NOT_FOUND)
    for field, value in updated_post.model_dump().items():
        setattr(post, field, value)
    db.commit()
    db.refresh(post)
    return BaseResponse.success(data=PostResponse.model_validate(post), message="Post updated successfully",
                                status_code=status.HTTP_200_OK)
