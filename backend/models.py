"""ORM 模型：与 docs/schema.sql 对应。"""
from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    DECIMAL,
    Integer,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class DimGenre(Base):
    __tablename__ = "dim_genre"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, unique=True)


class DimCountry(Base):
    __tablename__ = "dim_country"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, unique=True)


class DimYear(Base):
    __tablename__ = "dim_year"
    year = Column(SmallInteger, primary_key=True)


class Movie(Base):
    __tablename__ = "movie"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    douban_id = Column(String(32), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    director = Column(String(255))
    actors = Column(Text)
    genre = Column(String(128))
    country = Column(String(128))
    year = Column(SmallInteger)
    rating = Column(DECIMAL(3, 1))
    rating_count = Column(Integer)
    summary = Column(Text)
    poster_url = Column(String(512))
    created_at = Column(DateTime, server_default=func.current_timestamp())


class AggGenre(Base):
    __tablename__ = "agg_genre"
    genre = Column(String(64), primary_key=True)
    movie_count = Column(Integer)
    avg_rating = Column(DECIMAL(3, 2))


class AggCountry(Base):
    __tablename__ = "agg_country"
    country = Column(String(64), primary_key=True)
    movie_count = Column(Integer)
    avg_rating = Column(DECIMAL(3, 2))


class AggYear(Base):
    __tablename__ = "agg_year"
    year = Column(SmallInteger, primary_key=True)
    movie_count = Column(Integer)
    avg_rating = Column(DECIMAL(3, 2))