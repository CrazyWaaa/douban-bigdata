"""数据库连接：SQLAlchemy + PyMySQL，引擎懒加载。"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from config import SETTINGS

engine = create_engine(
    SETTINGS.sqlalchemy_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True,
)

SessionLocal = scoped_session(
    sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
)


def get_session():
    return SessionLocal()
