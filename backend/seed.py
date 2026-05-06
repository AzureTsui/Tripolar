"""Seed initial categories, sources, and AI tool metadata."""
import os
from app.database import SessionLocal, init_db
from app.models import Category, Source, AIToolProductType, AIToolUseCase

CATEGORIES = [
    ("观点洞察", "opinion"),
    ("产品发布", "product"),
    ("行业报告", "report"),
    ("模型发布", "model"),
    ("论文", "paper"),
    ("工具测评", "tool"),
]

SOURCES = [
    {"name": "36氪 AI", "url": "https://36kr.com/feed", "type": "rss"},
    {"name": "机器之心", "url": "https://www.jiqizhixin.com/rss", "type": "rss"},
    {"name": "Hacker News", "url": "https://hnrss.org/frontpage", "type": "rss"},
    {"name": "ArXiv ML", "url": "http://export.arxiv.org/rss/cs.LG", "type": "rss"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed", "type": "rss"},
]

AI_PRODUCT_TYPES = [
    ("AI编程工具", "ai-coding-tools", "辅助开发者写代码、读代码、调试和重构的AI工具", 10),
    ("AI视频工具", "ai-video-tools", "用于视频生成、剪辑、字幕、特效和内容制作的AI工具", 20),
    ("AI写作工具", "ai-writing-tools", "用于文章、营销文案、邮件、脚本等文本创作的AI工具", 30),
    ("AI图像工具", "ai-image-tools", "用于图片生成、编辑、设计和视觉创作的AI工具", 40),
    ("AI办公工具", "ai-office-tools", "用于文档、表格、PPT、会议和协作效率提升的AI工具", 50),
]

AI_USE_CASES = [
    ("代码生成", "code-generation", "根据自然语言或上下文生成代码", 10),
    ("视频生成", "video-generation", "根据提示词、图片或其他素材生成视频内容", 10),
    ("视频创作", "video-creation", "综合视频内容创作，包括策划、制作和输出", 15),
    ("代码补全", "code-completion", "在编码过程中智能补全代码", 20),
    ("视频剪辑", "video-editing", "剪辑、拼接、调整和处理视频内容", 20),
    ("电商视频制作", "ecommerce-video-creation", "面向电商商品展示、营销投放和带货场景的视频制作", 25),
    ("数字人制作", "digital-human-creation", "创建虚拟数字人形象并生成口播、交互或表演视频", 30),
    ("动画制作", "animation-creation", "生成动画风格的视频内容，包括二次元、漫画等", 35),
    ("视频翻译/本地化", "video-localization", "视频翻译、配音替换和多语言本地化处理", 40),
    ("字幕生成", "subtitle-generation", "自动识别语音并生成字幕", 40),
    ("视频广告制作", "video-ad-creation", "面向广告投放和营销推广场景的视频素材制作", 45),
    ("短剧创作", "short-drama-creation", "创作漫剧、短剧或系列化叙事视频内容", 50),
    ("文案写作", "copywriting", "生成营销文案、社媒文案、广告语等内容", 50),
    ("内容创作", "content-creation", "面向自媒体、图文转视频等内容创作需求", 55),
    ("视觉创作", "visual-creation", "综合视觉内容创作，包括图像和视频的艺术化生成", 60),
    ("文章写作", "article-writing", "生成长文章、博客、SEO文章等内容", 60),
    ("知识视频制作", "knowledge-video-creation", "将文档、知识内容转化为结构化讲解视频", 65),
    ("创意设计", "creative-video-design", "视频风格化、创意设计和艺术化处理", 70),
    ("图片生成", "image-generation", "根据提示词生成图片", 70),
    ("PPT生成", "presentation-generation", "根据主题或文档生成演示文稿", 80),
    ("文档问答", "document-qa", "基于文档内容进行问答和总结", 90),
]


def seed():
    init_db()
    db = SessionLocal()
    try:
        for name, slug in CATEGORIES:
            if not db.query(Category).filter(Category.slug == slug).first():
                db.add(Category(name=name, slug=slug))

        for s in SOURCES:
            if not db.query(Source).filter(Source.url == s["url"]).first():
                db.add(Source(**s))

        for name, slug, desc, sort_order in AI_PRODUCT_TYPES:
            if not db.query(AIToolProductType).filter(AIToolProductType.slug == slug).first():
                db.add(AIToolProductType(name=name, slug=slug, description=desc, sort_order=sort_order))

        for name, slug, desc, sort_order in AI_USE_CASES:
            if not db.query(AIToolUseCase).filter(AIToolUseCase.slug == slug).first():
                db.add(AIToolUseCase(name=name, slug=slug, description=desc, sort_order=sort_order))

        db.commit()
        print("Seed data inserted (categories, sources, AI product types, AI use cases).")
        print("For 100 AI video tools, run: psql -U tripolar -d tripolar -f sql/03_seed_ai_tools.sql")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
