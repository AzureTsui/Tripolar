from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import Article
from app.schemas import ArticleOut, ArticleDetail, PaginatedResponse, PaginationMeta

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.get("", response_model=PaginatedResponse)
def list_articles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    source: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Article)

    if source:
        query = query.filter(Article.source == source)

    total = query.count()
    rows = (
        query.order_by(Article.date.desc().nullslast(), Article.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    articles = [ArticleOut.model_validate(row) for row in rows]
    return PaginatedResponse(
        data=articles,
        meta=PaginationMeta(page=page, per_page=per_page, total=total),
    )


@router.get("/{article_id}", response_model=ArticleDetail)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(404, "Article not found")
    return ArticleDetail.model_validate(article)
