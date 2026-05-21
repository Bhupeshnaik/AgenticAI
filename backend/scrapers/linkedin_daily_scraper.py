"""
LinkedIn Daily Scraper
======================

Continuously runs once every 24 hours and collects LinkedIn posts that
discuss:

  * Domain-Driven Design (DDD)
  * Industry-domain agentic AI solutions
  * Real-world success stories of agentic deployments in industry

Legality
--------
Direct scraping of LinkedIn HTML violates LinkedIn's User Agreement §8.2.
This collector therefore only uses lawful, API-backed sources. Pick one
via env vars:

  LINKEDIN_SCRAPER_PROVIDER=serpapi     # Google search "site:linkedin.com"
                                        #   SERPAPI_KEY required
  LINKEDIN_SCRAPER_PROVIDER=rapidapi    # licensed LinkedIn data API
                                        #   RAPIDAPI_KEY + RAPIDAPI_HOST required
  LINKEDIN_SCRAPER_PROVIDER=linkedin    # official LinkedIn API (partner only)
                                        #   LINKEDIN_ACCESS_TOKEN required

Outputs JSONL files under ``data/linkedin/`` — one file per UTC day plus
an aggregate ``all_posts.jsonl`` deduplicated by URL.

Run
---
    python -m backend.scrapers.linkedin_daily_scraper          # daemon
    python -m backend.scrapers.linkedin_daily_scraper --once   # one cycle
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import aiohttp
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [linkedin-scraper] %(message)s",
)
log = logging.getLogger(__name__)


# Search queries — each query is run against the configured provider.
# Mix of DDD, agentic AI in industry verticals, and success-story phrasing.
DEFAULT_QUERIES: list[str] = [
    '"domain-driven design" agentic AI',
    '"domain-driven" agents production',
    '"agentic AI" "case study" industry',
    '"agentic AI" success story banking',
    '"agentic AI" success story healthcare',
    '"agentic AI" success story manufacturing',
    '"agentic AI" success story retail',
    '"agentic AI" success story insurance',
    '"agentic workflow" enterprise deployment',
    '"multi-agent" production deployment industry',
    '"domain agents" enterprise',
    '"agentic solution" ROI results',
]

# Keyword filter applied AFTER fetching — keeps only relevant posts.
RELEVANCE_KEYWORDS: tuple[str, ...] = (
    "domain-driven",
    "domain driven",
    "ddd",
    "agentic",
    "multi-agent",
    "autonomous agent",
    "ai agent",
    "agent orchestration",
    "case study",
    "success story",
    "rollout",
    "in production",
)


@dataclass
class LinkedInPost:
    id: str
    url: str
    title: str
    snippet: str
    source: str
    matched_keywords: list[str]
    author: str | None = None
    posted_at: str | None = None  # ISO8601 if known
    fetched_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @staticmethod
    def stable_id(url: str) -> str:
        return hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]


class ProviderError(RuntimeError):
    pass


# ───────────────────────────── Providers ──────────────────────────────


async def _search_serpapi(
    session: aiohttp.ClientSession, query: str, api_key: str
) -> list[LinkedInPost]:
    """Use SerpAPI to Google-search ``site:linkedin.com/posts <query>``."""
    params = {
        "engine": "google",
        "q": f'site:linkedin.com/posts {query}',
        "num": "20",
        "api_key": api_key,
    }
    async with session.get(
        "https://serpapi.com/search.json", params=params, timeout=30
    ) as resp:
        if resp.status != 200:
            raise ProviderError(f"SerpAPI HTTP {resp.status}: {await resp.text()}")
        data = await resp.json()

    posts: list[LinkedInPost] = []
    for item in data.get("organic_results", []):
        link = item.get("link") or ""
        if "linkedin.com" not in link:
            continue
        posts.append(
            LinkedInPost(
                id=LinkedInPost.stable_id(link),
                url=link,
                title=item.get("title", "").strip(),
                snippet=item.get("snippet", "").strip(),
                source="serpapi",
                matched_keywords=[],
            )
        )
    return posts


async def _search_rapidapi(
    session: aiohttp.ClientSession,
    query: str,
    api_key: str,
    api_host: str,
) -> list[LinkedInPost]:
    """Use a RapidAPI-listed LinkedIn data API (host configurable)."""
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": api_host}
    params = {"keyword": query, "page": "1"}
    url = f"https://{api_host}/search/posts"
    async with session.get(url, headers=headers, params=params, timeout=30) as resp:
        if resp.status != 200:
            raise ProviderError(f"RapidAPI HTTP {resp.status}: {await resp.text()}")
        data = await resp.json()

    raw_items = data.get("data") or data.get("posts") or data.get("results") or []
    posts: list[LinkedInPost] = []
    for item in raw_items:
        link = item.get("postUrl") or item.get("url") or item.get("link")
        if not link:
            continue
        posts.append(
            LinkedInPost(
                id=LinkedInPost.stable_id(link),
                url=link,
                title=(item.get("title") or item.get("headline") or "").strip(),
                snippet=(item.get("text") or item.get("snippet") or "").strip(),
                author=(item.get("author") or {}).get("name")
                if isinstance(item.get("author"), dict)
                else item.get("author"),
                posted_at=item.get("postedAt") or item.get("date"),
                source="rapidapi",
                matched_keywords=[],
            )
        )
    return posts


async def _search_linkedin_official(
    session: aiohttp.ClientSession, query: str, access_token: str
) -> list[LinkedInPost]:
    """LinkedIn official Posts API. Requires partner-tier OAuth access."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    params = {"q": "keyword", "keywords": query, "count": "25"}
    async with session.get(
        "https://api.linkedin.com/v2/posts",
        headers=headers,
        params=params,
        timeout=30,
    ) as resp:
        if resp.status != 200:
            raise ProviderError(
                f"LinkedIn API HTTP {resp.status}: {await resp.text()}"
            )
        data = await resp.json()

    posts: list[LinkedInPost] = []
    for item in data.get("elements", []):
        urn = item.get("id", "")
        link = f"https://www.linkedin.com/feed/update/{urn}" if urn else ""
        if not link:
            continue
        commentary = (
            item.get("commentary")
            or item.get("specificContent", {})
            .get("com.linkedin.ugc.ShareContent", {})
            .get("shareCommentary", {})
            .get("text", "")
        )
        posts.append(
            LinkedInPost(
                id=LinkedInPost.stable_id(link),
                url=link,
                title="",
                snippet=commentary.strip(),
                author=item.get("author"),
                posted_at=item.get("createdAt"),
                source="linkedin",
                matched_keywords=[],
            )
        )
    return posts


