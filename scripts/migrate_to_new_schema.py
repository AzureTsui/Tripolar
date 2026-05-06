"""Migrate data from ai_tools_backup202505062330 → new 3-table schema."""
import psycopg2
import re
import hashlib

conn = psycopg2.connect('postgresql://tripolar:tripolar@localhost:5432/tripolar')
cur = conn.cursor()

# ============================================================
# 1. Create the 3 new tables
# ============================================================
cur.execute("""
CREATE TABLE IF NOT EXISTS public.ai_product_types (
  id serial PRIMARY KEY,
  name varchar(100) NOT NULL,
  slug varchar(120) NOT NULL UNIQUE,
  description text,
  sort_order integer DEFAULT 0 NOT NULL,
  is_active boolean DEFAULT true NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS public.ai_use_cases (
  id serial PRIMARY KEY,
  name varchar(100) NOT NULL,
  slug varchar(120) NOT NULL UNIQUE,
  description text,
  sort_order integer DEFAULT 0 NOT NULL,
  is_active boolean DEFAULT true NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS public.ai_tools (
  id serial PRIMARY KEY,
  name varchar(100) NOT NULL,
  slug varchar(120) NOT NULL UNIQUE,
  company varchar(100),
  product_type_id integer NOT NULL,
  primary_use_case_id integer NOT NULL,
  short_description varchar(200),
  overview text,
  website_url varchar(500),
  logo_url varchar(500),
  status varchar(30) DEFAULT 'active' NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL,
  CONSTRAINT fk_ai_tools_product_type
    FOREIGN KEY (product_type_id) REFERENCES public.ai_product_types(id),
  CONSTRAINT fk_ai_tools_primary_use_case
    FOREIGN KEY (primary_use_case_id) REFERENCES public.ai_use_cases(id)
);
""")
print("Tables created.")

# ============================================================
# 2. Insert product type
# ============================================================
cur.execute("""
INSERT INTO public.ai_product_types (name, slug, description, sort_order)
VALUES ('AI视频工具', 'ai-video-tools', '用于视频生成、剪辑、字幕、特效和内容制作的AI工具', 20)
ON CONFLICT (slug) DO NOTHING;
""")

# ============================================================
# 3. Insert all use cases (video-domain)
# ============================================================
use_cases = [
    ('视频生成', 'video-generation', '根据提示词、图片或其他素材生成视频内容', 10),
    ('视频创作', 'video-creation', '综合视频内容创作，包括策划、制作和输出', 15),
    ('视频剪辑', 'video-editing', '剪辑、拼接、调整和处理视频内容', 20),
    ('电商视频制作', 'ecommerce-video-creation', '面向电商商品展示、营销投放和带货场景的视频制作', 25),
    ('数字人制作', 'digital-human-creation', '创建虚拟数字人形象并生成口播、交互或表演视频', 30),
    ('动画制作', 'animation-creation', '生成动画风格的视频内容，包括二次元、漫画等', 35),
    ('视频翻译/本地化', 'video-localization', '视频翻译、配音替换和多语言本地化处理', 40),
    ('视频广告制作', 'video-ad-creation', '面向广告投放和营销推广场景的视频素材制作', 45),
    ('短剧创作', 'short-drama-creation', '创作漫剧、短剧或系列化叙事视频内容', 50),
    ('内容创作', 'content-creation', '面向自媒体、图文转视频等内容创作需求', 55),
    ('视觉创作', 'visual-creation', '综合视觉内容创作，包括图像和视频的艺术化生成', 60),
    ('知识视频制作', 'knowledge-video-creation', '将文档、知识内容转化为结构化讲解视频', 65),
    ('创意设计', 'creative-video-design', '视频风格化、创意设计和艺术化处理', 70),
    ('字幕生成', 'subtitle-generation', '自动识别语音并生成字幕', 75),
]

for name, slug, desc, sort_order in use_cases:
    cur.execute(
        "INSERT INTO public.ai_use_cases (name, slug, description, sort_order) "
        "VALUES (%s, %s, %s, %s) ON CONFLICT (slug) DO NOTHING",
        (name, slug, desc, sort_order)
    )

cur.execute("SELECT id, slug FROM public.ai_use_cases")
use_case_map = {slug: id for id, slug in cur.fetchall()}
print(f"Use cases: {len(use_case_map)}")

