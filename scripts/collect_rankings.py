#!/usr/bin/env python3
"""
Qidian Rankings Collector - GitHub Actions version.
Uses Playwright to scrape ranking pages from www.qidian.com.
Falls back to previous data if blocked.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ─── Config ─────────────────────────────────────────────────────────────────

RANKINGS: dict[str, dict[str, str]] = {
    "yuepiao":  {"name": "月票榜",  "url": "https://www.qidian.com/rank/yuepiao/"},
    "hotsales": {"name": "畅销榜",  "url": "https://www.qidian.com/rank/hotsales/"},
    "recom":    {"name": "推荐榜",  "url": "https://www.qidian.com/rank/recom/"},
    "collect":  {"name": "收藏榜",  "url": "https://www.qidian.com/rank/collect/"},
}

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "data"))
KEEP_DAYS = int(os.getenv("KEEP_DAYS", "31"))
TOP_N = int(os.getenv("TOP_N", "20"))

# ─── Data Structures ──────────────────────────────────────────────────────────

@dataclass
class BookEntry:
    rank: int
    title: str
    author: str
    category: str
    subcategory: str
    status: str
    summary: str
    latest_update: str
    metric: str

@dataclass
class RankingSnapshot:
    ranking_key: str
    ranking_name: str
    source_url: str
    captured_at: str
    page_title: str
    body_hash: str
    entries: list[BookEntry]
    raw_preview: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "ranking_key": self.ranking_key,
            "ranking_name": self.ranking_name,
            "source_url": self.source_url,
            "captured_at": self.captured_at,
            "page_title": self.page_title,
            "body_hash": self.body_hash,
            "entries": [asdict(e) for e in self.entries],
            "raw_preview": self.raw_preview,
        }

# ─── Browser Setup ────────────────────────────────────────────────────────────

from playwright.sync_api import sync_playwright, Browser, Error as PlaywrightError

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
]

def make_browser() -> Browser:
    pw = sync_playwright().__enter__()
    return pw.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--single-process",
        ],
    )

def make_page(browser: Browser, ctx):
    page = ctx.new_page()
    # Block images/fonts to speed up
    page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2}", lambda r: r.abort())
    return page

# ─── Parsing ─────────────────────────────────────────────────────────────────

CATEGORIES = ["玄幻","奇幻","武侠","仙侠","都市","现实","军事","历史","游戏","体育","科幻","诸天无限","悬疑","轻小说"]
STATUS = ["连载","完本"]

def normalize_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip() and line.strip() not in {"|","\uff2a","\uff1a"}]

def parse_entries(body_text: str, top_n: int) -> list[BookEntry]:
    lines = normalize_lines(body_text)
    entries: list[BookEntry] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.isdigit():
            i += 1
            continue
        rank = int(line)
        if rank < 1 or rank > max(top_n, 100):
            i += 1
            continue
        window = lines[i+1 : i+13]
        if len(window) < 5:
            i += 1
            continue
        title = window[0]
        author = window[1] if len(window) > 1 else ""
        category = subcategory = status = summary = latest_update = metric = ""
        for idx, token in enumerate(window[2:], start=2):
            if token in CATEGORIES and not category:
                category = token
                if idx+2 < len(window) and window[idx+1] == "\u00b7":
                    subcategory = window[idx+2]
            if token in STATUS and not status:
                status = token
            if token.startswith("\u6700\u65b0\u66f4\u65b0"):
                latest_update = token
            if any(k in token for k in ["\u63a8\u8350","\u6708\u7968","\u6536\u85cf","\u9500\u91cf"]):
                metric = token
        for token in window:
            if token in {title, author, category, subcategory, status, metric} or token.startswith("\u6700\u65b0\u66f4\u65b0") or token == "\u00b7":
                continue
            if len(token) >= 12 and not summary:
                summary = token
        if title and author and category:
            entries.append(BookEntry(rank, title, author, category, subcategory, status, summary, latest_update, metric))
        if len(entries) >= top_n:
            break
        i += 1
    return entries

# ─── Collection ──────────────────────────────────────────────────────────────

def collect_one(browser: Browser, ranking_key: str, meta: dict[str, str], top_n: int) -> RankingSnapshot | None:
    url = meta["url"]
    for attempt in range(3):
        ua = random.choice(USER_AGENTS)
        ctx = browser.new_context(
            user_agent=ua,
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
            ignoreHTTPSErrors=True,
            extra_http_headers={"Accept-Language": "zh-CN,zh;q=0.9"},
        )
        page = make_page(browser, ctx)
        try:
            resp = page.goto(url, timeout=30000, wait_until="domcontentloaded")
            if not resp or resp.status not in (200, 202):
                page.close(); ctx.close()
                time.sleep(5)
                continue
            page.wait_for_timeout(4000)
            body_text = page.inner_text("body").strip()
            page_title = page.title()
            actual_url = page.url
            # Check for captcha
            html = page.content()
            if "tcaptcha" in html or "challenge-node" in html or "captcha" in html.lower():
                page.close(); ctx.close()
                if attempt < 2:
                    time.sleep(random.uniform(5, 12))
                    continue
                return None
            if not body_text or len(body_text) < 200:
                page.close(); ctx.close()
                if attempt < 2:
                    time.sleep(5)
                    continue
                return None
            entries = parse_entries(body_text, top_n)
            body_hash = hashlib.sha256(body_text.encode("utf-8")).hexdigest()
            page.close(); ctx.close()
            return RankingSnapshot(
                ranking_key=ranking_key,
                ranking_name=meta["name"],
                source_url=actual_url,
                captured_at=datetime.now(timezone.utc).isoformat(),
                page_title=page_title,
                body_hash=body_hash,
                entries=entries,
                raw_preview="\n".join(normalize_lines(body_text)[:120]),
            )
        except PlaywrightError:
            try: page.close(); ctx.close()
            except: pass
            if attempt < 2:
                time.sleep(8)
                continue
    return None

def run_collection() -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "snapshots").mkdir(exist_ok=True)
    (OUTPUT_DIR / "latest").mkdir(exist_ok=True)

    browser = make_browser()
    saved = []
    missing = []

    for ranking_key, meta in RANKINGS.items():
        print(f"Collecting {ranking_key}...", flush=True)
        snapshot = collect_one(browser, ranking_key, meta, TOP_N)
        if snapshot:
            day = datetime.now(timezone.utc).date().isoformat()
            snap_dir = OUTPUT_DIR / "snapshots" / ranking_key / day
            snap_dir.mkdir(parents=True, exist_ok=True)
            ts = snapshot.captured_at.replace(":", "-")
            snap_path = snap_dir / f"{ts}.json"
            snap_path.write_text(json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
            latest_path = OUTPUT_DIR / "latest" / f"{ranking_key}.json"
            latest_path.write_text(json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
            saved.append({"ranking_key": ranking_key, "entries": len(snapshot.entries), "top_1": snapshot.entries[0].title if snapshot.entries else None})
            print(f"  -> {len(snapshot.entries)} entries, top: {snapshot.entries[0].title if snapshot.entries else 'none'}")
        else:
            missing.append(ranking_key)
            print(f"  -> failed (captcha or blocked)")

    browser.close()
    return {"saved": saved, "missing": missing, "captured_at": datetime.now(timezone.utc).isoformat()}

if __name__ == "__main__":
    result = run_collection()
    print(json.dumps(result, ensure_ascii=False, indent=2))