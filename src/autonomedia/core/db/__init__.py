from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Assuming a database URL is configured, e.g., from environment variables or a config file.
# For testing, we use an SQLite in-memory database.
# For the actual application, this would be a PostgreSQL or other DB URL.
# As a placeholder, let's use a default SQLite URL.
SQLALCHEMY_DATABASE_URL = "sqlite:///./autonomedia.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
