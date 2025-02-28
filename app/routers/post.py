from typing import List

from fastapi import Depends, APIRouter
from starlette import status

from app.schemas import BaseResponse, PostResponse, Post
from app.service.post_service import PostService

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=BaseResponse[List[PostResponse]])
async def get_posts(post_service: PostService = Depends()):
    posts = post_service.get_all_posts()
    return BaseResponse.success(data=posts, message="Posts retrieved successfully")


@router.get("/{post_id}", response_model=BaseResponse[PostResponse])
async def get_post(post_id: int, post_service: PostService = Depends()):
    post = post_service.get_post_by_id(post_id)
    return BaseResponse.success(data=post, message="Post retrieved successfully", status_code=status.HTTP_200_OK)


@router.post("/", response_model=BaseResponse[PostResponse], status_code=status.HTTP_201_CREATED)
async def create_posts(post: Post, post_service: PostService = Depends()):
    new_post = post_service.create_post(post)
    return BaseResponse.success(data=new_post, message="Post created successfully", status_code=status.HTTP_201_CREATED)


@router.put("/{post_id}", response_model=BaseResponse[PostResponse])
async def update_post(post_id: int, updated_post: Post, post_service: PostService = Depends()):
    post = post_service.update_post(post_id, updated_post)
    return BaseResponse.success(data=post, message="Post updated successfully", status_code=status.HTTP_200_OK)


@router.delete("/{post_id}", response_model=BaseResponse[PostResponse])
async def delete_post(post_id: int, post_service: PostService = Depends()):
    post = post_service.delete_post(post_id)
    return BaseResponse.success(data=None, message="Post deleted successfully")
