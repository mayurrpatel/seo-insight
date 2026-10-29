"""
Crawler link extraction and domain boundary tests.
"""

from crawler.crawler import WebsiteCrawler, is_same_domain, normalize_domain
from bs4 import BeautifulSoup


def test_domain_normalization_and_matching():
    assert normalize_domain("example.com") == "example.com"
    assert normalize_domain("www.example.com") == "example.com"
    assert normalize_domain("example.com:8080") == "example.com"
    assert is_same_domain("https://example.com/page1", "https://www.example.com/page2") is True
    assert is_same_domain("https://example.com/page1", "https://otherdomain.com/page1") is False


def test_crawler_link_filtering():
    crawler = WebsiteCrawler(start_url="https://example.com")
    html = """
    <html>
        <body>
            <a href="/about">About Us</a>
            <a href="https://example.com/pricing">Pricing</a>
            <a href="https://other.com/partner">Partner</a>
            <a href="javascript:void(0)">Click</a>
            <a href="mailto:support@example.com">Email</a>
            <a href="#section">Section</a>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    internal_links = []
    external_links = []

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("javascript:", "mailto:", "tel:", "#")):
            continue
        from urllib.parse import urljoin
        abs_url = urljoin("https://example.com/home", href)
        cleaned = crawler.clean_url(abs_url)
        if is_same_domain("https://example.com", cleaned):
            internal_links.append(cleaned)
        else:
            external_links.append(cleaned)

    assert "https://example.com/about" in internal_links
    assert "https://example.com/pricing" in internal_links
    assert "https://other.com/partner" in external_links
    assert len(internal_links) == 2
    assert len(external_links) == 1
