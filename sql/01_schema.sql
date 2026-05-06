-- ============================================================
-- Tripolar 数据库 — 全量 DDL
-- 包含: RSS 资讯核心 + AI 工具目录 两套表
-- 用途: 手动建库或结构参考
-- 适配: PostgreSQL 16
-- ============================================================

BEGIN;

-- ============================================================
-- 一、RSS 资讯核心（sources / categories / articles）
--    对应 backend/app/models.py
-- ============================================================

-- 1-1. RSS 订阅源
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
COMMENT ON TABLE sources IS 'RSS 订阅源管理';

-- 1-2. 文章分类
CREATE TABLE IF NOT EXISTS categories (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    slug       VARCHAR(100) NOT NULL UNIQUE,
    sort_order INTEGER DEFAULT 0
);
COMMENT ON TABLE categories IS '文章分类';

-- 1-3. 聚合文章
CREATE TABLE IF NOT EXISTS articles (
    id         SERIAL PRIMARY KEY,
    title      VARCHAR(500) NOT NULL,
    source     VARCHAR(200) NOT NULL,
    url        TEXT NOT NULL UNIQUE,
    date       TIMESTAMPTZ,
    tags       VARCHAR(500) DEFAULT '',
    summary    TEXT,
    heat_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
COMMENT ON TABLE articles IS 'RSS 聚合文章';
COMMENT ON COLUMN articles.source IS '来源名称字符串，不走外键';

-- ============================================================
-- 二、AI 工具目录（ai_product_types / ai_use_cases / ai_tools）
--    设计依据: docs/ai_tools表设计逻辑..md
--    原则:
--      产品类型 → 回答"它是什么工具？"
--      使用场景 → 回答"用户用它做什么任务？"
--      MVP 每个产品只保留一个主产品类型 + 一个主使用场景
-- ============================================================

-- 2-1. 产品类型表
CREATE TABLE IF NOT EXISTS ai_product_types (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100)  NOT NULL,
    slug        VARCHAR(120)  NOT NULL UNIQUE,
    description TEXT,
    sort_order  INTEGER       DEFAULT 0 NOT NULL,
    is_active   BOOLEAN       DEFAULT TRUE NOT NULL,
    created_at  TIMESTAMPTZ   DEFAULT now() NOT NULL,
    updated_at  TIMESTAMPTZ   DEFAULT now() NOT NULL
);
COMMENT ON TABLE ai_product_types IS 'AI产品类型表 — 回答"它是什么工具？"';

-- 2-2. 使用场景表
CREATE TABLE IF NOT EXISTS ai_use_cases (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100)  NOT NULL,
    slug        VARCHAR(120)  NOT NULL UNIQUE,
    description TEXT,
    sort_order  INTEGER       DEFAULT 0 NOT NULL,
    is_active   BOOLEAN       DEFAULT TRUE NOT NULL,
    created_at  TIMESTAMPTZ   DEFAULT now() NOT NULL,
    updated_at  TIMESTAMPTZ   DEFAULT now() NOT NULL
);
COMMENT ON TABLE ai_use_cases IS 'AI产品使用场景表 — 回答"用户用它做什么任务？"';

-- 2-3. AI 工具主表
CREATE TABLE IF NOT EXISTS ai_tools (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(100)  NOT NULL,
    slug                VARCHAR(120)  NOT NULL UNIQUE,
    company             VARCHAR(100),
    product_type_id     INTEGER       NOT NULL,
    primary_use_case_id INTEGER       NOT NULL,
    short_description   VARCHAR(200),
    overview            TEXT,
    website_url         VARCHAR(500),
    logo_url            VARCHAR(500),
    status              VARCHAR(30)   DEFAULT 'active' NOT NULL,
    created_at          TIMESTAMPTZ   DEFAULT now() NOT NULL,
    updated_at          TIMESTAMPTZ   DEFAULT now() NOT NULL,

    CONSTRAINT fk_ai_tools_product_type
        FOREIGN KEY (product_type_id) REFERENCES ai_product_types(id),
    CONSTRAINT fk_ai_tools_primary_use_case
        FOREIGN KEY (primary_use_case_id) REFERENCES ai_use_cases(id)
);
COMMENT ON TABLE ai_tools IS 'AI产品表 — 存放具体 AI 工具/产品的本体信息';
COMMENT ON COLUMN ai_tools.company             IS '所属公司（MVP 先用字符串）';
COMMENT ON COLUMN ai_tools.product_type_id     IS '主产品类型 → ai_product_types';
COMMENT ON COLUMN ai_tools.primary_use_case_id IS '主使用场景 → ai_use_cases';
COMMENT ON COLUMN ai_tools.short_description   IS '一句话简介';
COMMENT ON COLUMN ai_tools.overview            IS '产品详细介绍';
COMMENT ON COLUMN ai_tools.website_url         IS '产品官网地址';

-- 索引
CREATE INDEX IF NOT EXISTS idx_ai_tools_product_type ON ai_tools (product_type_id);
CREATE INDEX IF NOT EXISTS idx_ai_tools_use_case     ON ai_tools (primary_use_case_id);
CREATE INDEX IF NOT EXISTS idx_ai_tools_company      ON ai_tools (company);
CREATE INDEX IF NOT EXISTS idx_ai_tools_status       ON ai_tools (status);

COMMIT;
