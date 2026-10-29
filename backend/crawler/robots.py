"""
Robots.txt parser and policy checker.
"""

from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
import httpx
from .ssrf import validate_url_ssrf


class RobotsHandler:
    def __init__(self, base_url: str, user_agent: str = "SEOInsightBot/1.0", allow_test_local: bool = False):
        self.base_url = base_url
        self.user_agent = user_agent
        self.allow_test_local = allow_test_local
        self.parsed_base = urlparse(base_url)
        self.robots_url = f"{self.parsed_base.scheme}://{self.parsed_base.netloc}/robots.txt"
        self.rp = RobotFileParser()
        self.found = False
        self.status_code = None
        self.sitemaps: list[str] = []
        self.content = ""
        self.error_message: str | None = None

    async def fetch(self, client: httpx.AsyncClient) -> None:
        """Fetch and parse robots.txt for the given domain."""
        is_safe, err = validate_url_ssrf(self.robots_url, allow_test_local=self.allow_test_local)
        if not is_safe:
            self.error_message = f"SSRF check failed for robots.txt: {err}"
            return

        try:
            resp = await client.get(self.robots_url, timeout=5.0, follow_redirects=True)
            self.status_code = resp.status_code
            if resp.status_code == 200:
                self.found = True
                self.content = resp.text
                lines = self.content.splitlines()
                self.rp.parse(lines)
                for line in lines:
                    line_clean = line.strip()
                    if line_clean.lower().startswith("sitemap:"):
                        parts = line_clean.split(":", 1)
                        if len(parts) > 1:
                            sitemap_url = parts[1].strip()
                            if sitemap_url:
                                self.sitemaps.append(sitemap_url)
            else:
                self.found = False
        except Exception as e:
            self.found = False
            self.error_message = str(e)

    def is_allowed(self, target_url: str) -> bool:
        """Check if user-agent is permitted to crawl target_url."""
        if not self.found:
            # If no robots.txt exists, standard crawling is allowed
            return True
        try:
            return self.rp.can_fetch(self.user_agent, target_url)
        except Exception:
            return True
