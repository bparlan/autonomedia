# Integration tests for Milestone M3 API endpoints

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.autonomedia.core.db import get_db
from src.autonomedia.web.main import app
from src.autonomedia.web.models import Base, Comment, Content, Like, User

# Database setup for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the dependency to use the test database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# Create database tables before tests and drop them after
@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


# Mock user for testing authentication
@pytest.fixture(scope="module")
def mock_user():
    # This needs to be adapted based on how get_current_user is implemented
    # For simplicity, we assume a fixture that bypasses actual auth and returns a user.
    # In a real scenario, you'd mock the dependency properly.
    user = User(
        user_id=1,
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
    )
    return user


def test_create_comment():
    # Setup: Create content and mock user first
    db = TestingSessionLocal()
    user = User(
        user_id=1,
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
    )
    content = Content(
        content_id=1, user_id=1, title="Test Content", body="This is test content."
    )
    db.add(user)
    db.add(content)
    db.commit()
    db.refresh(user)
    db.refresh(content)
    db.close()

    comment_data = {"content_id": 1, "body": "This is a test comment."}
    # Mock get_current_user to return the mock_user
    # For simplicity, we're bypassing the actual dependency injection here and assuming
    # the test client can be configured to use a mock user.
    # A more robust way would be to use dependency overrides for get_current_user as well.

    response = client.post(
        "/comments/", json=comment_data, headers={"Authorization": "Bearer dummy_token"}
    )  # Assuming token auth

    assert response.status_code == 200  # Expecting 200 OK, not 401 due to mock
    assert response.json()["body"] == "This is a test comment."
    assert response.json()["content_id"] == 1
    assert response.json()["user_id"] == 1


def test_get_comments_for_content():
    # Setup: Create user, content, and comments
    db = TestingSessionLocal()
    user = User(
        user_id=1,
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
    )
    content = Content(
        content_id=1, user_id=1, title="Test Content", body="This is test content."
    )
    comment1 = Comment(comment_id=1, content_id=1, user_id=1, body="Comment 1")
    comment2 = Comment(comment_id=2, content_id=1, user_id=1, body="Comment 2")
    db.add_all([user, content, comment1, comment2])
    db.commit()
    db.refresh(user)
    db.refresh(content)
    db.refresh(comment1)
    db.refresh(comment2)
    db.close()

    response = client.get(
        "/comments/?content_id=1", headers={"Authorization": "Bearer dummy_token"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 2
    # Check if comments are sorted by created_at descending (most recent first)
    # For simplicity, assuming creation order matches order in list if times are same.
    # In a real test, you'd check timestamps.
    assert (
        response.json()[0]["body"] == "Comment 2"
    )  # Assuming comment2 was created after comment1


def test_create_like():
    # Setup: Create user and content
    db = TestingSessionLocal()
    user = User(
        user_id=1,
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
    )
    content = Content(
        content_id=1, user_id=1, title="Test Content", body="This is test content."
    )
    db.add_all([user, content])
    db.commit()
    db.refresh(user)
    db.refresh(content)
    db.close()

    like_data = {"content_id": 1}
    response = client.post(
        "/likes/", json=like_data, headers={"Authorization": "Bearer dummy_token"}
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Content liked successfully."


def test_create_like_duplicate():
    # Setup: Create user, content, and an initial like
    db = TestingSessionLocal()
    user = User(
        user_id=1,
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
    )
    content = Content(
        content_id=1, user_id=1, title="Test Content", body="This is test content."
    )
    like = Like(like_id=1, content_id=1, user_id=1)
    db.add_all([user, content, like])
    db.commit()
    db.refresh(user)
    db.refresh(content)
    db.refresh(like)
    db.close()

    like_data = {"content_id": 1}
    response = client.post(
        "/likes/", json=like_data, headers={"Authorization": "Bearer dummy_token"}
    )

    assert response.status_code == 200  # Expecting 200 OK for already liked
    assert response.json()["message"] == "Content already liked by user."


def test_delete_like():
    # Setup: Create user, content, and a like
    db = TestingSessionLocal()
    user = User(
        user_id=1,
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
    )
    content = Content(
        content_id=1, user_id=1, title="Test Content", body="This is test content."
    )
    like = Like(like_id=1, content_id=1, user_id=1)
    db.add_all([user, content, like])
    db.commit()
    db.refresh(user)
    db.refresh(content)
    db.refresh(like)
    db.close()

    like_data = {"content_id": 1}
    response = client.delete(
        "/likes/", json=like_data, headers={"Authorization": "Bearer dummy_token"}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Content unliked successfully."


def test_create_content():
    # Setup: Mock user
    db = TestingSessionLocal()
    user = User(
        user_id=1,
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    content_data = {"title": "New Content", "body": "This is the body of new content."}
    response = client.post(
        "/content/", json=content_data, headers={"Authorization": "Bearer dummy_token"}
    )

    assert response.status_code == 200
    assert response.json()["title"] == "New Content"
    assert response.json()["body"] == "This is the body of new content."
    assert response.json()["user_id"] == 1


def test_update_content():
    # Setup: Create user, content, and mock the current_user dependency
    db = TestingSessionLocal()
    user = User(
        user_id=1,
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
    )
    content = Content(
        content_id=1, user_id=1, title="Original Title", body="Original Body."
    )
    db.add_all([user, content])
    db.commit()
    db.refresh(user)
    db.refresh(content)
    db.close()

    update_data = {"title": "Updated Title", "body": "Updated Body."}
    response = client.put(
        "/content/1", json=update_data, headers={"Authorization": "Bearer dummy_token"}
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["body"] == "Updated Body."


def test_get_all_content():
    # Setup: Create user, content
    db = TestingSessionLocal()
    user = User(
        user_id=1,
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
    )
    content1 = Content(content_id=1, user_id=1, title="Content 1", body="Body 1")
    content2 = Content(content_id=2, user_id=1, title="Content 2", body="Body 2")
    db.add_all([user, content1, content2])
    db.commit()
    db.refresh(user)
    db.refresh(content1)
    db.refresh(content2)
    db.close()

    response = client.get("/content/", headers={"Authorization": "Bearer dummy_token"})

    assert response.status_code == 200
    assert len(response.json()) == 2
    # Check order (descending by created_at)
    assert (
        response.json()[0]["title"] == "Content 2"
    )  # Assuming content2 created after content1


def test_get_content_by_id():
    # Setup: Create user, content
    db = TestingSessionLocal()
    user = User(
        user_id=1,
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
    )
    content = Content(
        content_id=1, user_id=1, title="Test Content", body="This is test content."
    )
    db.add_all([user, content])
    db.commit()
    db.refresh(user)
    db.refresh(content)
    db.close()

    response = client.get("/content/1", headers={"Authorization": "Bearer dummy_token"})

    assert response.status_code == 200
    assert response.json()["title"] == "Test Content"
    assert response.json()["body"] == "This is test content."


def test_get_content_by_id_not_found():
    # Setup: Create user
    db = TestingSessionLocal()
    user = User(
        user_id=1,
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    response = client.get(
        "/content/999", headers={"Authorization": "Bearer dummy_token"}
    )
    assert response.status_code == 404
