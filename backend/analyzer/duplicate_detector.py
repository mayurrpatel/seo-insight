"""
Cross-Page Duplicate Content and Site-Wide SEO Rule Checker.
"""

from collections import defaultdict
from bs4 import BeautifulSoup
from .seo_rules import SEOIssue


def analyze_cross_page_issues(crawler, scanned_pages: dict) -> list[SEOIssue]:
    """
    Check site-wide issues across all crawled pages:
    - Duplicate Titles
    - Duplicate Meta Descriptions
    - Missing robots.txt
    - Missing sitemap.xml
    - Broken External Links
    """
    issues: list[SEOIssue] = []

    # 1. Site-wide robots.txt check
    if crawler.robots_handler and not crawler.robots_handler.found:
        issues.append(SEOIssue(
            id=f"site-robots-missing-{hash(crawler.start_url) & 0xfffffff}",
            rule_id="ROBOTS_TXT_MISSING",
            title="Missing robots.txt File",
            category="Indexability & Crawling",
            severity="Medium",
            priority_score=60,
            affected_url=crawler.robots_handler.robots_url,
            evidence=f"No valid robots.txt found at {crawler.robots_handler.robots_url} (HTTP {crawler.robots_handler.status_code or 'Failed'}).",
            impact="Search engine crawlers rely on robots.txt for crawl instructions, rate limits, and finding sitemap files.",
            suggested_fix="Create and publish a robots.txt file at the root of your domain specifying crawl rules and linking your sitemap.xml."
        ))

    # 2. Site-wide sitemap.xml check
    if not crawler.sitemap_found:
        issues.append(SEOIssue(
            id=f"site-sitemap-missing-{hash(crawler.start_url) & 0xfffffff}",
            rule_id="SITEMAP_XML_MISSING",
            title="Missing XML Sitemap",
            category="Indexability & Crawling",
            severity="High",
            priority_score=75,
            affected_url=f"{crawler.start_url.rstrip('/')}/sitemap.xml",
            evidence="No XML sitemap referenced in robots.txt and standard /sitemap.xml returned 404 or was missing.",
            impact="XML sitemaps help search engines discover deep or newly published URLs quickly and understand site hierarchy.",
            suggested_fix="Generate an XML sitemap complying with the sitemaps.org protocol and submit it to Google Search Console."
        ))

    # 3. Cross-page duplicate title & meta description maps
    titles_map = defaultdict(list)
    desc_map = defaultdict(list)

    for url, res in scanned_pages.items():
        if res.is_html and res.html and res.status_code and res.status_code < 400:
            try:
                soup = BeautifulSoup(res.html, "html.parser")
                t_tag = soup.find("title")
                if t_tag and t_tag.string and t_tag.string.strip():
                    cleaned_t = " ".join(t_tag.string.split()).lower()
                    titles_map[cleaned_t].append(url)

                d_tag = soup.find("meta", attrs={"name": lambda x: x and x.lower() == "description"})
                if d_tag and d_tag.get("content", "").strip():
                    cleaned_d = " ".join(d_tag.get("content").split()).lower()
                    desc_map[cleaned_d].append(url)
            except Exception:
                pass

    # Flag duplicate titles
    for title_text, urls in titles_map.items():
        if len(urls) > 1:
            sample_urls = ", ".join(urls[:3])
            for u in urls:
                issues.append(SEOIssue(
                    id=f"dup-title-{hash(u + title_text) & 0xfffffff}",
                    rule_id="DUPLICATE_TITLE_TAG",
                    title="Duplicate Page Title Across Multiple URLs",
                    category="Meta Tags",
                    severity="High",
                    priority_score=78,
                    affected_url=u,
                    affected_count=len(urls),
                    evidence=f"Shared title '{title_text[:60]}' appears on {len(urls)} pages: {sample_urls}",
                    impact="Identical title tags force pages to compete against each other for rankings (keyword cannibalization) and reduce CTR.",
                    suggested_fix="Craft a unique, specific title tag for each distinct URL highlighting its distinct value."
                ))

    # Flag duplicate descriptions
    for desc_text, urls in desc_map.items():
        if len(urls) > 1:
            sample_urls = ", ".join(urls[:3])
            for u in urls:
                issues.append(SEOIssue(
                    id=f"dup-desc-{hash(u + desc_text) & 0xfffffff}",
                    rule_id="DUPLICATE_META_DESCRIPTION",
                    title="Duplicate Meta Description",
                    category="Meta Tags",
                    severity="Medium",
                    priority_score=55,
                    affected_url=u,
                    affected_count=len(urls),
                    evidence=f"Identical meta description used on {len(urls)} pages: {sample_urls}",
                    impact="Duplicate descriptions provide poor user search snippets and are frequently replaced by Google with arbitrary text.",
                    suggested_fix="Write unique meta descriptions tailored to the specific content and call-to-action of each page."
                ))

    # 4. Broken External Links
    if crawler.broken_external_links:
        for ext_url, code in crawler.broken_external_links.items():
            status_text = f"HTTP {code}" if code > 0 else "Connection/DNS Failure"
            issues.append(SEOIssue(
                id=f"ext-broken-{hash(ext_url) & 0xfffffff}",
                rule_id="EXTERNAL_BROKEN_LINK",
                title="Broken External Link",
                category="Links & Navigation",
                severity="Medium",
                priority_score=58,
                affected_url=ext_url,
                evidence=f"External link failed with: {status_text}",
                impact="Outbound broken links degrade user experience and signal outdated or unmaintained web content to search engines.",
                suggested_fix="Replace with a working resource URL or remove the broken link from your pages."
            ))

    return issues
