# Tripolar - AI Product Radar

全球 AI 信息聚合平台。自动抓取 RSS/Atom 订阅源，去重写入 PostgreSQL，并异步抓取原文正文保存为 Markdown。

## 工程架构

### 技术栈总览

| 层级 | 技术 | 职责 |
|------|------|------|
| 前端 | React 18 + Vite + Tailwind CSS + React Router 6 | SPA 页面渲染、路由分发、API 数据消费 |
| 后端 | FastAPI + SQLAlchemy 2.0 + Pydantic | REST API 服务、ORM 映射、请求校验 |
| 数据库 | PostgreSQL 16 | RSS 元数据与文章正文持久化 |
| RSS 抓取 | feedparser | RSS/Atom 订阅源解析与按 URL 去重入库 |
| 正文抓取 | Redis + RQ + Playwright + Readability + Markdownify | 解耦正文爬取、动态渲染、正文提取、Markdown 存储 |
| 可选降级 | Firecrawl | 本地抽取失败或内容过短时转换网页为 Markdown |
| 部署 | systemd + uvicorn | 进程守护、ASGI 服务运行 |

### 系统架构图

```mermaid
flowchart TB
    subgraph 展示层
        A[Feed 文章流]
        B[ArticleDetail 详情]
        C[Sources 源管理]
    end

    subgraph API层
        D[FastAPI Routers]
        E[Pydantic Schemas]
    end

    subgraph 存储层
        F[(PostgreSQL)]
        G[(sources / categories / articles)]
    end

    subgraph RSS抓取层
        H[RSS/Atom 源]
        I[feedparser]
        J[fetcher.py]
        K[scripts/fetch_articles.py]
    end

    subgraph 正文抓取层
        L[(Redis / RQ)]
        M[scripts/content_worker.py]
        N[Playwright]
        O[Readability]
        P[Markdownify]
        Q[Firecrawl 可选降级]
    end

    H --> I --> J --> K --> F
    J --> L --> M --> N --> O --> P --> F
    O -.内容过短或失败.-> Q -.Markdown.-> F
    F --> G --> D --> E --> A & B & C
```

### 目录结构

```
tripolar/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routers/
│   │   └── services/
│   │       ├── fetcher.py
│   │       ├── crawler_config.py
│   │       ├── content_queue.py
│   │       ├── content_extractor.py
│   │       └── content_fetcher.py
│   ├── scripts/
│   │   ├── fetch_articles.py
│   │   ├── content_worker.py
│   │   └── enqueue_pending_content.py
│   ├── seed.py
│   ├── schema.sql
│   └── requirements.txt
├── frontend/
├── config/
│   ├── urls.txt
│   └── crawler.yaml
├── deploy/
├── docs/
└── README.md
```

## 数据模型

三张核心表，`articles.source` 为来源名称字符串，不与 `sources` 建立外键关联。

```mermaid
erDiagram
    sources {
        int id PK
        string name
        string url UK
        string type
        float trust_score
        string status
        timestamp last_fetched_at
        timestamp created_at
    }

    categories {
        int id PK
        string name
        string slug UK
        int sort_order
    }

    articles {
        int id PK
        string title
        string source
        string url UK
        timestamp date
        string tags
        string summary
        string content_format
        string content_status
        string content_provider
        string content_hash
        text content_text
        text content_error
        timestamp content_fetched_at
        float heat_score
        timestamp created_at
        timestamp updated_at
    }
```

正文抓取状态：

| 状态 | 说明 |
|------|------|
| pending | 已入库但尚未成功入队或等待补投 |
| queued | 已投递到 Redis/RQ 队列 |
| fetching | worker 正在抓取正文 |
| success | 正文抓取成功并写入 `content_text` |
| failed | 正文抓取失败，错误写入 `content_error` |

## API 端点

| 方法 | 路径 | 参数 | 响应 | 说明 |
|------|------|------|------|------|
| GET | `/api/health` | — | `{status: "ok"}` | 健康检查 |
| GET | `/api/articles` | `page`, `per_page`, `source` | `PaginatedResponse[ArticleOut]` | 文章分页列表，支持来源筛选 |
| GET | `/api/articles/{id}` | — | `ArticleDetail` | 文章详情，包含正文抓取字段 |
| GET | `/api/categories` | — | `CategoryOut[]` | 全部分类 |
| GET | `/api/sources` | — | `SourceOut[]` | 全部 RSS 源 |
| POST | `/api/sources` | `SourceCreate` body | `SourceOut` | 新增 RSS 源 |
| DELETE | `/api/sources/{id}` | — | 204 | 删除 RSS 源 |

