from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Generic, TypeVar


# ============================================================
# RSS 资讯核心
# ============================================================

class SourceCreate(BaseModel):
    name: str
    url: str
    type: str = "rss"


class SourceOut(BaseModel):
    id: int
    name: str
    url: str
    type: str
    trust_score: float
    status: str
    last_fetched_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    sort_order: int

    class Config:
        from_attributes = True


class ArticleOut(BaseModel):
    id: int
    title: str
    source: str
    url: str
    date: Optional[datetime] = None
    tags: str = ""
    summary: Optional[str] = None
    heat_score: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ArticleDetail(ArticleOut):
    content_text: Optional[str] = None


T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    meta: PaginationMeta


# ============================================================
# AI 工具目录
# ============================================================

class AIToolProductTypeOut(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    sort_order: int = 0

    class Config:
        from_attributes = True


class AIToolUseCaseOut(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    sort_order: int = 0

    class Config:
        from_attributes = True


class AIToolOut(BaseModel):
    id: int
    name: str
    slug: str
    company: Optional[str] = None
    product_type: Optional[AIToolProductTypeOut] = None
    use_case: Optional[AIToolUseCaseOut] = None
    short_description: Optional[str] = None
    overview: Optional[str] = None
    website_url: Optional[str] = None
    logo_url: Optional[str] = None
    status: str = "active"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AIToolDetail(AIToolOut):
    updated_at: Optional[datetime] = None