# ─────────────────────────── Orchestration ────────────────────────────


class LinkedInDailyScraper:
    def __init__(
        self,
        provider: str | None = None,
        queries: Iterable[str] | None = None,
        output_dir: Path | None = None,
        run_hour_utc: int = 7,
    ) -> None:
        self.provider = (
            provider or os.getenv("LINKEDIN_SCRAPER_PROVIDER", "serpapi")
        ).lower()
        self.queries = list(queries or DEFAULT_QUERIES)
        self.output_dir = output_dir or Path(__file__).resolve().parents[2] / "data" / "linkedin"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.aggregate_path = self.output_dir / "all_posts.jsonl"
        self.run_hour_utc = run_hour_utc

    # ── provider dispatch ──
    async def _fetch_for_query(
        self, session: aiohttp.ClientSession, query: str
    ) -> list[LinkedInPost]:
        if self.provider == "serpapi":
            key = os.getenv("SERPAPI_KEY", "")
            if not key:
                raise ProviderError("SERPAPI_KEY is not set")
            return await _search_serpapi(session, query, key)

        if self.provider == "rapidapi":
            key = os.getenv("RAPIDAPI_KEY", "")
            host = os.getenv("RAPIDAPI_HOST", "linkedin-data-api.p.rapidapi.com")
            if not key:
                raise ProviderError("RAPIDAPI_KEY is not set")
            return await _search_rapidapi(session, query, key, host)

        if self.provider == "linkedin":
            token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
            if not token:
                raise ProviderError("LINKEDIN_ACCESS_TOKEN is not set")
            return await _search_linkedin_official(session, query, token)

        raise ProviderError(f"Unknown provider: {self.provider!r}")

    # ── filtering & dedup ──
    @staticmethod
    def _match_keywords(text: str) -> list[str]:
        low = text.lower()
        return sorted({kw for kw in RELEVANCE_KEYWORDS if kw in low})

    def _seen_urls(self) -> set[str]:
        if not self.aggregate_path.exists():
            return set()
        seen: set[str] = set()
        with self.aggregate_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    seen.add(json.loads(line)["url"])
                except Exception:
                    continue
        return seen

    # ── one collection cycle ──
    async def collect_once(self) -> list[LinkedInPost]:
        log.info("Cycle starting — provider=%s queries=%d", self.provider, len(self.queries))
        seen = self._seen_urls()
        results: dict[str, LinkedInPost] = {}

        async with aiohttp.ClientSession() as session:
            for query in self.queries:
                try:
                    posts = await self._fetch_for_query(session, query)
                except ProviderError as exc:
                    log.error("Provider error for %r: %s", query, exc)
                    return []
                except Exception as exc:
                    log.warning("Query %r failed: %s", query, exc)
                    continue

                for p in posts:
                    if p.url in seen or p.url in results:
                        continue
                    if not urlparse(p.url).netloc.endswith("linkedin.com"):
                        continue
                    matched = self._match_keywords(f"{p.title} {p.snippet}")
                    if not matched:
                        continue
                    p.matched_keywords = matched
                    results[p.url] = p

                # be polite — small gap between queries
                await asyncio.sleep(1.0)

        new_posts = list(results.values())
        log.info("Cycle complete — %d new relevant posts", len(new_posts))
        self._write(new_posts)
        return new_posts

    def _write(self, posts: list[LinkedInPost]) -> None:
        if not posts:
            return
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        daily_path = self.output_dir / f"{today}.jsonl"
        with daily_path.open("a", encoding="utf-8") as fh, self.aggregate_path.open(
            "a", encoding="utf-8"
        ) as agg:
            for p in posts:
                line = json.dumps(asdict(p), ensure_ascii=False)
                fh.write(line + "\n")
                agg.write(line + "\n")
        log.info("Wrote %d posts to %s", len(posts), daily_path)

    # ── daemon loop ──
    def _seconds_until_next_run(self) -> float:
        now = datetime.now(timezone.utc)
        target = datetime.combine(
            now.date(), time(hour=self.run_hour_utc, tzinfo=timezone.utc)
        )
        if target <= now:
            target += timedelta(days=1)
        return (target - now).total_seconds()

    async def run_forever(self) -> None:
        log.info("Daemon up — will run daily at %02d:00 UTC", self.run_hour_utc)
        while True:
            try:
                await self.collect_once()
            except Exception:
                log.exception("Unhandled error during cycle")
            wait_s = self._seconds_until_next_run()
            log.info("Sleeping %.1f hours until next run", wait_s / 3600)
            await asyncio.sleep(wait_s)


# ────────────────────────────── CLI ───────────────────────────────────


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument("--once", action="store_true", help="Run a single cycle and exit")
    p.add_argument(
        "--provider",
        choices=("serpapi", "rapidapi", "linkedin"),
        help="Override LINKEDIN_SCRAPER_PROVIDER",
    )
    p.add_argument(
        "--hour",
        type=int,
        default=int(os.getenv("LINKEDIN_SCRAPER_HOUR_UTC", "7")),
        help="UTC hour-of-day to run (default 07:00 UTC)",
    )
    return p.parse_args(argv)


async def _amain(argv: list[str]) -> int:
    args = _parse_args(argv)
    scraper = LinkedInDailyScraper(provider=args.provider, run_hour_utc=args.hour)
    if args.once:
        await scraper.collect_once()
        return 0
    await scraper.run_forever()
    return 0


def main() -> int:
    return asyncio.run(_amain(sys.argv[1:]))


if __name__ == "__main__":
    raise SystemExit(main())
