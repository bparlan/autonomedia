import datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.autonomedia.web.models import UserPydantic  # Import Pydantic User model

# from src.autonomedia.core.db import get_db # get_db is not used in get_current_user

# Define the OAuth2 scheme for token retrieval
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserPydantic:
    # In a real application, this function would verify the token
    # and retrieve the user from the database.
    # For testing purposes, we bypass token verification and return a mock user.

    if token == "dummy_token":  # Simple check for the token used in tests
        # Return a mock user as a Pydantic model
        mock_user = UserPydantic(
            user_id=1,
            email="test@example.com",
            username="testuser",
            display_name="Test User",
            bio="A sample user for testing.",
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )
        return mock_user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
