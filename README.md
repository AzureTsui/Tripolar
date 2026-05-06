# Tripolar - AI Product Radar

全球 AI 信息聚合平台。自动抓取、清洗、聚类、分析 AI 领域动态。

## 工程架构

### 技术栈总览

| 层级 | 技术 | 职责 |
|------|------|------|
| 前端 | React 18 + Vite + Tailwind CSS + React Router 6 | SPA 页面渲染、路由分发、API 数据消费 |
| 后端 | FastAPI + SQLAlchemy 2.0 + Pydantic | REST API 服务、ORM 映射、请求校验 |
| 数据库 | PostgreSQL 16 | 持久化存储、全文检索 |
| 抓取 | feedparser | RSS/Atom 订阅源解析与去重入库 |
| 部署 | systemd + uvicorn | 进程守护、ASGI 服务运行 |

### 系统架构图

```mermaid
flowchart TB
    subgraph 展示层
        direction LR
        A[Feed 文章流]
        B[ArticleDetail 详情]
        C[Sources 源管理]
        D[React Router 6]
        E[Tailwind CSS]
    end

    subgraph API 层
        direction LR
        F["/api/articles"]
        G["/api/categories"]
        H["/api/sources"]
        I[Pydantic Schemas]
    end

    subgraph 存储层
        J[(PostgreSQL 16)]
        K[SQLAlchemy ORM]
        L[(sources / categories / articles)]
    end

    subgraph 抓取层
        M[RSS/Atom 源]
        N[feedparser]
        O[fetcher.py]
        P[scripts/fetch_articles.py]
    end

    M --> N --> O --> P
    P --> J
    J --> K --> L
    L --> F & G & H
    F & G & H --> I
    I --> D
    D --> A & B & C
    E --- A & B & C
```

### 目录结构

```
tripolar/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 应用入口，中间件与路由注册
│   │   ├── config.py            # 环境变量配置（DB/CORS/API Key）
│   │   ├── database.py          # SQLAlchemy 引擎、Session、Base 声明
│   │   ├── models.py            # ORM 模型：Source、Category、Article
│   │   ├── schemas.py           # Pydantic 请求/响应模型
│   │   ├── routers/
│   │   │   ├── articles.py      # /api/articles 端点（列表 + 详情）
│   │   │   ├── categories.py    # /api/categories 端点
│   │   │   └── sources.py       # /api/sources 端点（CRUD）
│   │   └── services/
│   │       └── fetcher.py       # RSS 抓取核心逻辑（按 URL 去重）
│   ├── scripts/
│   │   └── fetch_articles.py    # 独立抓取脚本入口
│   ├── seed.py                  # 种子数据初始化（分类 + RSS 源）
│   ├── schema.sql               # 等价 DDL（参考用）
│   └── requirements.txt         # Python 依赖
├── frontend/
│   ├── src/
│   │   ├── main.jsx             # React 入口，BrowserRouter 挂载
│   │   ├── App.jsx              # 路由定义（/ /article/:id /sources）
│   │   ├── api/
│   │   │   └── client.js        # fetch 封装，对 /api/* 的统一请求层
│   │   ├── pages/
│   │   │   ├── Feed.jsx         # 文章流主页（分页 + 来源筛选）
│   │   │   ├── ArticleDetail.jsx # 文章详情页
│   │   │   └── Sources.jsx      # RSS 源管理页
│   │   └── components/
│   │       ├── Header.jsx       # 顶部导航栏
│   │       ├── ArticleCard.jsx  # 文章卡片
│   │       ├── CategoryFilter.jsx # 分类筛选按钮组
│   │       ├── Pagination.jsx   # 分页控件
│   │       └── Loading.jsx      # 加载动画
│   ├── index.html               # HTML 入口
│   ├── vite.config.js           # Vite 配置（React 插件 + API 代理）
│   ├── tailwind.config.js       # Tailwind 配置
│   └── package.json             # Node 依赖
├── config/
│   └── urls.txt                 # RSS 源 URL 清单（备选源参考）
├── deploy/
│   └── tripolar-web.service     # systemd 服务单元文件
├── docs/
│   ├── SCHEMA.md                # 数据库表结构说明
│   └── DATA_FLOW.md             # 数据流转与对象设计文档
└── README.md
```

### 数据模型

三张核心表，`articles.source` 为简单字符串，不与 `sources` 建立外键关联——源可删除而文章不丢失。

```mermaid
erDiagram
    sources {
        int id PK "自增主键"
        string name "来源名称"
        string url UK "RSS 地址，唯一"
        string type "源类型，默认 rss"
        float trust_score "信任度 0~1"
        string status "active / inactive"
        timestamp last_fetched_at "最后抓取时间"
        timestamp created_at "创建时间"
    }

    categories {
        int id PK "自增主键"
        string name "分类名（中文）"
        string slug UK "英文标识，唯一"
        int sort_order "排序权重"
    }

    articles {
        int id PK "自增主键"
        string title "文章标题"
        string source "来源名称（非外键）"
        string url UK "原文链接，唯一"
        timestamp date "发布时间"
        string tags "标签，逗号分隔"
        string summary "内容摘要"
        float heat_score "热度评分"
        timestamp created_at "入库时间"
        timestamp updated_at "更新时间"
    }
```

- **Source → Article**：通过 `articles.source` 字符串匹配 `sources.name`，松散耦合
- **Category**：独立分类表，当前用于种子数据标签体系（观点洞察 / 产品发布 / 行业报告 / 模型发布 / 论文 / 工具测评）

### API 端点

| 方法 | 路径 | 参数 | 响应 | 说明 |
|------|------|------|------|------|
| GET | `/api/health` | — | `{status: "ok"}` | 健康检查 |
| GET | `/api/articles` | `page`, `per_page`, `source` | `PaginatedResponse[ArticleOut]` | 文章分页列表，支持来源筛选 |
| GET | `/api/articles/{id}` | — | `ArticleDetail` | 文章详情（含摘要） |
| GET | `/api/categories` | — | `CategoryOut[]` | 全部分类 |
| GET | `/api/sources` | — | `SourceOut[]` | 全部 RSS 源 |
| POST | `/api/sources` | `SourceCreate` body | `SourceOut` (201) | 新增 RSS 源 |
| DELETE | `/api/sources/{id}` | — | 204 | 删除 RSS 源 |

分页响应结构：

```json
{
  "data": [{ "id": 1, "title": "...", "source": "36氪 AI", ... }],
  "meta": { "page": 1, "per_page": 20, "total": 150 }
}
```

### 数据流

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
