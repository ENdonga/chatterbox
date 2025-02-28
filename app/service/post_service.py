from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status

from app.database import models
from app.database.database import get_db
from app.schemas.post import PostResponse, Post


class PostService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_all_posts(self) -> List[PostResponse]:
        posts = self.db.query(models.Post).all()
        if not posts:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Could not retrieve posts. No posts found")
        return [PostResponse.model_validate(post) for post in posts]

    def get_post_by_id(self, post_id: int) -> PostResponse:
        post = self.db.query(models.Post).filter(models.Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {post_id} not found")
        return PostResponse.model_validate(post)

    def create_post(self, post: Post) -> PostResponse:
        try:
            new_post = models.Post(**post.model_dump())
            self.db.add(new_post)
            self.db.commit()
            self.db.refresh(new_post)
            return PostResponse.model_validate(new_post)
        except IntegrityError as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            raise e

    def update_post(self, post_id: int, updated_post: Post) -> PostResponse:
        post = self.db.query(models.Post).filter(models.Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {post_id} not found")
        for field, value in updated_post.model_dump().items():
            setattr(post, field, value)
        self.db.commit()
        self.db.refresh(post)
        return PostResponse.model_validate(post)

    def delete_post(self, post_id: int) -> PostResponse:
        post = self.db.query(models.Post).filter(models.Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {post_id} not found")
        self.db.delete(post)
        self.db.commit()
        return PostResponse.model_validate(post)
