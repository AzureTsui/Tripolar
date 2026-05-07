"""独立脚本：补投等待正文抓取的文章。"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import or_

from app.database import SessionLocal
from app.models import Article
from app.services.content_queue import enqueue_article_content


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--status", choices=["pending", "failed", "all"], default="pending")
    return parser.parse_args()


def main():
    args = parse_args()
    db = SessionLocal()
    enqueued = 0

    try:
        query = db.query(Article)
        if args.status == "all":
            query = query.filter(or_(Article.content_text.is_(None), Article.content_status != "success"))
        else:
            query = query.filter(or_(Article.content_status == args.status, Article.content_text.is_(None)))

        articles = query.order_by(Article.created_at.asc()).limit(args.limit).all()

        for article in articles:
            try:
                if enqueue_article_content(article.id, db):
                    enqueued += 1
            except Exception as error:
                article.content_status = "pending"
                article.content_error = str(error)[:2000]

        db.commit()
        print(f"Enqueued {enqueued} article content jobs")
    finally:
        db.close()


if __name__ == "__main__":
    main()
