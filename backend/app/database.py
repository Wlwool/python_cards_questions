import sqlite3

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def _py_lower(value):
    """Нижний регистр: встроенная lower() в SQLite знает только ASCII"""
    return value.lower() if isinstance(value, str) else value


@event.listens_for(Engine, "connect")
def _register_sqlite_functions(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        dbapi_connection.create_function("py_lower", 1, _py_lower, deterministic=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
