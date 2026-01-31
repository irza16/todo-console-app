"""
Database configuration and connection management for SQLModel with Neon PostgreSQL.
"""
from typing import Optional
from pydantic_settings import BaseSettings
from sqlmodel import SQLModel, create_engine, Session, pool


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    cors_origin: str = "http://localhost:3000"
    groq_api_key: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Create SQLModel engine with connection pooling for Neon Serverless
engine = create_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False,  # Set to True for debugging SQL queries
)


def get_session():
    """Get a database session."""
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()


def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)
