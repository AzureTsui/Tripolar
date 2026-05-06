# 数据流转与对象设计

## 一、整体数据流向

```mermaid
flowchart LR
    subgraph RSS抓取层
        A[RSS 源] -->|feedparser| B[fetcher.py]
        C[sources 表] --> B
    end

    subgraph 存储层
        B -->|写入基础元数据| D[(PostgreSQL articles)]
        D -->|SQLAlchemy| E[Article ORM]
    end

    subgraph 正文抓取层
        B -->|article_id| F[(Redis / RQ)]
        F --> G[content_worker.py]
        G --> H[Playwright]
        H --> I[Readability]
        I --> J[Markdownify]
        I -.失败或内容过短.-> K[Firecrawl 可选降级]
        J -->|Markdown| D
        K -->|Markdown| D
    end

    subgraph API层
        E -->|查询| L[FastAPI Routers]
        L -->|Pydantic| M[Response Schemas]
    end

    subgraph 展示层
        M -->|JSON| N[React Frontend]
        N -->|JSX| O[ArticleDetail]
    end
```

## 二、核心对象设计

### 2.1 ORM 模型

定义在 `backend/app/models.py`：

```
Source
  ├ id
  ├ name
  ├ url
  ├ type
  ├ trust_score
  ├ status
  ├ last_fetched_at
  └ created_at

Category
  ├ id
  ├ name
  ├ slug
  └ sort_order

Article
  ├ id
  ├ title
  ├ source
  ├ url
  ├ date
  ├ tags
  ├ summary
  ├ content_text
  ├ content_format
  ├ content_status
  ├ content_error
  ├ content_fetched_at
  ├ content_provider
  ├ content_hash
  ├ heat_score
  ├ created_at
  └ updated_at
```

`articles.source` 是来源名称字符串，不是外键；删除 RSS 源不会删除历史文章。

### 2.2 API Schema

定义在 `backend/app/schemas.py`：

| Schema | 用途 | 关键字段 |
|--------|------|----------|
| `SourceCreate` | 创建源请求体 | name, url, type |
| `SourceOut` | 源列表/详情响应 | id, name, url, trust_score, status, last_fetched_at |
| `CategoryOut` | 分类列表响应 | id, name, slug, sort_order |
| `ArticleOut` | 文章列表项 | id, title, source, url, date, summary, heat_score |
| `ArticleDetail` | 文章详情 | ArticleOut + content_text/content_status/content_format |
| `PaginatedResponse` | 分页包裹 | data[], meta{page, per_page, total} |

## 三、RSS 抓取流程

```mermaid
sequenceDiagram
    participant S as fetch_articles.py
    participant F as fetcher.py
    participant DB as PostgreSQL
    participant RSS as RSS 源
    participant Q as Redis/RQ

    S->>F: fetch_all_sources(db)
    F->>DB: 查询 status=active 的 Source
    DB-->>F: Source 列表
    loop 每个 Source
        F->>RSS: feedparser.parse(url)
        RSS-->>F: feed entries
        loop 每个 entry
            F->>DB: 按 URL 检查是否存在
            alt URL 不存在
                F->>DB: INSERT Article(content_status=pending)
                F->>Q: enqueue article_id
                F->>DB: content_status=queued
            else URL 已存在
                F->>F: 跳过
            end
        end
        F->>DB: UPDATE source.last_fetched_at
    end
    F-->>S: {source_name: new_count}
```

关键逻辑：
- 按 `articles.url` 去重，保证重复执行不会重复入库。
- 队列失败不会阻断 RSS 入库，文章保持 `pending`，可后续补投。
- `fetcher.py` 只负责发现链接与投递任务，不负责同步抓正文。

## 四、正文抓取流程

```mermaid
sequenceDiagram
    participant W as content_worker.py
    participant Q as Redis/RQ
    participant DB as PostgreSQL
    participant P as Playwright
    participant R as Readability
    participant M as Markdownify
    participant F as Firecrawl

    W->>Q: 消费 article_id
    W->>DB: 查询 Article
    W->>DB: content_status=fetching
    W->>P: 打开 article.url
    P-->>R: 渲染后 HTML
    R-->>M: 正文 HTML
    alt 内容有效
        M-->>DB: content_text Markdown
        W->>DB: content_status=success
    else 抽取失败或内容过短且启用 Firecrawl
        W->>F: scrape_url(url)
        F-->>DB: content_text Markdown
        W->>DB: content_status=success
    else 失败
        W->>DB: content_status=failed, content_error=错误信息
    end
```

## 五、脚本入口

| 脚本 | 用途 |
|------|------|
| `backend/scripts/fetch_articles.py` | 抓取 RSS 新文章并投递正文任务 |
| `backend/scripts/content_worker.py` | 启动 RQ worker 消费正文任务 |
| `backend/scripts/enqueue_pending_content.py` | 给历史或失败文章补投正文任务 |

## 六、配置流转

```text
.env
  ├ DATABASE_URL
  ├ REDIS_URL
  ├ CONTENT_QUEUE_NAME
  ├ CRAWLER_CONFIG_PATH
  ├ FIRECRAWL_API_KEY
  └ FIRECRAWL_ENABLED

config/crawler.yaml
  ├ queue
  ├ crawler
  ├ fallback
  └ domains
```

`backend/app/services/crawler_config.py` 会读取 `config/crawler.yaml`，并在配置文件缺失、格式错误或字段缺失时使用默认值。

## 七、API 到前端

```text
GET /api/articles/{id}
  ↓
ArticleDetail
  ├ content_text
  ├ content_format
  ├ content_status
  ├ content_fetched_at
  └ content_provider
  ↓
frontend/src/pages/ArticleDetail.jsx
```

当前前端按纯文本展示 `content_text`。如果后续需要更好展示 Markdown 表格和 LaTeX，可在前端加入 `react-markdown`、`remark-gfm`、`remark-math`、`rehype-katex`。
