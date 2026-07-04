
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.autonomedia.core.db import get_db
from src.autonomedia.core.security import get_current_user
from src.autonomedia.web.models import (
    Content,
    Like,
    LikePydantic,
    UserPydantic,
)  # Import Pydantic models

router = APIRouter(prefix="/likes", tags=["likes"])


# Request body models
class LikeRequest(BaseModel):
    content_id: int


class UnlikeRequest(BaseModel):
    content_id: int


@router.post("/", response_model=LikePydantic)
def create_like(
    like_data: LikeRequest,
    db: Session = Depends(get_db),
    current_user: UserPydantic = Depends(get_current_user),
):
    content_id = like_data.content_id

    if not content_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing content_id"
        )

    # Check if content exists
    content_item = db.query(Content).filter(Content.content_id == content_id).first()
    if not content_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    # Check if user has already liked this content
    existing_like = (
        db.query(Like)
        .filter(Like.content_id == content_id, Like.user_id == current_user.user_id)
        .first()
    )

    if existing_like:
        # Return existing like if already present, or adjust logic as needed
        return existing_like

    new_like = Like(content_id=content_id, user_id=current_user.user_id)
    db.add(new_like)
    db.commit()
    db.refresh(new_like)

    return new_like


@router.delete("/", response_model=dict)
def delete_like(
    unlike_data: UnlikeRequest,
    db: Session = Depends(get_db),
    current_user: UserPydantic = Depends(get_current_user),
):
    content_id = unlike_data.content_id

    if not content_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing content_id"
        )

    # Check if content exists
    content_item = db.query(Content).filter(Content.content_id == content_id).first()
    if not content_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    # Find and delete the like
    like_to_delete = (
        db.query(Like)
        .filter(Like.content_id == content_id, Like.user_id == current_user.user_id)
        .first()
    )

    if not like_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found for this content by the user.",
        )

    db.delete(like_to_delete)
    db.commit()
    return {"message": "Content unliked successfully."}


# Endpoint to get like count for a content item could be added here
