from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=False, unique=True)
    type = Column(String(20), default="rss")
    trust_score = Column(Float, default=0.5)
    status = Column(String(20), default="active")
    last_fetched_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    sort_order = Column(Integer, default=0)


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    source = Column(String(200), nullable=False)
    url = Column(Text, nullable=False, unique=True)
    date = Column(DateTime(timezone=True), nullable=True)
    tags = Column(String(500), default="")
    summary = Column(Text, nullable=True)
    content_text = Column(Text, nullable=True)
    content_format = Column(String(20), default="markdown")
    content_status = Column(String(20), default="pending")
    content_error = Column(Text, nullable=True)
    content_fetched_at = Column(DateTime(timezone=True), nullable=True)
    content_provider = Column(String(50), nullable=True)
    content_hash = Column(String(64), nullable=True)
    heat_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
