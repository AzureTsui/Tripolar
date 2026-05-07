"""独立脚本：启动文章正文抓取 worker。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from redis import Redis
from rq import Worker

from app.config import REDIS_URL
from app.services.content_queue import get_content_queue


def main():
    redis_conn = Redis.from_url(REDIS_URL)
    queue = get_content_queue()
    worker = Worker([queue], connection=redis_conn)
    worker.work()


if __name__ == "__main__":
    main()
