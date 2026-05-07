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
│   │   │   ├── articles.py      # /api/articles 端点（列表 + 详情）
│   │   │   ├── categories.py    # /api/categories 端点
│   │   │   ├── sources.py       # /api/sources 端点（CRUD）
│   │   │   └── ai_tools.py      # /api/tools 端点（列表 + 详情 + 元数据）
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
│   ├── seed.py                  # 种子数据初始化（分类 + RSS 源 + AI 工具元数据）
│   └── requirements.txt         # Python 依赖
├── sql/
│   ├── 01_schema.sql             # 全量 DDL（RSS 核心 + AI 工具目录，6 张表）
│   ├── 02_seed_core.sql          # RSS 核心种子数据
│   └── 03_seed_ai_tools.sql      # AI 视频工具种子数据（100 条）
├── frontend/
├── config/
│   ├── urls.txt
│   └── crawler.yaml
├── deploy/
├── docs/
│   ├── DATABASE.md                           # 数据库总览文档（DDL + 设计 + 运维）
│   └── AI视频工具全量清单 (100个).md           # AI 视频工具原始数据源
├── scripts/
│   └── migrate_to_new_schema.py               # 旧表 → 新三表迁移脚本（历史参考）
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

### AI 工具目录（三表设计）

产品类型回答"它是什么"，使用场景回答"用户用它做什么"。

```mermaid
erDiagram
    ai_product_types {
        int id PK "自增主键"
        string name "产品类型名（如 AI视频工具）"
        string slug UK "唯一标识，用于 URL"
        string description "类型说明"
        int sort_order "排序权重"
        boolean is_active "是否启用"
    }

    ai_use_cases {
        int id PK "自增主键"
        string name "使用场景名（如 视频生成）"
        string slug UK "唯一标识，用于 URL"
        string description "场景说明"
        int sort_order "排序权重"
        boolean is_active "是否启用"
    }

    ai_tools {
        int id PK "自增主键"
        string name "产品名称"
        string slug UK "URL 友好标识"
        string company "所属公司"
        int product_type_id FK "→ ai_product_types.id"
        int primary_use_case_id FK "→ ai_use_cases.id"
        string short_description "一句话简介"
        string overview "详细介绍"
        string website_url "官网"
        string logo_url "Logo"
        string status "active / inactive"
        timestamp created_at "创建时间"
        timestamp updated_at "更新时间"
    }

    ai_product_types ||--o{ ai_tools : "1 个类型 → N 个产品"
    ai_use_cases ||--o{ ai_tools : "1 个场景 → N 个产品"
```

当前数据规模：5 个产品类型 / 21 个使用场景 / 100 个 AI 视频工具。

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
| GET | `/api/tools` | `page`, `per_page`, `product_type_id`, `use_case_id`, `search` | `PaginatedResponse[AIToolOut]` | AI 工具分页列表，支持类型/场景筛选和搜索 |
| GET | `/api/tools/{id}` | — | `AIToolDetail` | AI 工具详情 |
| GET | `/api/tools/meta/product-types` | — | `AIToolProductTypeOut[]` | 全部产品类型 |
| GET | `/api/tools/meta/use-cases` | — | `AIToolUseCaseOut[]` | 全部使用场景 |

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

## 数据流

端到端流程，从 RSS 抓取到前端展示：

```mermaid
sequenceDiagram
    participant Cron as 定时任务 / 手动
    participant Script as fetch_articles.py
    participant Fetcher as fetcher.py
    participant Feed as feedparser
    participant RSS as RSS/Atom 源
    participant DB as PostgreSQL
    participant API as FastAPI Routers
    participant React as React SPA

    Cron->>Script: 触发抓取
    Script->>Fetcher: fetch_all_sources(db)
    Fetcher->>DB: 查询 status=active 的 Source 列表
    DB-->>Fetcher: Source[]
    loop 遍历每个 Source
        Fetcher->>Feed: feedparser.parse(url)
        Feed->>RSS: HTTP GET
        RSS-->>Feed: XML/Atom
        Feed-->>Fetcher: 解析后的 entries
        loop 遍历每个 entry
            Fetcher->>DB: 按 URL 查重
            alt URL 不存在
                Fetcher->>DB: INSERT Article
            else URL 已存在
                Fetcher->>Fetcher: 跳过
            end
        end
        Fetcher->>DB: UPDATE source.last_fetched_at
    end
    Fetcher-->>Script: {source_name: new_count}

    React->>API: GET /api/articles?page=1
    API->>DB: SELECT * FROM articles ORDER BY date DESC
    DB-->>API: Article[]
    API->>API: Pydantic 序列化为 ArticleOut[]
    API-->>React: PaginatedResponse JSON
    React->>React: 渲染 Feed 页面
```

