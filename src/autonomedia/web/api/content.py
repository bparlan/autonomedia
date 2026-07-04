from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.autonomedia.core.db import get_db
from src.autonomedia.core.security import get_current_user
from src.autonomedia.web.models import (
    Content,
    ContentPydantic,
    UserPydantic,
)  # Import Pydantic models

router = APIRouter(prefix="/content", tags=["content"])


# Request body models
class CreateContentRequest(BaseModel):
    title: str
    body: str


class UpdateContentRequest(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None


@router.post("/", response_model=ContentPydantic)
def create_content(
    content_data: CreateContentRequest,
    db: Session = Depends(get_db),
    current_user: UserPydantic = Depends(get_current_user),
):
    title = content_data.title
    body = content_data.body

    new_content = Content(user_id=current_user.user_id, title=title, body=body)
    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    return new_content


@router.put("/{content_id}", response_model=ContentPydantic)
def update_content(
    content_id: int,
    content_data: UpdateContentRequest,
    db: Session = Depends(get_db),
    current_user: UserPydantic = Depends(get_current_user),
):
    content_item = db.query(Content).filter(Content.content_id == content_id).first()

    if not content_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    # Ensure the user owns the content
    if content_item.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not own this content",
        )

    # Update fields if provided
    if content_data.title is not None:
        content_item.title = content_data.title
    if content_data.body is not None:
        content_item.body = content_data.body

    db.commit()
    db.refresh(content_item)
    return content_item


@router.get("/", response_model=List[ContentPydantic])
def get_all_content(
    db: Session = Depends(get_db),
    current_user: UserPydantic = Depends(get_current_user),
):
    content_list = db.query(Content).order_by(Content.created_at.desc()).all()
    return content_list


@router.get("/{content_id}", response_model=ContentPydantic)
def get_content_by_id(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: UserPydantic = Depends(get_current_user),
):
    content_item = db.query(Content).filter(Content.content_id == content_id).first()
    if not content_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    return content_item


# Note: Deletion endpoints would be added here in a full implementation.
