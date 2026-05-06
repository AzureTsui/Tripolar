# 数据库表结构

> 对应 `backend/app/models.py`，由 SQLAlchemy 自动建表。
> 已存在的数据库不会被 `create_all()` 自动加列，需要执行 `backend/schema.sql` 中的升级 SQL。

## ER 图

```
sources                     articles                         categories
┌──────────────────┐       ┌──────────────────────┐        ┌────────────────┐
│ id        INTEGER │       │ id            INTEGER │        │ id      INTEGER │
│ name   VARCHAR   │       │ title         VARCHAR │        │ name    VARCHAR │
│ url         TEXT  │       │ source        VARCHAR │        │ slug    VARCHAR │
│ type   VARCHAR   │       │ url              TEXT │        │ sort_order INT  │
│ trust_score FLOAT │       │ date        TIMESTAMP│        └────────────────┘
│ status VARCHAR   │       │ tags          VARCHAR│
│ last_fetched_at  │       │ summary          TEXT│
│ created_at       │       │ content_text     TEXT│
└──────────────────┘       │ content_status VARCHAR│
                           │ content_format VARCHAR│
                           │ content_provider VARCHAR│
                           │ content_hash   VARCHAR│
                           │ content_error     TEXT│
                           │ content_fetched_at   │
                           │ heat_score      FLOAT│
                           │ created_at           │
                           │ updated_at           │
                           └──────────────────────┘
```

注：`articles.source` 直接存来源名称字符串，不走外键关联。

## 表：sources

RSS 订阅源管理。

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | INTEGER | PK, INDEX | 自增 | 主键 |
| name | VARCHAR(255) | NOT NULL | | 来源名称 |
| url | TEXT | NOT NULL, UNIQUE | | RSS 地址 |
| type | VARCHAR(20) | | `'rss'` | 源类型 |
| trust_score | FLOAT | | `0.5` | 信任度评分 |
| status | VARCHAR(20) | | `'active'` | 状态 |
| last_fetched_at | TIMESTAMP | | NULL | 最后抓取时间 |
| created_at | TIMESTAMP | | `now()` | 创建时间 |

## 表：categories

文章分类。

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | INTEGER | PK, INDEX | 自增 | 主键 |
| name | VARCHAR(100) | NOT NULL | | 分类名（中文） |
| slug | VARCHAR(100) | NOT NULL, UNIQUE | | 英文标识 |
| sort_order | INTEGER | | `0` | 排序权重 |

当前种子数据：观点洞察 / 产品发布 / 行业报告 / 模型发布 / 论文 / 工具测评。

## 表：articles

聚合的文章数据。

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | INTEGER | PK, INDEX | 自增 | 主键 |
| title | VARCHAR(500) | NOT NULL | | 标题 |
| source | VARCHAR(200) | NOT NULL | | 来源名称 |
| url | TEXT | NOT NULL, UNIQUE | | 原文链接 |
| date | TIMESTAMP | | NULL | 文章发布时间 |
| tags | VARCHAR(500) | | `''` | 标签，逗号分隔 |
| summary | TEXT | | NULL | RSS 摘要 |
| content_text | TEXT | | NULL | 原文正文，默认保存 Markdown |
| content_format | VARCHAR(20) | | `'markdown'` | 正文格式 |
| content_status | VARCHAR(20) | | `'pending'` | 正文抓取状态 |
| content_error | TEXT | | NULL | 正文抓取失败原因 |
| content_fetched_at | TIMESTAMP | | NULL | 正文抓取完成时间 |
| content_provider | VARCHAR(50) | | NULL | 正文抓取 provider |
| content_hash | VARCHAR(64) | | NULL | 正文 SHA-256 |
| heat_score | FLOAT | | `0.0` | 热度评分 |
| created_at | TIMESTAMP | | `now()` | 入库时间 |
| updated_at | TIMESTAMP | | `now()` | 最后更新时间 |

## 正文状态流转

```
pending → queued → fetching → success
                  └────────→ failed → queued
```

## 数据流

```
sources.url → fetcher.py(feedparser) → articles 基础元数据
                                      ↓
                              Redis/RQ article_id
                                      ↓
                      content_worker.py 抓取正文 Markdown
                                      ↓
                         articles.content_text / 状态字段
                                      ↓
                              GET /api/articles/{id}
```
