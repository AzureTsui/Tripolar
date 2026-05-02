from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Article, Source
from app.schemas import ArticleOut, ArticleDetail, PaginatedResponse, PaginationMeta

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.get("", response_model=PaginatedResponse)
def list_articles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    source_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Article, Source.name.label("source_name")).outerjoin(
        Source, Article.source_id == Source.id
    )

    if category_id:
        query = query.filter(Article.category_id == category_id)
    if source_id:
        query = query.filter(Article.source_id == source_id)

    total = query.count()
    rows = (
        query.order_by(Article.published_at.desc().nullslast())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    articles = []
    for article, source_name in rows:
        d = ArticleOut.model_validate(article)
        d.source_name = source_name
        articles.append(d)

    return PaginatedResponse(
        data=articles,
        meta=PaginationMeta(page=page, per_page=per_page, total=total),
    )


@router.get("/{article_id}", response_model=ArticleDetail)
def get_article(article_id: int, db: Session = Depends(get_db)):
    row = (
        db.query(Article, Source.name.label("source_name"))
        .outerjoin(Source, Article.source_id == Source.id)
        .filter(Article.id == article_id)
        .first()
    )
    if not row:
        raise HTTPException(404, "Article not found")
    article, source_name = row
    d = ArticleDetail.model_validate(article)
    d.source_name = source_name
    return d