## 配置

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| DATABASE_URL | `postgresql://tripolar:tripolar@localhost:5432/tripolar` | PostgreSQL 连接串 |
| CORS_ORIGINS | `http://localhost:5173` | 前端跨域来源 |
| REDIS_URL | `redis://localhost:6379/0` | Redis/RQ 连接串 |
| CONTENT_QUEUE_NAME | `article-content` | 正文抓取队列名称 |
| CRAWLER_CONFIG_PATH | `config/crawler.yaml` | 爬虫配置文件路径 |
| FIRECRAWL_API_KEY | 空 | Firecrawl API Key |
| FIRECRAWL_ENABLED | `false` | 是否启用 Firecrawl 降级 |

### `config/crawler.yaml`

该文件统一配置正文抓取、队列和域名策略。配置缺失或填写错误时，后端会使用默认值兜底。

```yaml
queue:
  name: article-content
  retry_max: 3

crawler:
  provider: playwright_readability
  timeout_ms: 30000
  wait_until: domcontentloaded
  user_agent: "TripolarBot/0.1"
  min_content_chars: 500
  max_content_chars: 200000
  scroll_steps: 2

fallback:
  firecrawl_enabled: false
  use_firecrawl_when_content_short: true

domains:
  arxiv.org:
    min_content_chars: 300
  news.ycombinator.com:
    skip: true
```

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

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
npm run dev
npm run build
```

### RSS 抓取

```bash
cd backend
python scripts/fetch_articles.py
```

新文章会先写入 `articles`，随后尝试投递 `article_id` 到 Redis/RQ 正文抓取队列。Redis 不可用时，RSS 入库不会失败，文章会保持 `content_status = 'pending'`。

### 正文抓取 Worker

先确保 Redis 正在运行，然后启动 worker：

```bash
cd backend
python scripts/content_worker.py
```

worker 会消费 `article-content` 队列，使用 Playwright 动态渲染页面，Readability 提取正文，再将 Markdown 写回 `articles.content_text`。

### 历史文章补抓

```bash
cd backend
python scripts/enqueue_pending_content.py --limit 10
python scripts/enqueue_pending_content.py --status failed --limit 20
```

## 已有数据库升级

如果数据库已经存在，`Base.metadata.create_all()` 不会自动给 `articles` 加新列。请手动执行：

```sql
ALTER TABLE articles
    ADD COLUMN IF NOT EXISTS content_text TEXT,
    ADD COLUMN IF NOT EXISTS content_format VARCHAR(20) DEFAULT 'markdown',
    ADD COLUMN IF NOT EXISTS content_status VARCHAR(20) DEFAULT 'pending',
    ADD COLUMN IF NOT EXISTS content_error TEXT,
    ADD COLUMN IF NOT EXISTS content_fetched_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS content_provider VARCHAR(50),
    ADD COLUMN IF NOT EXISTS content_hash VARCHAR(64);
```

## 正文抓取策略

1. 默认使用 Playwright 打开原文链接，模拟真实浏览器环境。
2. 使用 Readability 提取正文 HTML，过滤导航、广告、侧边栏和页脚。
3. 使用 Markdownify 转 Markdown，尽量保留表格、代码块和公式文本。
4. 如果本地抽取失败或内容过短，且配置启用了 Firecrawl，则调用 Firecrawl 降级。
5. 对 Cloudflare 或验证码页面，默认记录 `failed`，不阻塞 RSS 抓取；可后续按域名配置 Firecrawl 或付费 Scraping Browser。

## 验证建议

```bash
cd backend
python -m py_compile app/config.py app/models.py app/schemas.py app/services/*.py scripts/*.py
```

然后按顺序验证：

1. 执行数据库升级 SQL。
2. 启动 Redis。
3. 执行 `python scripts/fetch_articles.py`。
4. 执行 `python scripts/content_worker.py`。
5. 请求 `GET /api/articles/{id}`，确认返回 `content_text`、`content_status`、`content_format`。
6. 抽查普通新闻、中文媒体、厂商博客、arXiv、含表格或 LaTeX 的页面。

## 部署

见 `deploy/tripolar-web.service`。正文 worker 建议作为独立进程部署，并与 Web 服务分别守护。