# ============================================================
# 4. Track -> use_case mapping
# ============================================================
track_to_use_case = {
    '视频生成': 'video-generation',
    '视频大模型': 'video-generation',
    '视频生成/编辑': 'video-generation',
    '视频短片': 'video-generation',
    '音乐视频': 'video-generation',
    '短视频': 'video-generation',
    'AI视频创作': 'video-creation',
    '视频Agent': 'video-creation',
    '视频社区': 'video-creation',
    '影视创作': 'video-creation',
    '视频制作': 'video-creation',
    '视频本地化': 'video-localization',
    '视频翻译': 'video-localization',
    '视频编辑': 'video-editing',
    '视频剪辑': 'video-editing',
    '视频处理': 'video-editing',
    '电商视频': 'ecommerce-video-creation',
    '电商营销': 'ecommerce-video-creation',
    '直播电商': 'ecommerce-video-creation',
    '数字人': 'digital-human-creation',
    '数字人/视频': 'digital-human-creation',
    '3D数字人': 'digital-human-creation',
    '数字人营销': 'digital-human-creation',
    '对口型': 'digital-human-creation',
    '角色动态': 'digital-human-creation',
    '角色生成': 'digital-human-creation',
    '数字分身': 'digital-human-creation',
    '虚拟人': 'digital-human-creation',
    '动画生成': 'animation-creation',
    '动画视频': 'animation-creation',
    '动漫创作': 'animation-creation',
    '动漫视频': 'animation-creation',
    '动画故事': 'animation-creation',
    '视频广告': 'video-ad-creation',
    '营销视频': 'video-ad-creation',
    '创意生产': 'video-ad-creation',
    '漫剧/短剧': 'short-drama-creation',
    '短剧/漫剧': 'short-drama-creation',
    '短剧协作': 'short-drama-creation',
    '短剧创作': 'short-drama-creation',
    '内容创作': 'content-creation',
    '智能创作': 'content-creation',
    'AIGC创作': 'content-creation',
    '故事生成': 'content-creation',
    '视觉创作': 'visual-creation',
    '图像/视频': 'visual-creation',
    '知识视频': 'knowledge-video-creation',
    '创意设计': 'creative-video-design',
}

# ============================================================
# 5. Manual slugs for all 100 products
# ============================================================
manual_slugs = {
    'LibTV': 'libtv',
    '绘蛙AI视频': 'huiwa-ai-video',
    '堆友AI视频': 'duiyou-ai-video',
    'SoundView': 'soundview',
    '蝉镜': 'chanjing',
    'HeyGen': 'heygen',
    'LiblibAI': 'liblibai',
    '有言': 'youyan',
    '白日梦': 'bai-ri-meng-ai',
    '即梦AI': 'jimeng-ai',
    'Pollo AI': 'pollo-ai',
    'Seedance': 'seedance',
    '魔珐星云': 'mofaxingyun',
    'JoyPix': 'joypix',
    '可灵AI': 'kling-ai',
    'Vidu': 'vidu',
    '腾讯混元AI视频': 'hunyuan-ai-video',
    '通义万相AI视频': 'tongyi-wanxiang-video',
    '雾象 (Fogsight)': 'fogsight',
    'TapNow': 'tapnow',
    'Higgsfield': 'higgsfield',
    'Flova': 'flova',
    'Zorq AI': 'zorq-ai',
    'Pexo': 'pexo',
    'Topview': 'topview-ai',
    '万镜一刻': 'wanjing-yike',
    'TagoMovie': 'tagomovie',
    '灵绘AI': 'linghui-ai',
    'Pixmax': 'pixmax',
    'Brainrot.mov': 'brainrot-mov',
    '造点AI': 'zaodian-ai',
    '造次': 'zaoci',
    '花生AI': 'huasheng-ai',
    'VibeKnow': 'vibeknow',
    'MuseArt AI': 'museart-ai',
    'AniShort': 'anishort',
    '献丑AI': 'xianchou-ai',
    '海螺视频': 'hailuo-video',
    'MochiAni': 'mochiani',
    'AdsTurbo AI': 'adsturbo-ai',
    'NextCut AI': 'nextcut-ai',
    '云幕同声': 'yunmu-tongsheng',
    '萌动AI': 'mengdong-ai',
    'KomikoAI': 'komiko-ai',
    'Keevx': 'keevx',
    '即创': 'jichuang',
    '智谱清影': 'zhipu-qingying',
    '内容特工队': 'content-agent',
    '磁力开创': 'cili-kaichuang',
    'A2E': 'a2e',
    'HitPaw': 'hitpaw',
    'Runway': 'runway',
    'Pika': 'pika',
    'KreadoAI': 'kreado-ai',
    'SekoTalk': 'sekotalk',
    '通义灵眸': 'tongyi-lingmou',
    '巨日禄': 'jurilu',
    'Medeo': 'medeo',
    'Boba': 'boba-video',
    'Dream Machine': 'dream-machine',
    '讯飞绘镜': 'xunfei-huijing',
    '绘想': 'huixiang',
    'Hedra': 'hedra',
    'Vozo': 'vozo',
    'Viggle': 'viggle',
    'Tavus': 'tavus',
    '万兴天幕': 'wanxing-tianmu',
    '妙播': 'miaobo',
    '阶跃视频': 'jieyue-video',
    '秒创': 'miaochuang',
    '元镜': 'yuanjing',
    'SkyReels': 'skyreels',
    'MOKI': 'moki',
    '神笔马良': 'shenbi-maliang',
    'Video Ocean': 'video-ocean',
    'Flow Studio': 'flow-studio',
    'Vizard': 'vizard',
    '寻光': 'xunguang',
    'Hotshot': 'hotshot',
    'vivago.ai': 'vivago-ai',
    'Humva': 'humva',
    'D-ID': 'd-id',
    'Stable Video': 'stable-video',
    'OneStory': 'onestory',
    'Noisee AI': 'noisee-ai',
    '万兴播爆': 'wanxing-bobao',
    'Vimi': 'vimi',
    'Etna': 'etna',
    '艺映AI': 'yiying-ai',
    'LensGo': 'lensgo',
    '必剪Studio': 'bijian-studio',
    '度加创作工具': 'dujia-creator',
    'WinkStudio': 'winkstudio',
    'VMagic': 'vmagic',
    '讯飞虚拟人': 'xunfei-virtual-man',
    '飞影数字人': 'feiying-digital-human',
    'Video Studio': 'video-studio',
    'Pixfun': 'pixfun',
    'Decohere': 'decohere',
    'YoYo': 'yoyo-video',
}


