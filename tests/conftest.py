import os
import importlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def _sqlite_url() -> str:
    # File-based sqlite so multiple connections see the same schema.
    return "sqlite+pysqlite:///./tests/test.db"


@pytest.fixture(scope="session", autouse=True)
def _set_env_for_tests(_sqlite_url: str):
    # Ensure imports that read env vars behave predictably in tests.
    os.environ.setdefault("DATABASE_URL", _sqlite_url)
    os.environ.setdefault("JWT_KEY", "test-jwt-key")
    os.environ.setdefault("ADMIN_API_KEY", "test-admin-key")
    yield


@pytest.fixture(scope="session")
def engine(_sqlite_url: str):
    engine_ = create_engine(_sqlite_url, connect_args={"check_same_thread": False})
    yield engine_
    engine_.dispose()


@pytest.fixture()
def db_session(engine):
    """
    Creates a fresh schema for each test and yields a SQLAlchemy session.
    """
    # Import here so env vars are already set.
    from models.base import Base

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def app_with_overrides(db_session, monkeypatch):
    """
    Loads the FastAPI app and overrides dependency providers so requests use our test DB session,
    deterministic auth, and lightweight services.
    """
    import database as database_module
    import dependencies as dependencies_module

    # Make dependency get_db() yield the test session.
    def _get_db_override():
        try:
            yield db_session
        finally:
            pass

    # Patch database.session_local used by dependencies.get_db
    TestingSessionLocal = lambda: db_session  # noqa: E731
    monkeypatch.setattr(database_module, "session_local", TestingSessionLocal, raising=True)

    # Dependency override for get_db
    dependencies_module.get_db = _get_db_override  # type: ignore[assignment]

    # Import (or reload) main after overrides are in place.
    import main as main_module
    importlib.reload(main_module)

    return main_module.app


@pytest.fixture()
def client(app_with_overrides):
    return TestClient(app_with_overrides)

