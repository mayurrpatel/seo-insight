"""
Asynchronous Website Crawler with SSRF Protection, Robots.txt compliance,
and domain isolation.
"""

import asyncio
import time
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup
import httpx

from .ssrf import validate_url_ssrf
from .robots import RobotsHandler


def normalize_domain(netloc: str) -> str:
    """Normalize domain by removing port and optional 'www.' prefix for comparison."""
    host = netloc.split(":")[0].lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def is_same_domain(url1: str, url2: str) -> bool:
    """Check if two URLs belong to the same registered domain."""
    d1 = normalize_domain(urlparse(url1).netloc)
    d2 = normalize_domain(urlparse(url2).netloc)
    return d1 == d2


class PageCrawlResult:
    def __init__(self, url: str):
        self.url = url
        self.final_url = url
        self.status_code: int | None = None
        self.response_time_ms: float = 0.0
        self.content_type: str = ""
        self.html: str = ""
        self.headers: dict[str, str] = {}
        self.redirect_history: list[dict] = []
        self.internal_links: list[str] = []
        self.external_links: list[str] = []
        self.error: str | None = None
        self.is_html: bool = False


class WebsiteCrawler:
    def __init__(
        self,
        start_url: str,
        max_pages: int = 15,
        timeout: float = 8.0,
        user_agent: str = "SEOInsightBot/1.0 (+https://seoinsight.local/bot)",
        allow_test_local: bool = False,
    ):
        self.start_url = start_url.strip()
        self.max_pages = min(max(1, max_pages), 30)
        self.timeout = timeout
        self.user_agent = user_agent
        self.allow_test_local = allow_test_local

        self.pages_discovered = 0
        self.pages_scanned = 0
        self.pages_failed = 0
        self.current_url: str | None = None
        self.status = "idle"  # idle, crawling, completed, failed
        self.status_message = "Ready"

        self.scanned_pages: dict[str, PageCrawlResult] = {}
        self.to_crawl: list[str] = []
        self.seen_urls: set[str] = set()
        self.robots_handler: RobotsHandler | None = None
        self.sitemap_found: bool = False
        self.sitemap_url: str | None = None
        self.broken_external_links: dict[str, int] = {}  # url -> status_code

    def clean_url(self, url: str) -> str:
        """Strip fragment and trailing slash normalization."""
        clean, _ = urldefrag(url)
        return clean.strip()

    async def check_sitemap(self, client: httpx.AsyncClient, base_url: str) -> None:
        """Check for standard /sitemap.xml if not discovered in robots.txt."""
        parsed = urlparse(base_url)
        sitemap_target = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
        is_safe, _ = validate_url_ssrf(sitemap_target, allow_test_local=self.allow_test_local)
        if not is_safe:
            return

        try:
            resp = await client.get(sitemap_target, timeout=4.0, follow_redirects=True)
            if resp.status_code == 200 and ("xml" in resp.headers.get("content-type", "") or "<urlset" in resp.text[:200]):
                self.sitemap_found = True
                self.sitemap_url = str(resp.url)
        except Exception:
            pass

    async def verify_external_link(self, client: httpx.AsyncClient, url: str) -> bool:
        """
        Safely check an external link.
        Returns True if working (2xx or 3xx), False if broken (4xx, 5xx, or network error).
        """
        is_safe, _ = validate_url_ssrf(url, allow_test_local=self.allow_test_local)
        if not is_safe:
            return True  # Skip SSRF-unsafe external urls from broken list to avoid scanning internal resources

        try:
            # First try HEAD request
            resp = await client.head(url, timeout=4.0, follow_redirects=True)
            if resp.status_code >= 400 and resp.status_code not in (403, 405):
                # Retry with GET in case HEAD is not allowed
                resp = await client.get(url, timeout=4.0, follow_redirects=True)
            if resp.status_code >= 400:
                self.broken_external_links[url] = resp.status_code
                return False
            return True
        except Exception:
            self.broken_external_links[url] = 0  # Connection error / DNS failure
            return False

    async def crawl(self) -> dict[str, PageCrawlResult]:
        """Perform the crawl of the target domain."""
        self.status = "crawling"
        self.status_message = "Validating target URL..."

        is_safe, err_msg = validate_url_ssrf(self.start_url, allow_test_local=self.allow_test_local)
        if not is_safe:
            self.status = "failed"
            self.status_message = f"SSRF Validation Blocked: {err_msg}"
            raise ValueError(f"Security validation failed: {err_msg}")

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        async with httpx.AsyncClient(headers=headers, follow_redirects=False, verify=False) as client:
            # 1. Fetch robots.txt
            self.status_message = "Checking robots.txt and sitemap directives..."
            self.robots_handler = RobotsHandler(self.start_url, user_agent=self.user_agent, allow_test_local=self.allow_test_local)
            await self.robots_handler.fetch(client)

            if self.robots_handler.sitemaps:
                self.sitemap_found = True
                self.sitemap_url = self.robots_handler.sitemaps[0]
            else:
                await self.check_sitemap(client, self.start_url)

            # Check if start URL is allowed by robots.txt
            if not self.robots_handler.is_allowed(self.start_url):
                self.status = "failed"
                self.status_message = f"Crawling blocked by robots.txt for: {self.start_url}"
                raise PermissionError(f"Crawl prohibited by website robots.txt rules for {self.start_url}")

            # 2. Initialize crawl queue
            cleaned_start = self.clean_url(self.start_url)
            self.to_crawl.append(cleaned_start)
            self.seen_urls.add(cleaned_start)
            self.pages_discovered = 1

            external_links_to_check: set[str] = set()

            while self.to_crawl and self.pages_scanned < self.max_pages:
                current_url = self.to_crawl.pop(0)
                self.current_url = current_url
                self.status_message = f"Crawling {self.pages_scanned + 1}/{self.max_pages}: {current_url}"

                # Recheck robots rule for each page
                if not self.robots_handler.is_allowed(current_url):
                    continue

                page_res = PageCrawlResult(current_url)
                t_start = time.perf_counter()

                try:
                    # Handle redirects manually to track hops and validate SSRF on each hop
                    curr_req_url = current_url
                    redirect_hops = 0
                    max_redirects = 5

                    while redirect_hops <= max_redirects:
                        # Validate each hop for SSRF
                        is_safe_hop, hop_err = validate_url_ssrf(curr_req_url, allow_test_local=self.allow_test_local)
                        if not is_safe_hop:
                            raise ValueError(f"Redirect blocked by SSRF check: {hop_err}")

                        resp = await client.get(curr_req_url, timeout=self.timeout)
                        page_res.status_code = resp.status_code

                        # Check for redirect status
                        if resp.is_redirect and "location" in resp.headers:
                            next_loc = resp.headers["location"]
                            next_url = urljoin(curr_req_url, next_loc)
                            page_res.redirect_history.append({
                                "from": curr_req_url,
                                "to": next_url,
                                "status": resp.status_code
                            })
                            redirect_hops += 1
                            curr_req_url = next_url
                        else:
                            page_res.final_url = curr_req_url
                            page_res.content_type = resp.headers.get("content-type", "")
                            page_res.headers = dict(resp.headers)
                            if "text/html" in page_res.content_type.lower() or "<html" in resp.text[:200].lower():
                                page_res.is_html = True
                                page_res.html = resp.text
                            break

                    if redirect_hops > max_redirects:
                        page_res.error = f"Excessive redirects: exceeded {max_redirects} hops"

                except Exception as e:
                    page_res.error = str(e)
                    self.pages_failed += 1

                page_res.response_time_ms = round((time.perf_counter() - t_start) * 1000, 1)
                self.scanned_pages[current_url] = page_res
                self.pages_scanned += 1

                # If HTML, extract links
                if page_res.is_html and page_res.html:
                    try:
                        soup = BeautifulSoup(page_res.html, "html.parser")
                        for a_tag in soup.find_all("a", href=True):
                            raw_href = a_tag["href"].strip()
                            if not raw_href or raw_href.startswith(("javascript:", "mailto:", "tel:", "#")):
                                continue

                            abs_link = urljoin(page_res.final_url, raw_href)
                            cleaned_link = self.clean_url(abs_link)

                            if is_same_domain(self.start_url, cleaned_link):
                                page_res.internal_links.append(cleaned_link)
                                if cleaned_link not in self.seen_urls and len(self.seen_urls) < 100:
                                    self.seen_urls.add(cleaned_link)
                                    self.to_crawl.append(cleaned_link)
                                    self.pages_discovered += 1
                            else:
                                if cleaned_link.startswith(("http://", "https://")):
                                    page_res.external_links.append(cleaned_link)
                                    if len(external_links_to_check) < 10:
                                        external_links_to_check.add(cleaned_link)
                    except Exception as parse_err:
                        # Non-fatal HTML parsing error
                        pass

                # Polite delay
                await asyncio.sleep(0.05)

            # Sample external links verification
            if external_links_to_check:
                self.status_message = "Verifying external link health..."
                for ext_url in list(external_links_to_check)[:8]:
                    await self.verify_external_link(client, ext_url)

        self.status = "completed"
        self.status_message = f"Crawl complete. Scanned {self.pages_scanned} pages."
        return self.scanned_pages
