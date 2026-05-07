from dataclasses import dataclass

from bs4 import BeautifulSoup
from markdownify import markdownify as html_to_markdown
from readability import Document

from app.config import FIRECRAWL_API_KEY
from app.services.crawler_config import get_domain_config, load_crawler_config


@dataclass
class ExtractedContent:
    text: str
    format: str
    provider: str
    title: str | None = None


class ContentExtractionError(Exception):
    pass


def extract_article_content(url: str) -> ExtractedContent:
    config = load_crawler_config()
    domain_config = get_domain_config(url, config)

    if domain_config.get("skip"):
        raise ContentExtractionError("domain skipped by crawler config")

    try:
        content = _extract_with_playwright_readability(url, domain_config)
    except Exception as error:
        if _firecrawl_enabled(config):
            return _extract_with_firecrawl(url, domain_config)
        raise ContentExtractionError(str(error)) from error

    min_chars = int(domain_config.get("min_content_chars", 500))
    if len(content.text.strip()) < min_chars:
        fallback = config.get("fallback", {})
        if fallback.get("use_firecrawl_when_content_short") and _firecrawl_enabled(config):
            return _extract_with_firecrawl(url, domain_config)
        raise ContentExtractionError("extracted content is shorter than min_content_chars")

    return content


def _extract_with_playwright_readability(url: str, domain_config: dict) -> ExtractedContent:
    from playwright.sync_api import sync_playwright

    timeout_ms = int(domain_config.get("timeout_ms", 30000))
    wait_until = domain_config.get("wait_until", "domcontentloaded")
    user_agent = domain_config.get("user_agent", "TripolarBot/0.1")
    scroll_steps = int(domain_config.get("scroll_steps", 2))
    max_chars = int(domain_config.get("max_content_chars", 200000))

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()
        page.goto(url, wait_until=wait_until, timeout=timeout_ms)

        for _ in range(max(scroll_steps, 0)):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(500)

        html = page.content()
        browser.close()

    document = Document(html)
    title = document.short_title()
    summary_html = document.summary(html_partial=True)
    markdown = _html_fragment_to_markdown(summary_html)

    if max_chars > 0:
        markdown = markdown[:max_chars]

    return ExtractedContent(
        text=markdown.strip(),
        format="markdown",
        provider="playwright_readability",
        title=title,
    )


def _html_fragment_to_markdown(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")

    for annotation in soup.select('annotation[encoding="application/x-tex"]'):
        annotation.replace_with(f" ${annotation.get_text(strip=True)} ")

    for math_script in soup.select('script[type="math/tex"], script[type="math/tex; mode=display"]'):
        tex = math_script.get_text(strip=True)
        math_script.replace_with(f" ${tex} ")

    for hidden in soup.select(".katex-html"):
        hidden.decompose()

    return html_to_markdown(str(soup), heading_style="ATX", strip=["script", "style"]).strip()


def _firecrawl_enabled(config: dict) -> bool:
    fallback = config.get("fallback", {})
    return bool(fallback.get("firecrawl_enabled") and FIRECRAWL_API_KEY)


def _extract_with_firecrawl(url: str, domain_config: dict) -> ExtractedContent:
    try:
        from firecrawl import FirecrawlApp
    except Exception as error:
        raise ContentExtractionError("firecrawl package is unavailable") from error

    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    result = app.scrape_url(url, params={"formats": ["markdown"]})
    markdown = _firecrawl_markdown(result)
    max_chars = int(domain_config.get("max_content_chars", 200000))

    if max_chars > 0:
        markdown = markdown[:max_chars]

    if not markdown.strip():
        raise ContentExtractionError("firecrawl returned empty markdown")

    return ExtractedContent(
        text=markdown.strip(),
        format="markdown",
        provider="firecrawl",
        title=None,
    )


def _firecrawl_markdown(result) -> str:
    if isinstance(result, dict):
        return result.get("markdown") or result.get("data", {}).get("markdown") or ""

    markdown = getattr(result, "markdown", None)
    if markdown:
        return markdown

    data = getattr(result, "data", None)
    if isinstance(data, dict):
        return data.get("markdown", "")

    return ""
