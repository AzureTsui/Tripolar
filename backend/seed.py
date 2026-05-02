"""Seed initial categories and sources."""
from app.database import SessionLocal, init_db
from app.models import Category, Source

CATEGORIES = [
    ("观点洞察", "opinion"),
    ("产品发布", "product"),
    ("行业报告", "report"),
    ("模型发布", "model"),
    ("论文", "paper"),
    ("工具测评", "tool"),
]

SOURCES = [
    {"name": "36氪 AI", "url": "https://36kr.com/feed", "type": "rss"},
    {"name": "机器之心", "url": "https://www.jiqizhixin.com/rss", "type": "rss"},
    {"name": "Hacker News", "url": "https://hnrss.org/frontpage", "type": "rss"},
    {"name": "ArXiv ML", "url": "http://export.arxiv.org/rss/cs.LG", "type": "rss"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed", "type": "rss"},
]


def seed():
    init_db()
    db = SessionLocal()
    try:
        for name, slug in CATEGORIES:
            if not db.query(Category).filter(Category.slug == slug).first():
                db.add(Category(name=name, slug=slug))

        for s in SOURCES:
            if not db.query(Source).filter(Source.url == s["url"]).first():
                db.add(Source(**s))

        db.commit()
        print("Seed data inserted.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
