from typing import List

from fastapi import Depends
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.orm import Session

from app.database import models
from app.database.database import get_db
from app.exceptions.custom_exceptions import (
    EntityNotFoundException,
    DatabaseConnectionException,
    DatabaseTimeoutException,
    InternalServerError,
    ActionNotPermittedException
)
from app.schemas.post_model import PostResponse, PostModel


class PostService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_all_posts(self) -> List[PostResponse]:
        posts = self.db.query(models.Post).all()
        return [PostResponse.model_validate(post) for post in posts]

    def get_post_by_id(self, post_id: int) -> PostResponse:
        post = self.db.query(models.Post).filter(models.Post.id == post_id).first()
        if not post:
            raise EntityNotFoundException(entity_name="Post", identifier=post_id)
        return PostResponse.model_validate(post)

    def create_post(self, post: PostModel, current_user) -> PostResponse:
        owner_id = current_user.get("id")
        try:
            new_post = models.Post(owner_id=owner_id, **post.model_dump())
            self.db.add(new_post)
            self.db.commit()
            self.db.refresh(new_post)
            return PostResponse.model_validate(new_post)
        except OperationalError:
            self.db.rollback()
            raise DatabaseConnectionException(reason="Failed to connect to the database. Please try again later.")
        except IntegrityError as e:
            self.db.rollback()
            raise e
        except TimeoutError:
            self.db.rollback()
            raise DatabaseTimeoutException(reason="Database operation timed out. Please try again later.")
        except Exception as e:
            self.db.rollback()
            raise InternalServerError(reason=str(e))

    def update_post(self, post_id: int, updated_post: PostModel) -> PostResponse:
        post = self.db.query(models.Post).filter(models.Post.id == post_id).first()
        if not post:
            raise EntityNotFoundException(entity_name="Post", identifier=post_id)
        updated_data = updated_post.model_dump()
        # Trim off spaces for title and content if they exist
        updated_data["title"] = updated_data.get('title').strip() if "title" in updated_data else None
        updated_data["content"] = updated_data["content"].strip() if "content" in updated_data else None

        for field, value in updated_data.items():
            setattr(post, field, value)
        self.db.commit()
        self.db.refresh(post)
        return PostResponse.model_validate(post)

    def delete_post(self, post_id: int, current_user) -> PostResponse:
        post = self.db.query(models.Post).filter(models.Post.id == post_id).first()
        if post.owner.id != current_user.get("id"):
            raise ActionNotPermittedException(
                reason="You are not authorized to delete a post that does not belong to you.")
        if not post:
            raise EntityNotFoundException(entity_name="Post", identifier=post_id)
        self.db.delete(post)
        self.db.commit()
        return PostResponse.model_validate(post)
