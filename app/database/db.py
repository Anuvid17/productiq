from typing import Generator, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from app.config import DATABASE_URL
from app.utils.logger import logger


class Base(DeclarativeBase):
    """Declarative Base class for all SQLAlchemy 2.x ORM models."""
    pass


# Lazy engine instantiation helper / default engine setup
def get_engine(url: str = DATABASE_URL):
    """
    Create and return a SQLAlchemy 2.x engine.
    Supports PostgreSQL (psycopg3) and SQLite fallback for unit testing.
    """
    engine_kwargs: dict[str, Any] = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        engine_kwargs["connect_args"] = {"connect_timeout": 3}
        engine_kwargs["pool_size"] = 5
        engine_kwargs["max_overflow"] = 10

    return create_engine(url, **engine_kwargs)



# Default application engine and SessionLocal factory
engine = get_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db_session(db_engine=None) -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    Automatically commits on success, rolls back on exception, and closes session.
    """
    factory = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=db_engine or engine)
    session: Session = factory()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session transaction failed: {e}")
        raise
    finally:
        session.close()


import time

_fallback_engine = None
_last_health_check_time = 0.0
_last_health_status = None


def get_active_engine():
    """
    Returns primary PostgreSQL engine if connected, or initializes SQLite fallback engine if offline.
    Caches health status to avoid connection timeout latency on every request.
    """
    global _fallback_engine, _last_health_check_time, _last_health_status
    if _fallback_engine is not None:
        return _fallback_engine

    now = time.time()
    if _last_health_status is None or (now - _last_health_check_time) > 300.0:
        _last_health_status = check_db_health(engine)
        _last_health_check_time = now

    if _last_health_status.get("connected"):
        return engine
    
    if _fallback_engine is None:
        logger.warning("PostgreSQL connection unavailable. Initializing persistent SQLite fallback engine (productiq_dev.db) for API database sessions.")
        _fallback_engine = create_engine(
            "sqlite:///productiq_dev.db",
            connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(_fallback_engine)
    return _fallback_engine


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI-compatible database session dependency generator.
    Uses primary PostgreSQL engine or SQLite fallback engine when PostgreSQL is offline.
    """
    active_engine = get_active_engine()
    factory = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=active_engine)
    db = factory()
    try:
        yield db
    finally:
        db.close()


def check_db_health(target_engine=None) -> dict:
    """
    Lightweight health check performing a 'SELECT 1' query.
    Returns structured status result without exposing credentials.
    """
    active = target_engine or (_fallback_engine if _fallback_engine is not None else engine)
    try:
        with active.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": active.dialect.name,
            "connected": True
        }
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": active.dialect.name,
            "connected": False,
            "error": str(e)
        }
