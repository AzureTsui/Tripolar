# Tripolar - AI Product Radar

全球 AI 信息聚合平台。自动抓取、清洗、聚类、分析 AI 领域动态。

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt

# 确保 PostgreSQL 运行中，创建数据库
createdb tripolar

# 初始化种子数据
python seed.py

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev     # 开发模式（自动代理 /api 到后端）
npm run build   # 生产构建
```

### RSS 抓取

```bash
cd backend
python scripts/fetch_articles.py
```

## 部署

见 `deploy/tripolar-web.service`。
