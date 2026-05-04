from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


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


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int


class PaginatedResponse(BaseModel):
    data: List[ArticleOut]
    meta: PaginationMeta
