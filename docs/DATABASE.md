# Tripolar 数据库文档

> 最后更新: 2026-05-07  
> 数据库: PostgreSQL 16 / 库名: tripolar

## 一、总体结构

项目包含两套表，分别服务于不同的业务域：

```
┌─ RSS 资讯核心 ─────────────────────────────┐
│  sources      RSS 订阅源                   │
│  categories   文章分类                     │
│  articles     聚合文章                     │
├─ AI 工具目录 ──────────────────────────────┤
│  ai_product_types    产品类型（它是什么？）     │
│  ai_use_cases        使用场景（用户用它做什么？）│
│  ai_tools            AI 工具本体             │
└────────────────────────────────────────────┘
```

## 二、RSS 资讯核心

### ER 图

```
sources                     articles                    categories
┌──────────────────┐       ┌──────────────────┐       ┌────────────────┐
│ id        INTEGER │       │ id        INTEGER │       │ id      INTEGER │
│ name   VARCHAR(255)│      │ title  VARCHAR(500)│      │ name VARCHAR(100)│
│ url         TEXT  │       │ source VARCHAR(200)│      │ slug VARCHAR(100)│
│ type   VARCHAR(20) │       │ url         TEXT  │       │ sort_order INT  │
│ trust_score FLOAT │       │ date    TIMESTAMP │       └────────────────┘
│ status VARCHAR(20) │       │ tags  VARCHAR(500)│
│ last_fetched_at   │       │ summary      TEXT │
│ created_at        │       │ heat_score  FLOAT │
└──────────────────┘       │ created_at         │
                           │ updated_at         │
                           └──────────────────┘
注：articles.source 直接存来源名称字符串，不走外键关联。
```

### 数据流

```
sources.url → fetcher.py (feedparser) → articles (INSERT)
                                              ↓
                                    GET /api/articles
                                              ↓
                                    React 前端展示
```

### 源表与文章表的设计要点

- **按 URL 去重**：articles.url UNIQUE，同一篇文章不会重复入库
- **不修改已有文章**：RSS 源更新内容时不会覆盖已入库数据
- **source 为字符串**：articles.source 不设外键，降低写入耦合度

### 种子数据

6 个分类：观点洞察 / 产品发布 / 行业报告 / 模型发布 / 论文 / 工具测评

5 个 RSS 源：36氪 AI / 机器之心 / Hacker News / ArXiv ML / TechCrunch AI

---

## 三、AI 工具目录

### 设计原则

三张表，两个核心维度：

| 表 | 回答的问题 | 示例 |
|---|---|---|
| `ai_product_types` | "它是什么类型的工具？" | AI视频工具、AI编程工具 |
| `ai_use_cases` | "用户用它做什么任务？" | 视频生成、电商视频制作 |
| `ai_tools` | 产品本体信息 | LibTV、绘蛙AI视频 |

### 为什么要分离分类字段

旧设计中 `track`、`feature_tags` 是自由文本，会带来问题：

```
AI视频 ←→ AI 视频 ←→ AI视频工具 ←→ 视频AI    （同一含义，多种写法）
```

通过外键关联到 `ai_product_types` 和 `ai_use_cases`，分类名称统一，筛选稳定，数据不会因手写变脏。

### ER 图

```
ai_product_types            ai_tools                  ai_use_cases
┌──────────────────┐       ┌─────────────────────┐  ┌──────────────────┐
│ id        SERIAL  │       │ id           SERIAL  │  │ id        SERIAL  │
│ name  VARCHAR(100) │      │ name     VARCHAR(100) │  │ name  VARCHAR(100) │
│ slug  VARCHAR(120) │──FK──│ slug     VARCHAR(120) │  │ slug  VARCHAR(120) │
│ description  TEXT │       │ company  VARCHAR(100) │  │ description  TEXT │
│ sort_order   INT  │       │ product_type_id  INT │──│ sort_order   INT  │
│ is_active  BOOL  │       │ primary_use_case_id──FK─│ is_active  BOOL  │
└──────────────────┘       │ short_description    │  └──────────────────┘
                           │ overview       TEXT  │
                           │ website_url          │
                           │ status   VARCHAR(30) │
                           └─────────────────────┘
关系：
  一个产品类型 → 多个 AI 产品
  一个使用场景 → 多个 AI 产品
  一个 AI 产品 → 一个主产品类型 + 一个主使用场景
```

### MVP 阶段的设计取舍

**保留的简化项：**

| 设计决策 | 原因 |
|---|---|
| `company` 用字符串不拆表 | 公司不是当前核心筛选维度，拆表增加维护成本 |
| 每个产品只一个主使用场景 | 覆盖多数用户的搜索心智，后续加中间表扩展 |
| 不设 `feature_tags` | 自由标签统计困难、去重困难，暂时写入 `overview` |
| 不设 `tracks` 赛道表 | 赛道偏市场分析，对用户找工具边界模糊，后期补 |

**后续演进路径：**

```
第 1 阶段（当前）：ai_tools + ai_product_types + ai_use_cases
第 2 阶段：增加 ai_tool_use_cases，支持一个产品多个使用场景
第 3 阶段：增加 ai_tags / ai_tool_tags，支持特性标签
第 4 阶段：增加 companies，公司结构化
第 5 阶段：增加 market_tracks，支持赛道分析和榜单
```

---

## 四、初始化流程

### 首次建库

```sql
-- 以 postgres 超级用户执行
CREATE USER tripolar WITH PASSWORD 'tripolar';
CREATE DATABASE tripolar OWNER tripolar;
```

### 建表 + 种子数据

```bash
cd backend

# 方式一：Python（自动建表 + 种子）
python seed.py

# 方式二：纯 SQL
psql -U tripolar -d tripolar -f sql/01_schema.sql
psql -U tripolar -d tripolar -f sql/02_seed_core.sql
psql -U tripolar -d tripolar -f sql/03_seed_ai_tools.sql
```

### 抓取文章

```bash
cd backend
python scripts/fetch_articles.py
```

### 重置数据库

```sql
DROP DATABASE tripolar;
CREATE DATABASE tripolar OWNER tripolar;
-- 然后重新执行 seed
```

---

## 五、连接信息

```
DATABASE_URL=postgresql://tripolar:tripolar@localhost:5432/tripolar
```

`.env` 文件位置：`backend/.env`

---

## 六、当前限制

- 没有迁移工具（如 Alembic），改模型后需手动同步表结构
- `create_all` 不会删数据，也不会改已有字段类型
- 建议后续引入 Alembic：`pip install alembic && alembic init alembic`

---

## 七、相关文件索引

| 路径 | 用途 |
|---|---|
| `sql/01_schema.sql` | 全量 DDL（所有表的 CREATE） |
| `sql/02_seed_core.sql` | RSS 核心种子（categories + sources） |
| `sql/03_seed_ai_tools.sql` | AI 视频工具种子（100 条 + 产品类型 + 使用场景） |
| `backend/app/database.py` | SQLAlchemy 引擎和 Base 定义 |
| `backend/seed.py` | Python 初始化脚本（自动建表 + 写种子） |
| `docs/AI视频工具全量清单 (100个).md` | 原始数据源 |
| `scripts/migrate_to_new_schema.py` | 旧表 → 新三表迁移脚本（历史参考） |
