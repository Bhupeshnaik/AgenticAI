"""
LinkedIn Daily Scraper (SerpAPI)
================================

Continuously runs once every 24 hours and collects LinkedIn posts that
discuss:

  * Domain-Driven Design (DDD)
  * Industry-domain agentic AI solutions
  * Real-world success stories of agentic deployments in industry

Legality
--------
Direct scraping of LinkedIn HTML violates LinkedIn's User Agreement §8.2.
This collector uses SerpAPI to query Google with ``site:linkedin.com/posts``
— a lawful, indexed source. Requires ``SERPAPI_KEY`` in the environment.

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
import html
import json
import logging
import os
import smtplib
import ssl
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, time, timedelta, timezone
from email.message import EmailMessage
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
    matched_keywords: list[str]
    source: str = "serpapi"
    author: str | None = None
    posted_at: str | None = None
    fetched_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @staticmethod
    def stable_id(url: str) -> str:
        return hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]


class ProviderError(RuntimeError):
    pass


async def _search_serpapi(
    session: aiohttp.ClientSession, query: str, api_key: str
) -> list[LinkedInPost]:
    """Google-search ``site:linkedin.com/posts <query>`` via SerpAPI."""
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
                matched_keywords=[],
            )
        )
    return posts


class LinkedInDailyScraper:
    def __init__(
        self,
        queries: Iterable[str] | None = None,
        output_dir: Path | None = None,
        run_hour_utc: int = 7,
        email_enabled: bool = True,
    ) -> None:
        self.queries = list(queries or DEFAULT_QUERIES)
        self.output_dir = output_dir or Path(__file__).resolve().parents[2] / "data" / "linkedin"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.aggregate_path = self.output_dir / "all_posts.jsonl"
        self.run_hour_utc = run_hour_utc
        self.email_enabled = email_enabled

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

    async def collect_once(self) -> list[LinkedInPost]:
        api_key = os.getenv("SERPAPI_KEY", "")
        if not api_key:
            log.error("SERPAPI_KEY is not set — cannot run cycle")
            return []

        log.info("Cycle starting — queries=%d", len(self.queries))
        seen = self._seen_urls()
        results: dict[str, LinkedInPost] = {}

        async with aiohttp.ClientSession() as session:
            for query in self.queries:
                try:
                    posts = await _search_serpapi(session, query, api_key)
                except ProviderError as exc:
                    log.error("SerpAPI error for %r: %s", query, exc)
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

                await asyncio.sleep(1.0)

        new_posts = list(results.values())
        log.info("Cycle complete — %d new relevant posts", len(new_posts))
        self._write(new_posts)
        if self.email_enabled and new_posts:
            try:
                self._send_email_digest(new_posts)
            except Exception:
                log.exception("Failed to send email digest")
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

    @staticmethod
    def _render_digest(posts: list[LinkedInPost]) -> tuple[str, str, str]:
        """Return (subject, text_body, html_body) for the digest email."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        subject = f"LinkedIn DDD / Agentic AI digest — {today} ({len(posts)} posts)"

        text_lines = [
            f"LinkedIn daily digest — {today} UTC",
            f"{len(posts)} new posts matching DDD / agentic-AI keywords.",
            "",
        ]
        html_rows: list[str] = []
        for i, p in enumerate(posts, 1):
            kws = ", ".join(p.matched_keywords) or "—"
            text_lines.append(f"[{i}] {p.title or '(no title)'}")
            text_lines.append(f"    keywords: {kws}")
            text_lines.append(f"    {p.snippet}")
            text_lines.append(f"    {p.url}")
            text_lines.append("")
            html_rows.append(
                "<li style='margin-bottom:18px'>"
                f"<a href='{html.escape(p.url)}'><b>{html.escape(p.title or '(no title)')}</b></a>"
                f"<div style='color:#555;font-size:12px'>keywords: {html.escape(kws)}</div>"
                f"<div>{html.escape(p.snippet)}</div>"
                "</li>"
            )

        html_body = (
            "<html><body style='font-family:Arial,sans-serif;font-size:14px'>"
            f"<h2>LinkedIn daily digest — {today} UTC</h2>"
            f"<p>{len(posts)} new posts matching DDD / agentic-AI keywords.</p>"
            f"<ol>{''.join(html_rows)}</ol>"
            "</body></html>"
        )
        return subject, "\n".join(text_lines), html_body

    def _send_email_digest(self, posts: list[LinkedInPost]) -> None:
        host = os.getenv("SMTP_HOST")
        port = int(os.getenv("SMTP_PORT", "587"))
        user = os.getenv("SMTP_USER")
        password = os.getenv("SMTP_PASSWORD")
        sender = os.getenv("SMTP_FROM", user or "")
        recipient = os.getenv("SMTP_TO", "bhupeshnaik@gmail.com")

        if not (host and user and password and sender):
            log.warning(
                "SMTP not fully configured — skipping email "
                "(need SMTP_HOST, SMTP_USER, SMTP_PASSWORD, SMTP_FROM)"
            )
            return

        subject, text_body, html_body = self._render_digest(posts)
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient
        msg.set_content(text_body)
        msg.add_alternative(html_body, subtype="html")

        ctx = ssl.create_default_context()
        if port == 465:
            with smtplib.SMTP_SSL(host, port, context=ctx, timeout=30) as smtp:
                smtp.login(user, password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=30) as smtp:
                smtp.starttls(context=ctx)
                smtp.login(user, password)
                smtp.send_message(msg)
        log.info("Emailed digest to %s (%d posts)", recipient, len(posts))

    def send_test_email(self) -> None:
        """Send a one-off email with a synthetic post to verify SMTP wiring."""
        demo = LinkedInPost(
            id="test",
            url="https://www.linkedin.com/posts/example",
            title="Test post — domain-driven agentic AI case study",
            snippet="This is a test digest entry to verify SMTP delivery.",
            matched_keywords=["domain-driven", "agentic", "case study"],
        )
        self._send_email_digest([demo])

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


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="LinkedIn daily scraper (SerpAPI)")
    p.add_argument("--once", action="store_true", help="Run a single cycle and exit")
    p.add_argument("--no-email", action="store_true", help="Skip email digest")
    p.add_argument(
        "--test-email",
        action="store_true",
        help="Send a synthetic digest to verify SMTP and exit",
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
    scraper = LinkedInDailyScraper(
        run_hour_utc=args.hour, email_enabled=not args.no_email
    )
    if args.test_email:
        scraper.send_test_email()
        return 0
    if args.once:
        await scraper.collect_once()
        return 0
    await scraper.run_forever()
    return 0


def main() -> int:
    return asyncio.run(_amain(sys.argv[1:]))


if __name__ == "__main__":
    raise SystemExit(main())
