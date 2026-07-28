"""CockroachDB engine and transaction boundaries."""
import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Base class for transactional persistence models."""


engine = create_engine(
    os.getenv("DATABASE_URL", "postgresql+psycopg://root@localhost:26257/travel_operations?sslmode=disable"),
    pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "5")),
    pool_pre_ping=True,
)
SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)


def session_scope() -> Generator[Session, None, None]:
    """Yield a session and atomically commit or roll back its transaction."""
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