抓取策略要点：
- **按 URL 去重**：同一 URL 不会重复入库，保证幂等执行
- **不覆盖更新**：已入库文章不会被后续抓取修改内容
- **独立脚本**：`fetch_articles.py` 不依赖 Web 进程，可由 cron/systemd timer 调度

## 项目启动

本项目采用前后端分离架构，开发或部署时需要**同时运行后端和前端**两个服务：

| 服务 | 技术栈 | 端口 | 说明 |
|------|--------|------|------|
| 后端 API | FastAPI + uvicorn | 8000 | 提供 REST API，前端通过代理转发请求 |
| 前端页面 | React + Vite | 5173 | SPA 页面渲染，开发模式代理 `/api` → `:8000` |

### 1. 环境准备

```bash
# 确保 PostgreSQL 16 运行中，创建数据库（首次）
createdb tripolar
```

### 2. 后端启动

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 初始化数据库（二选一）
python seed.py                                                  # Python 方式
# psql -U tripolar -d tripolar -f sql/01_schema.sql             # SQL 方式（三脚本依次执行）
# psql -U tripolar -d tripolar -f sql/02_seed_core.sql
# psql -U tripolar -d tripolar -f sql/03_seed_ai_tools.sql

# 启动 API 服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 前端启动

```bash
cd frontend
npm install
npm run dev     # 开发模式，热更新 + API 代理（Vite proxy /api → localhost:8000）
```

### 4. RSS 抓取（手动触发）

```bash
cd backend
source venv/bin/activate   # Windows: venv\Scripts\activate
python scripts/fetch_articles.py
```

## 生产部署

### Backend — systemd 服务

```bash
sudo cp deploy/tripolar-web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now tripolar-web
```

正文 worker 建议作为独立进程部署，与 Web 服务分别守护。

### Frontend — 静态文件

前端构建为纯静态文件，由 Nginx 或 uvicorn 托管：

```bash
cd frontend
npm run build       # 输出到 dist/
```

**方式一：Nginx 托管**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/tripolar/frontend/dist;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
    }

    location / {
        try_files $uri /index.html;   # SPA fallback
    }
}
```

**方式二：FastAPI 直接托管**

```python
# 在 app/main.py 中添加静态文件挂载
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")
```

### 正文抓取 Worker

新文章会先写入 `articles`，随后投递 `article_id` 到 Redis/RQ 正文抓取队列。Redis 不可用时入库不会失败，文章保持 `content_status = 'pending'`。

```bash
# 确保 Redis 运行中
cd backend
python scripts/content_worker.py     # 消费 article-content 队列
```

worker 使用 Playwright 动态渲染页面 → Readability 提取正文 → Markdownify 转 Markdown → 写回 `articles.content_text`。

### 历史文章补抓

```bash
cd backend
python scripts/enqueue_pending_content.py --limit 10
python scripts/enqueue_pending_content.py --status failed --limit 20
```

## 已有数据库升级

如果数据库已存在但缺少正文抓取相关列，手动执行：

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

1. Playwright 打开原文链接，模拟真实浏览器环境
2. Readability 提取正文 HTML，过滤导航、广告、侧边栏
3. Markdownify 转 Markdown，保留表格、代码块和公式
4. 本地抽取失败或内容过短时，启用 Firecrawl 降级（需配置 `FIRECRAWL_ENABLED=true`）
5. Cloudflare / 验证码页面记录 `failed`，不阻塞 RSS 抓取

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATABASE_URL` | `postgresql://tripolar:tripolar@localhost:5432/tripolar` | PostgreSQL 连接串 |
| `CORS_ORIGINS` | `http://localhost:5173` | 前端跨域来源 |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis/RQ 连接串 |
| `CONTENT_QUEUE_NAME` | `article-content` | 正文抓取队列名称 |
| `FIRECRAWL_API_KEY` | — | Firecrawl API Key（可选） |
| `FIRECRAWL_ENABLED` | `false` | 是否启用 Firecrawl 降级 |
| `DEEPSEEK_API_KEY` | — | DeepSeek API 密钥（可选） |