def make_slug(name):
    """Fallback slug generator."""
    if all(ord(c) < 128 for c in name):
        s = name.lower().strip()
        s = re.sub(r'[^a-z0-9]+', '-', s)
        return s.strip('-')
    h = hashlib.md5(name.encode()).hexdigest()[:6]
    eng_parts = re.findall(r'[A-Za-z0-9]+', name)
    if eng_parts:
        base = '-'.join(p.lower() for p in eng_parts)
        return f'{base}-{h}'
    return f'ai-tool-{h}'


# ============================================================
# 6. Migrate: backup -> new ai_tools
# ============================================================
cur.execute(
    "SELECT id, name, company, track, core_function, overview, website_url, created_at "
    "FROM ai_tools_backup202505062330 ORDER BY id"
)
rows = cur.fetchall()

cur.execute("SELECT id FROM public.ai_product_types WHERE slug = 'ai-video-tools'")
pt_id = cur.fetchone()[0]

committed = 0
warnings = []

for row in rows:
    old_id, name, company, track, core_func, overview, url, created_at = row

    uc_slug = track_to_use_case.get(track)
    if uc_slug is None:
        warnings.append(f"Unknown track '{track}' for {name}, defaulting to video-creation")
        uc_slug = 'video-creation'
    uc_id = use_case_map[uc_slug]

    slug = manual_slugs.get(name)
    if slug is None:
        slug = make_slug(name)
        warnings.append(f"AUTO-SLUG: {name} -> {slug}")

    try:
        cur.execute(
            "INSERT INTO public.ai_tools "
            "(name, slug, company, product_type_id, primary_use_case_id, "
            " short_description, overview, website_url, status, created_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'active', %s) "
            "ON CONFLICT (slug) DO UPDATE SET "
            "name = EXCLUDED.name, company = EXCLUDED.company, "
            "product_type_id = EXCLUDED.product_type_id, "
            "primary_use_case_id = EXCLUDED.primary_use_case_id, "
            "short_description = EXCLUDED.short_description, "
            "overview = EXCLUDED.overview, website_url = EXCLUDED.website_url, "
            "updated_at = now()",
            (name, slug, company, pt_id, uc_id, core_func, overview, url, created_at)
        )
        committed += 1
    except Exception as e:
        warnings.append(f"ERROR inserting {name}: {e}")

conn.commit()
print(f"Migration: {committed}/{len(rows)} rows inserted")

for w in warnings:
    print(f"  {w}")

# ============================================================
# 7. Verify
# ============================================================
cur.execute("SELECT count(*) FROM public.ai_tools")
print(f"\nai_tools count: {cur.fetchone()[0]}")

cur.execute("""
    SELECT uc.name, count(*) as cnt
    FROM public.ai_tools t
    JOIN public.ai_use_cases uc ON t.primary_use_case_id = uc.id
    GROUP BY uc.name ORDER BY cnt DESC
""")
print("Use case distribution:")
for r in cur.fetchall():
    print(f"  {r[0]:20s} {r[1]}")

cur.close()
conn.close()
print("\nDone.")
