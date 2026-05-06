from redis import Redis
from rq import Queue, Retry

from app.config import CONTENT_QUEUE_NAME, REDIS_URL
from app.services.crawler_config import load_crawler_config
from app.models import Article


SKIP_STATUSES = {"queued", "fetching", "success"}


def _queue_name() -> str:
    config = load_crawler_config()
    return config.get("queue", {}).get("name") or CONTENT_QUEUE_NAME


def _retry_config() -> Retry:
    config = load_crawler_config()
    retry_max = int(config.get("queue", {}).get("retry_max", 3))
    return Retry(max=retry_max)


def get_content_queue() -> Queue:
    redis_conn = Redis.from_url(REDIS_URL)
    return Queue(_queue_name(), connection=redis_conn)


def enqueue_article_content(article_id: int, db=None) -> bool:
    if db is not None:
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article or article.content_status in SKIP_STATUSES:
            return False

    queue = get_content_queue()
    job_id = f"article-content:{article_id}"

    if queue.fetch_job(job_id):
        return False

    queue.enqueue(
        "app.services.content_fetcher.fetch_article_content",
        article_id,
        job_id=job_id,
        retry=_retry_config(),
    )

    if db is not None:
        article.content_status = "queued"
        db.flush()

    return True
