from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.autonomedia.core.db import get_db
from src.autonomedia.core.security import get_current_user
from src.autonomedia.web.models import (  # Import Pydantic models
    Comment,
    CommentPydantic,
    Content,
    UserPydantic,
)

router = APIRouter(
    prefix="/comments",
    tags=["comments"]
)

# Request body model for creating a comment
class CreateCommentRequest(BaseModel):
    content_id: int
    body: str

@router.post("/", response_model=CommentPydantic)
def create_comment(comment_data: CreateCommentRequest, db: Session = Depends(get_db), current_user: UserPydantic = Depends(get_current_user)):
    content_id = comment_data.content_id
    body = comment_data.body

    # Check if content exists
    content_item = db.query(Content).filter(Content.content_id == content_id).first()
    if not content_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")

    new_comment = Comment(
        content_id=content_id,
        user_id=current_user.user_id,
        body=body
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment

@router.get("/", response_model=List[CommentPydantic])
def get_comments_for_content(content_id: int, db: Session = Depends(get_db), current_user: UserPydantic = Depends(get_current_user)):
    # Check if content exists
    content_item = db.query(Content).filter(Content.content_id == content_id).first()
    if not content_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")

    # Check if user is authenticated (even if content is public, for consistency)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    comments = db.query(Comment).filter(Comment.content_id == content_id).order_by(Comment.created_at.desc()).all()
    return comments

# Note: Edit and Delete comment endpoints would be added here in a full implementation.
# For M3, we focus on Create and Read for comments.
