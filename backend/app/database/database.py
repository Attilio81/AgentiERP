"""
Database connection and session management using SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# Create SQLAlchemy engine
# For SQL Server with pyodbc, connection pooling is important
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,
    max_overflow=10,
    echo=False  # Set to True for SQL debugging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for ORM models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Use with FastAPI Depends() to automatically handle session lifecycle.
    
    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
