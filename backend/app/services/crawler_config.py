from copy import deepcopy
from pathlib import Path
from urllib.parse import urlparse

import yaml

from app.config import CRAWLER_CONFIG_PATH, FIRECRAWL_ENABLED


DEFAULT_CRAWLER_CONFIG = {
    "queue": {
        "name": "article-content",
        "retry_max": 3,
    },
    "crawler": {
        "provider": "playwright_readability",
        "timeout_ms": 30000,
        "wait_until": "domcontentloaded",
        "user_agent": "TripolarBot/0.1",
        "min_content_chars": 500,
        "max_content_chars": 200000,
        "scroll_steps": 2,
    },
    "fallback": {
        "firecrawl_enabled": FIRECRAWL_ENABLED,
        "use_firecrawl_when_content_short": True,
    },
    "domains": {},
}


def _deep_merge(base: dict, override: dict) -> dict:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _config_path() -> Path:
    path = Path(CRAWLER_CONFIG_PATH)
    if path.is_absolute():
        return path
    return Path(__file__).resolve().parents[3] / path


def load_crawler_config() -> dict:
    path = _config_path()
    if not path.exists():
        return deepcopy(DEFAULT_CRAWLER_CONFIG)

    try:
        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}
    except Exception:
        return deepcopy(DEFAULT_CRAWLER_CONFIG)

    if not isinstance(data, dict):
        return deepcopy(DEFAULT_CRAWLER_CONFIG)

    config = _deep_merge(DEFAULT_CRAWLER_CONFIG, data)
    config["fallback"]["firecrawl_enabled"] = bool(
        FIRECRAWL_ENABLED or config.get("fallback", {}).get("firecrawl_enabled")
    )
    return config


def get_domain_config(url: str, config: dict | None = None) -> dict:
    config = config or load_crawler_config()
    host = urlparse(url).hostname or ""
    crawler_config = deepcopy(config.get("crawler", {}))

    for domain, domain_config in config.get("domains", {}).items():
        if host == domain or host.endswith(f".{domain}"):
            return _deep_merge(crawler_config, domain_config or {})

    return crawler_config
