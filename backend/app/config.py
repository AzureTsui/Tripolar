import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tripolar:tripolar@localhost:5432/tripolar")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CONTENT_QUEUE_NAME = os.getenv("CONTENT_QUEUE_NAME", "article-content")
CRAWLER_CONFIG_PATH = os.getenv("CRAWLER_CONFIG_PATH", "config/crawler.yaml")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")
FIRECRAWL_ENABLED = os.getenv("FIRECRAWL_ENABLED", "false").lower() in {"1", "true", "yes", "on"}
