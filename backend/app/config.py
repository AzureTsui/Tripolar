import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tripolar:tripolar@localhost:5432/tripolar")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
