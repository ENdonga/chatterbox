from typing import List

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from app import models
from app.database import get_db
from app.schemas import BaseResponse, PostResponse, Post

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=BaseResponse[List[PostResponse]])
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not retrieve posts. No posts found")
    return BaseResponse.success(
        data=[PostResponse.model_validate(post) for post in posts],
        message="Posts retrieved successfully"
    )


@router.post("/", response_model=BaseResponse[PostResponse], status_code=status.HTTP_201_CREATED)
async def create_posts(post: Post, db: Session = Depends(get_db)):
    try:
        new_post = models.Post(**post.model_dump())
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return BaseResponse.success(data=PostResponse.model_validate(new_post), message="Post created successfully",
                                    status_code=status.HTTP_201_CREATED)
    except IntegrityError as e:
        db.rollback()
        raise e

    except Exception as e:
        db.rollback()  # Rollback changes if an error occurs
        raise e


@router.get("/{post_id}", response_model=BaseResponse[PostResponse])
async def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {post_id} not found")
    return BaseResponse.success(data=PostResponse.model_validate(post), message="Post retrieved successfully",
                                status_code=status.HTTP_200_OK)


@router.delete("/{post_id}", response_model=BaseResponse[PostResponse])
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {post_id} not found")
    db.delete(post)
    db.commit()
    return BaseResponse.success(data=None, message="Post deleted successfully")


@router.put("/{post_id}", response_model=BaseResponse[PostResponse])
async def update_post(post_id: int, updated_post: Post, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {post_id} not found")
    for field, value in updated_post.model_dump().items():
        setattr(post, field, value)
    db.commit()
    db.refresh(post)
    return BaseResponse.success(data=PostResponse.model_validate(post), message="Post updated successfully",
                                status_code=status.HTTP_200_OK)
