from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import asyncpg
import asyncio
from app.core.config import settings

# SQLAlchemy setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Initialize database tables"""
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")

# Async database connection for high-performance operations
async def get_async_db_connection():
    """Get async database connection for time-series operations"""
    try:
        conn = await asyncpg.connect(settings.DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error connecting to async database: {e}")
        return None
