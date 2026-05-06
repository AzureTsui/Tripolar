-- Tripolar 数据库建表 DDL
-- 对应 backend/app/models.py，由 seed.py 自动建表
-- 本文件仅用于参考或手动重建

CREATE TABLE IF NOT EXISTS sources (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    url             TEXT NOT NULL UNIQUE,
    type            VARCHAR(20) DEFAULT 'rss',
    trust_score     FLOAT DEFAULT 0.5,
    status          VARCHAR(20) DEFAULT 'active',
    last_fetched_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    slug        VARCHAR(100) NOT NULL UNIQUE,
    sort_order  INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS articles (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(500) NOT NULL,
    source      VARCHAR(200) NOT NULL,
    url         TEXT NOT NULL UNIQUE,
    date        TIMESTAMPTZ,
    tags               VARCHAR(500) DEFAULT '',
    summary            TEXT,
    content_text       TEXT,
    content_format     VARCHAR(20) DEFAULT 'markdown',
    content_status     VARCHAR(20) DEFAULT 'pending',
    content_error      TEXT,
    content_fetched_at TIMESTAMPTZ,
    content_provider   VARCHAR(50),
    content_hash       VARCHAR(64),
    heat_score         FLOAT DEFAULT 0.0,
    created_at         TIMESTAMPTZ DEFAULT now(),
    updated_at         TIMESTAMPTZ DEFAULT now()
);

-- 已有数据库升级正文抓取字段
ALTER TABLE articles
    ADD COLUMN IF NOT EXISTS content_text TEXT,
    ADD COLUMN IF NOT EXISTS content_format VARCHAR(20) DEFAULT 'markdown',
    ADD COLUMN IF NOT EXISTS content_status VARCHAR(20) DEFAULT 'pending',
    ADD COLUMN IF NOT EXISTS content_error TEXT,
    ADD COLUMN IF NOT EXISTS content_fetched_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS content_provider VARCHAR(50),
    ADD COLUMN IF NOT EXISTS content_hash VARCHAR(64);

-- 种子数据
INSERT INTO categories (name, slug) VALUES
    ('观点洞察', 'opinion'),
    ('产品发布', 'product'),
    ('行业报告', 'report'),
    ('模型发布', 'model'),
    ('论文',     'paper'),
    ('工具测评', 'tool')
ON CONFLICT (slug) DO NOTHING;

INSERT INTO sources (name, url, type) VALUES
    ('36氪 AI',      'https://36kr.com/feed',                                          'rss'),
    ('机器之心',       'https://www.jiqizhixin.com/rss',                                'rss'),
    ('Hacker News',  'https://hnrss.org/frontpage',                                    'rss'),
    ('ArXiv ML',     'http://export.arxiv.org/rss/cs.LG',                              'rss'),
    ('TechCrunch AI','https://techcrunch.com/category/artificial-intelligence/feed',    'rss')
ON CONFLICT (url) DO NOTHING;
