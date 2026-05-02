from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, ARRAY
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
    title = Column(Text, nullable=False)
    url = Column(Text, nullable=False, unique=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    content_text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    tags = Column(ARRAY(String), default=[])
    heat_score = Column(Float, default=0.0)
    published_at = Column(DateTime(timezone=True), nullable=True)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default="new")
