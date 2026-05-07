import feedparser
from datetime import datetime
from app.models import Source, Article
from app.services.content_queue import enqueue_article_content


def fetch_source(source: Source, db, enqueue_content: bool = True) -> int:
    """Fetch a single RSS source, return number of new articles."""
    feed = feedparser.parse(source.url)
    new_count = 0

    for entry in feed.entries:
        url = (entry.get("link") or "").strip()
        if not url:
            continue

        existing = db.query(Article).filter(Article.url == url).first()
        if existing:
            continue

        published = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6])

        article = Article(
            title=entry.get("title", "Untitled"),
            url=url,
            source=source.name,
            date=published,
            tags="",
            summary=entry.get("summary", "") or entry.get("description", ""),
        )
        db.add(article)
        db.flush()

        if enqueue_content:
            try:
                enqueue_article_content(article.id, db)
            except Exception:
                article.content_status = "pending"

        new_count += 1

    source.last_fetched_at = datetime.utcnow()
    db.commit()
    return new_count


def fetch_all_sources(db, enqueue_content: bool = True) -> dict:
    """Fetch all active sources, return summary dict."""
    sources = db.query(Source).filter(Source.status == "active").all()
    results = {}
    for source in sources:
        try:
            count = fetch_source(source, db, enqueue_content=enqueue_content)
            results[source.name] = count
        except Exception as e:
            db.rollback()
            results[source.name] = f"error: {e}"
    return results
