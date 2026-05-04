import feedparser
from datetime import datetime
from app.models import Source, Article


def fetch_source(source: Source, db) -> int:
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
        new_count += 1

    source.last_fetched_at = datetime.utcnow()
    db.commit()
    return new_count


def fetch_all_sources(db) -> dict:
    """Fetch all active sources, return summary dict."""
    sources = db.query(Source).filter(Source.status == "active").all()
    results = {}
    for source in sources:
        try:
            count = fetch_source(source, db)
            results[source.name] = count
        except Exception as e:
            db.rollback()
            results[source.name] = f"error: {e}"
    return results
