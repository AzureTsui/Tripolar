from datetime import datetime
from hashlib import sha256

from app.database import SessionLocal
from app.models import Article
from app.services.content_extractor import extract_article_content


def fetch_article_content(article_id: int) -> bool:
    db = SessionLocal()
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return False
        if article.content_status == "success" and article.content_text:
            return False

        article.content_status = "fetching"
        article.content_error = None
        db.commit()

        try:
            content = extract_article_content(article.url)
            article.content_text = content.text
            article.content_format = content.format
            article.content_provider = content.provider
            article.content_hash = sha256(content.text.encode("utf-8")).hexdigest()
            article.content_fetched_at = datetime.utcnow()
            article.content_status = "success"
            article.content_error = None
            db.commit()
            return True
        except Exception as error:
            db.rollback()
            article = db.query(Article).filter(Article.id == article_id).first()
            if article:
                article.content_status = "failed"
                article.content_error = str(error)[:2000]
                db.commit()
            raise
    finally:
        db.close()
