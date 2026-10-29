"""
Unit tests for SEO issue detection rules.
"""

from analyzer.seo_rules import PageAnalyzer
from crawler.crawler import PageCrawlResult


def create_mock_page(url: str, html: str, status_code: int = 200) -> PageCrawlResult:
    res = PageCrawlResult(url)
    res.status_code = status_code
    res.is_html = True
    res.html = html
    res.content_type = "text/html; charset=utf-8"
    return res


def test_missing_title_tag():
    html = "<html><head></head><body><h1>Hello World</h1></body></html>"
    page = create_mock_page("https://example.com/test", html)
    analyzer = PageAnalyzer("https://example.com/test", page, {})
    issues = analyzer.analyze()

    rule_ids = [i.rule_id for i in issues]
    assert "TITLE_TAG_MISSING" in rule_ids
    crit_issues = [i for i in issues if i.rule_id == "TITLE_TAG_MISSING"]
    assert crit_issues[0].severity == "Critical"


def test_short_and_long_title_tags():
    # Short
    html_short = "<html><head><title>Tiny</title></head><body></body></html>"
    page_short = create_mock_page("https://example.com/short", html_short)
    issues_short = PageAnalyzer("https://example.com/short", page_short, {}).analyze()
    assert "TITLE_TAG_TOO_SHORT" in [i.rule_id for i in issues_short]

    # Long
    html_long = f"<html><head><title>{'A' * 70}</title></head><body></body></html>"
    page_long = create_mock_page("https://example.com/long", html_long)
    issues_long = PageAnalyzer("https://example.com/long", page_long, {}).analyze()
    assert "TITLE_TAG_TOO_LONG" in [i.rule_id for i in issues_long]


def test_missing_meta_description():
    html = "<html><head><title>Valid Title Here for Testing SEO Rules</title></head><body><h1>Hi</h1></body></html>"
    page = create_mock_page("https://example.com/test", html)
    issues = PageAnalyzer("https://example.com/test", page, {}).analyze()
    assert "META_DESCRIPTION_MISSING" in [i.rule_id for i in issues]


def test_h1_tags():
    # Missing H1
    html_no_h1 = "<html><head><title>A Valid Title Here for Testing</title></head><body><h2>Subheading</h2></body></html>"
    issues_no_h1 = PageAnalyzer("https://example.com/1", create_mock_page("https://example.com/1", html_no_h1), {}).analyze()
    assert "H1_HEADING_MISSING" in [i.rule_id for i in issues_no_h1]

    # Multiple H1
    html_multi_h1 = "<html><head><title>A Valid Title Here for Testing</title></head><body><h1>Title 1</h1><h1>Title 2</h1></body></html>"
    issues_multi = PageAnalyzer("https://example.com/2", create_mock_page("https://example.com/2", html_multi_h1), {}).analyze()
    assert "H1_HEADING_MULTIPLE" in [i.rule_id for i in issues_multi]


def test_image_alt_attributes():
    html = """
    <html>
        <head><title>A Valid Title Here for Testing</title></head>
        <body>
            <h1>Main Title</h1>
            <img src="/img/valid.png" alt="Valid Description" />
            <img src="/img/broken1.png" />
            <img src="/img/broken2.png" alt="" />
        </body>
    </html>
    """
    page = create_mock_page("https://example.com/images", html)
    issues = PageAnalyzer("https://example.com/images", page, {}).analyze()

    alt_issues = [i for i in issues if i.rule_id == "IMAGE_ALT_MISSING"]
    assert len(alt_issues) == 1
    assert alt_issues[0].affected_count == 2
    assert "/img/broken1.png" in alt_issues[0].evidence


def test_canonical_tags():
    # Missing canonical
    html_no_canon = "<html><head><title>Valid Title for Testing</title></head><body><h1>Hi</h1></body></html>"
    issues_no_canon = PageAnalyzer("https://example.com/c1", create_mock_page("https://example.com/c1", html_no_canon), {}).analyze()
    assert "CANONICAL_TAG_MISSING" in [i.rule_id for i in issues_no_canon]

    # Multiple conflicting canonicals
    html_multi_canon = """
    <html><head>
        <title>Valid Title for Testing</title>
        <link rel="canonical" href="https://example.com/c2" />
        <link rel="canonical" href="https://example.com/alt" />
    </head><body><h1>Hi</h1></body></html>
    """
    issues_multi = PageAnalyzer("https://example.com/c2", create_mock_page("https://example.com/c2", html_multi_canon), {}).analyze()
    assert "CANONICAL_TAG_MULTIPLE" in [i.rule_id for i in issues_multi]


def test_mixed_content_detection():
    html = """
    <html><head><title>Valid Title for Testing</title></head>
    <body>
        <h1>Secure Page</h1>
        <img src="http://insecure-cdn.com/logo.jpg" alt="Logo" />
    </body></html>
    """
    page = create_mock_page("https://example.com/secure", html)
    issues = PageAnalyzer("https://example.com/secure", page, {}).analyze()
    assert "MIXED_CONTENT_DETECTED" in [i.rule_id for i in issues]


def test_robots_noindex_directive():
    html = """
    <html><head>
        <title>Valid Title for Testing</title>
        <meta name="robots" content="noindex, follow" />
    </head><body><h1>Hi</h1></body></html>
    """
    page = create_mock_page("https://example.com/noindex", html)
    issues = PageAnalyzer("https://example.com/noindex", page, {}).analyze()
    assert "ROBOTS_NOINDEX_DIRECTIVE" in [i.rule_id for i in issues]
