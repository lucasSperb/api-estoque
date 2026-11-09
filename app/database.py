import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


def _database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        # No Railway o disco é descartado a cada deploy: sem banco, os dados sumiriam em silêncio.
        if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_ENVIRONMENT_NAME"):
            raise RuntimeError(
                "DATABASE_URL não definida. Em Variables do serviço, crie DATABASE_URL = ${{Postgres.DATABASE_URL}}."
            )
        url = "sqlite:///./local.db"
    # Railway e Heroku antigos entregam "postgres://"; o SQLAlchemy exige "postgresql://".
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


DATABASE_URL = _database_url()

_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
