import sys
from pathlib import Path

# Ensure project root and venv site-packages are in sys.path BEFORE any imports
ROOT_DIR = Path(__file__).resolve().parent.parent
VENV_SITE = ROOT_DIR / "venv" / "Lib" / "site-packages"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if VENV_SITE.exists() and str(VENV_SITE) not in sys.path:
    sys.path.insert(0, str(VENV_SITE))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database.db import Base, get_db
from app.main import app


@pytest.fixture
def db_session():
    """
    Isolated in-memory SQLite test database fixture.
    Overrides FastAPI get_db dependency so TestClient uses this session.
    """
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(test_engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()

    def _override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    try:
        yield session
    finally:
        app.dependency_overrides.clear()
        session.close()
