"""Standalone script: fetch RSS sources and store articles."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.services.fetcher import fetch_all_sources


def main():
    init_db()
    db = SessionLocal()
    try:
        results = fetch_all_sources(db)
        for name, count in results.items():
            status = "OK" if isinstance(count, int) else "ERR"
            print(f"[{status}] {name}: {count}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
