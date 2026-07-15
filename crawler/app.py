from __future__ import annotations

import asyncio
import ipaddress
import os
import socket
from contextlib import asynccontextmanager
from typing import Any
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from playwright.async_api import Browser, async_playwright

MAX_URLS_PER_REQUEST = 5
MAX_TEXT_LENGTH = 80_000


class CrawlRequest(BaseModel):
    urls: list[str] = Field(min_length=1, max_length=MAX_URLS_PER_REQUEST)
    crawler_config: dict[str, Any] = Field(default_factory=dict)


def is_public_http_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(parsed.hostname, None)}
        return bool(addresses) and all(ipaddress.ip_address(address).is_global for address in addresses)
    except (OSError, ValueError):
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    playwright = await async_playwright().start()
    app.state.browser = await playwright.chromium.launch()
    app.state.crawl_limit = asyncio.Semaphore(int(os.environ.get("CRAWLER_CONCURRENCY", "2")))
    try:
        yield
    finally:
        await app.state.browser.close()
        await playwright.stop()


app = FastAPI(title="AiYX Internal Crawler", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/crawl")
async def crawl(request: CrawlRequest) -> list[dict[str, Any]]:
    invalid_urls = [url for url in request.urls if not is_public_http_url(url)]
    if invalid_urls:
        raise HTTPException(status_code=400, detail="Only publicly routable HTTP(S) URLs can be crawled")

    results = await asyncio.gather(*(crawl_one(url) for url in request.urls), return_exceptions=True)
    return [result if isinstance(result, dict) else {"url": url, "error": str(result)} for url, result in zip(request.urls, results)]


async def crawl_one(url: str) -> dict[str, Any]:
    browser: Browser = app.state.browser
    async with app.state.crawl_limit:
        context = await browser.new_context(user_agent="AiYX-DATA-INTELI/1.0")
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            await page.wait_for_timeout(500)
            title = await page.title()
            description_locator = page.locator('meta[name="description"]')
            description = await description_locator.get_attribute("content") if await description_locator.count() else ""
            text = await page.locator("body").inner_text()
            return {
                "url": page.url,
                "markdown": text[:MAX_TEXT_LENGTH],
                "metadata": {"url": page.url, "title": title, "description": description},
            }
        finally:
            await context.close()
