"""CockroachDB engine and transaction boundaries."""

import os
from collections.abc import Generator
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Base class for transactional persistence models."""


def load_database_url() -> str:
    """Resolve the database URL, preferring an explicitly supplied local value."""
    database_url = os.getenv("DATABASE_URL")
    database_url_secret_arn = os.getenv("DATABASE_URL_SECRET_ARN")
    if database_url is None and database_url_secret_arn:
        database_url = boto3.client("secretsmanager").get_secret_value(
            SecretId=database_url_secret_arn
        )["SecretString"]
    if database_url is None:
        database_url = "cockroachdb://root@localhost:26257/travel_operations?sslmode=disable"
    if database_url.startswith("postgresql"):
        database_url = database_url.replace(
            database_url.split(":", maxsplit=1)[0], "cockroachdb", 1
        )
    root_cert_secret_arn = os.getenv("COCKROACH_ROOT_CERT_SECRET_ARN")
    if root_cert_secret_arn:
        root_cert = boto3.client("secretsmanager").get_secret_value(SecretId=root_cert_secret_arn)[
            "SecretString"
        ]
        root_cert_path = Path("/tmp/cockroach-root.crt")
        root_cert_path.write_text(root_cert, encoding="utf-8")
        parsed = urlsplit(database_url)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query["sslrootcert"] = str(root_cert_path)
        database_url = urlunsplit(
            (parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment)
        )
    return database_url


database_url = load_database_url()

engine = create_engine(
    database_url,
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
