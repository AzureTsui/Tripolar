# 数据库初始化流程

## 前置条件

- PostgreSQL 运行中
- `backend/` 目录下已创建 `venv` 并安装 `requirements.txt`
- `.env` 中 `DATABASE_URL` 配置正确

---

## 一、建库（手动，仅首次）

PostgreSQL 安装完成后，需要创建数据库和用户：

```sql
CREATE USER tripolar WITH PASSWORD 'tripolar';
CREATE DATABASE tripolar OWNER tripolar;
```

与 `.env` 中的连接串对应：

```
DATABASE_URL=postgresql://tripolar:tripolar@localhost:5432/tripolar
```

---

## 二、建表（自动）

`app/database.py` 定义了全局引擎和 `Base`：

```python
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
```

调用 `init_db()` 时会执行：

```python
def init_db():
    from app.models import Source, Category, Article  # 加载模型
    Base.metadata.create_all(bind=engine)             # 自动建表
```

`create_all` 的行为：
- 表不存在 → 创建
- 表已存在但字段有变化 → **不更新**（不会自动加列或改类型）
- 如果需要改表结构，需要手动执行 `ALTER TABLE` 或删表重建

---

## 三、种子数据（手动，首次 + 重置时）

`seed.py` 初始化分类和 RSS 源：

### 插入的分类（6 个）

| name | slug |
|------|------|
| 观点洞察 | opinion |
| 产品发布 | product |
| 行业报告 | report |
| 模型发布 | model |
| 论文 | paper |
| 工具测评 | tool |

### 插入的 RSS 源（5 个）

| name | url | type |
|------|-----|------|
| 36氪 AI | https://36kr.com/feed | rss |
| 机器之心 | https://www.jiqizhixin.com/rss | rss |
| Hacker News | https://hnrss.org/frontpage | rss |
| ArXiv ML | http://export.arxiv.org/rss/cs.LG | rss |
| TechCrunch AI | https://techcrunch.com/category/artificial-intelligence/feed | rss |

### 执行

```bash
cd backend
python seed.py
# 输出：Seed data inserted.
```

**幂等**：重复执行不会重复插入（按 URL 和 slug 判重）。

---

## 四、完整初始化流程

```mermaid
flowchart LR
    A[安装 PostgreSQL] --> B[创建用户 + 数据库]
    B --> C[python seed.py]
    C --> D[自动建表 + 写入种子数据]
    D --> E[python scripts/fetch_articles.py]
    E --> F[抓取 RSS → 写入 articles 表]
```

---

## 五、重置数据库

```bash
# 进入 psql，删除并重建
DROP DATABASE tripolar;
CREATE DATABASE tripolar OWNER tripolar;

# 重新初始化
cd backend && python seed.py
```

---

## 六、当前限制

- 没有迁移工具（Alembic），改模型后需要手动同步表结构
- `create_all` 不会删数据，也不会改已有字段类型
- 未来建议引入 Alembic：`pip install alembic && alembic init alembic`
