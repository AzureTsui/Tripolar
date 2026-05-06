from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
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
    heat_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ============================================================
# AI 工具目录（三表设计）
# ============================================================

class AIToolProductType(Base):
    __tablename__ = "ai_product_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(120), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    tools = relationship("AITool", back_populates="product_type")


class AIToolUseCase(Base):
    __tablename__ = "ai_use_cases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(120), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    tools = relationship("AITool", back_populates="use_case")


class AITool(Base):
    __tablename__ = "ai_tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(120), unique=True, nullable=False)
    company = Column(String(100), nullable=True)
    product_type_id = Column(Integer, ForeignKey("ai_product_types.id"), nullable=False)
    primary_use_case_id = Column(Integer, ForeignKey("ai_use_cases.id"), nullable=False)
    short_description = Column(String(200), nullable=True)
    overview = Column(Text, nullable=True)
    website_url = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)
    status = Column(String(30), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    product_type = relationship("AIToolProductType", back_populates="tools")
    use_case = relationship("AIToolUseCase", back_populates="tools")
