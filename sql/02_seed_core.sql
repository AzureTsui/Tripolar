-- ============================================================
-- Tripolar 种子数据 — RSS 资讯核心
-- 表: categories / sources
-- 执行: psql -U tripolar -d tripolar -f sql/02_seed_core.sql
-- ============================================================

BEGIN;

INSERT INTO categories (name, slug, sort_order) VALUES
    ('观点洞察', 'opinion', 1),
    ('产品发布', 'product', 2),
    ('行业报告', 'report',  3),
    ('模型发布', 'model',   4),
    ('论文',     'paper',   5),
    ('工具测评', 'tool',    6)
ON CONFLICT (slug) DO NOTHING;

INSERT INTO sources (name, url, type) VALUES
    ('36氪 AI',      'https://36kr.com/feed',                                          'rss'),
    ('机器之心',       'https://www.jiqizhixin.com/rss',                                'rss'),
    ('Hacker News',  'https://hnrss.org/frontpage',                                    'rss'),
    ('ArXiv ML',     'http://export.arxiv.org/rss/cs.LG',                              'rss'),
    ('TechCrunch AI','https://techcrunch.com/category/artificial-intelligence/feed',    'rss')
ON CONFLICT (url) DO NOTHING;

DO $$
BEGIN
    RAISE NOTICE 'categories : % rows', (SELECT count(*) FROM categories);
    RAISE NOTICE 'sources    : % rows', (SELECT count(*) FROM sources);
END $$;

COMMIT;
