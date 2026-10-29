"""
Rule-Based SEO Analyzer.
Evaluates individual crawled pages and domain configurations against technical SEO best practices.
"""

from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field


class SEOIssue(BaseModel):
    id: str
    rule_id: str
    title: str
    category: str  # "Meta Tags", "Content Structure", "Links & Navigation", "Indexability & Crawling", "Security"
    severity: str  # "Critical", "High", "Medium", "Low"
    priority_score: int  # 1 to 100
    affected_url: str
    affected_count: int = 1
    evidence: str
    impact: str
    suggested_fix: str


class PageAnalyzer:
    def __init__(self, page_url: str, crawl_data, domain_context: dict):
        self.url = page_url
        self.data = crawl_data  # PageCrawlResult
        self.domain_context = domain_context
        self.issues: list[SEOIssue] = []
        self.soup: BeautifulSoup | None = None

        if self.data.is_html and self.data.html:
            try:
                self.soup = BeautifulSoup(self.data.html, "html.parser")
            except Exception:
                self.soup = None

    def analyze(self) -> list[SEOIssue]:
        """Run all rule-based checks for this page."""
        self._check_http_status()

        # If HTTP response failed completely, skip DOM parsing checks
        if self.data.error or (self.data.status_code and self.data.status_code >= 400):
            return self.issues

        if not self.soup:
            return self.issues

        self._check_protocol_and_mixed_content()
        self._check_redirect_chains()
        self._check_title_tag()
        self._check_meta_description()
        self._check_headings()
        self._check_images()
        self._check_canonical()
        self._check_robots_meta()
        self._check_viewport_and_charset()
        self._check_broken_internal_links()

        return self.issues

    def _check_http_status(self):
        if self.data.error:
            self.issues.append(SEOIssue(
                id=f"http-error-{hash(self.url) & 0xfffffff}",
                rule_id="HTTP_REQUEST_FAILED",
                title="Page Crawl Failed",
                category="Indexability & Crawling",
                severity="Critical",
                priority_score=95,
                affected_url=self.url,
                evidence=f"Request failed with error: {self.data.error}",
                impact="Search engine crawlers and users cannot access this page. This page cannot be indexed or ranked.",
                suggested_fix="Ensure the web server is online, firewall allows public crawler access, and SSL certificates are valid."
            ))
            return

        code = self.data.status_code
        if code and code >= 500:
            self.issues.append(SEOIssue(
                id=f"http-5xx-{hash(self.url) & 0xfffffff}",
                rule_id="HTTP_5XX_SERVER_ERROR",
                title=f"Internal Server Error (HTTP {code})",
                category="Indexability & Crawling",
                severity="Critical",
                priority_score=95,
                affected_url=self.url,
                evidence=f"Server returned HTTP status {code}",
                impact="Search engines will de-index pages returning 5xx server errors and user experience is completely broken.",
                suggested_fix="Investigate web server and application error logs. Resolve unhandled exceptions, database connection limits, or backend timeouts."
            ))
        elif code and code == 404:
            self.issues.append(SEOIssue(
                id=f"http-404-{hash(self.url) & 0xfffffff}",
                rule_id="HTTP_404_NOT_FOUND",
                title="Page Not Found (HTTP 404)",
                category="Links & Navigation",
                severity="Critical",
                priority_score=90,
                affected_url=self.url,
                evidence=f"URL returned HTTP 404 Not Found",
                impact="Broken pages waste crawler budget, create dead ends for visitors, and cause link equity loss.",
                suggested_fix="Restore the missing resource, update inbound links to point to the correct URL, or implement a 301 permanent redirect to a relevant page."
            ))
        elif code and code >= 400:
            self.issues.append(SEOIssue(
                id=f"http-4xx-{hash(self.url) & 0xfffffff}",
                rule_id="HTTP_4XX_CLIENT_ERROR",
                title=f"Client Error (HTTP {code})",
                category="Indexability & Crawling",
                severity="High",
                priority_score=80,
                affected_url=self.url,
                evidence=f"URL responded with HTTP status {code}",
                impact="Crawler cannot access content on this URL due to access restriction or client error.",
                suggested_fix="Review authorization settings or rewrite rules to allow public search engine bot access."
            ))

    def _check_protocol_and_mixed_content(self):
        # 1. Plain HTTP check
        if self.url.lower().startswith("http://"):
            self.issues.append(SEOIssue(
                id=f"protocol-http-{hash(self.url) & 0xfffffff}",
                rule_id="INSECURE_HTTP_PROTOCOL",
                title="Page Served Over Insecure HTTP",
                category="Security",
                severity="High",
                priority_score=82,
                affected_url=self.url,
                evidence=f"Page is served via unencrypted 'http://' protocol.",
                impact="HTTPS is a confirmed Google ranking factor. Insecure pages trigger browser warnings and compromise user privacy.",
                suggested_fix="Install a valid SSL/TLS certificate and configure 301 redirects from HTTP to HTTPS across your server."
            ))

        # 2. Mixed Content check (if page is HTTPS, does it load HTTP assets?)
        if self.url.lower().startswith("https://") and self.soup:
            mixed_resources = []
            for tag in self.soup.find_all(["img", "script", "link", "iframe"]):
                src = tag.get("src") or tag.get("href")
                if src and src.strip().lower().startswith("http://"):
                    mixed_resources.append(src.strip())

            if mixed_resources:
                sample_count = len(mixed_resources)
                sample_text = ", ".join(mixed_resources[:3])
                self.issues.append(SEOIssue(
                    id=f"mixed-content-{hash(self.url) & 0xfffffff}",
                    rule_id="MIXED_CONTENT_DETECTED",
                    title="Insecure Mixed Content Detected",
                    category="Security",
                    severity="High",
                    priority_score=85,
                    affected_url=self.url,
                    affected_count=sample_count,
                    evidence=f"Found {sample_count} resource(s) loaded over insecure HTTP on this HTTPS page: {sample_text}",
                    impact="Modern browsers block active mixed content, breaking stylesheets, scripts, and media. Also invalidates page security indicators.",
                    suggested_fix="Update resource URLs in your templates and CSS to use relative protocol ('//') or explicit HTTPS ('https://')."
                ))

    def _check_redirect_chains(self):
        history = self.data.redirect_history
        if len(history) > 2:
            hops_str = " -> ".join([h["from"] for h in history] + [self.data.final_url])
            self.issues.append(SEOIssue(
                id=f"redirect-chain-{hash(self.url) & 0xfffffff}",
                rule_id="REDIRECT_CHAIN_EXCESSIVE",
                title="Redirect Chain Detected",
                category="Links & Navigation",
                severity="Medium",
                priority_score=65,
                affected_url=self.url,
                affected_count=len(history),
                evidence=f"{len(history)} redirect hops: {hops_str}",
                impact="Redirect chains slow down page load times, waste crawler budget, and dilute PageRank transfer.",
                suggested_fix="Point internal links and the initial redirect directly to the final destination URL."
            ))
        elif len(history) == 1 and history[0].get("status") == 302:
            self.issues.append(SEOIssue(
                id=f"redirect-302-{hash(self.url) & 0xfffffff}",
                rule_id="TEMPORARY_302_REDIRECT",
                title="Temporary 302 Redirect Used",
                category="Links & Navigation",
                severity="Low",
                priority_score=35,
                affected_url=self.url,
                evidence=f"302 temporary redirect to: {history[0].get('to')}",
                impact="302 redirects indicate temporary changes; search engines may not transfer link equity or index the target URL properly.",
                suggested_fix="Use a 301 permanent redirect if this relocation is permanent."
            ))

    def _check_title_tag(self):
        titles = self.soup.find_all("title")
        if not titles or not titles[0].string or not titles[0].string.strip():
            self.issues.append(SEOIssue(
                id=f"title-missing-{hash(self.url) & 0xfffffff}",
                rule_id="TITLE_TAG_MISSING",
                title="Missing or Empty Title Tag",
                category="Meta Tags",
                severity="Critical",
                priority_score=92,
                affected_url=self.url,
                evidence="<title> tag is missing or empty in HTML <head>.",
                impact="The title tag is one of the highest-weight on-page ranking factors. Without it, search engines generate random snippet titles.",
                suggested_fix="Add a unique, descriptive <title> tag between 50-60 characters summarizing the page topic."
            ))
            return

        title_text = titles[0].string.strip()
        title_len = len(title_text)

        if len(titles) > 1:
            self.issues.append(SEOIssue(
                id=f"title-multiple-{hash(self.url) & 0xfffffff}",
                rule_id="TITLE_TAG_MULTIPLE",
                title="Multiple Title Tags Found",
                category="Meta Tags",
                severity="Medium",
                priority_score=60,
                affected_url=self.url,
                evidence=f"Found {len(titles)} <title> tags on page.",
                impact="Multiple titles confuse search engine parsers and cause erratic snippet titles in search results.",
                suggested_fix="Remove duplicate <title> tags and ensure only one title tag exists in the <head>."
            ))

        if title_len < 20:
            self.issues.append(SEOIssue(
                id=f"title-short-{hash(self.url) & 0xfffffff}",
                rule_id="TITLE_TAG_TOO_SHORT",
                title="Title Tag Is Too Short",
                category="Meta Tags",
                severity="Low",
                priority_score=30,
                affected_url=self.url,
                evidence=f"Title is only {title_len} characters: '{title_text}'",
                impact="Short titles miss valuable opportunities to target secondary search queries and explain value to searchers.",
                suggested_fix="Expand the title tag to 50–60 characters, including your primary keyword and brand name."
            ))
        elif title_len > 65:
            self.issues.append(SEOIssue(
                id=f"title-long-{hash(self.url) & 0xfffffff}",
                rule_id="TITLE_TAG_TOO_LONG",
                title="Title Tag Exceeds Recommended Length",
                category="Meta Tags",
                severity="Medium",
                priority_score=50,
                affected_url=self.url,
                evidence=f"Title length is {title_len} characters (> 65 chars): '{title_text}'",
                impact="Long titles are truncated with ellipses (...) in Google search engine result pages (SERPs).",
                suggested_fix="Shorten the title tag to between 50 and 60 characters so it fits on both desktop and mobile SERPs."
            ))

    def _check_meta_description(self):
        desc_tag = self.soup.find("meta", attrs={"name": lambda x: x and x.lower() == "description"})
        if not desc_tag or not desc_tag.get("content", "").strip():
            self.issues.append(SEOIssue(
                id=f"desc-missing-{hash(self.url) & 0xfffffff}",
                rule_id="META_DESCRIPTION_MISSING",
                title="Missing Meta Description",
                category="Meta Tags",
                severity="High",
                priority_score=75,
                affected_url=self.url,
                evidence="No <meta name='description'> tag found in document head.",
                impact="Meta descriptions directly influence organic click-through rates (CTR). Without one, search engines pull arbitrary page text.",
                suggested_fix="Add an engaging meta description between 120 and 160 characters summarizing the page content with a call to action."
            ))
            return

        desc_content = desc_tag.get("content", "").strip()
        desc_len = len(desc_content)

        if desc_len < 50:
            self.issues.append(SEOIssue(
                id=f"desc-short-{hash(self.url) & 0xfffffff}",
                rule_id="META_DESCRIPTION_TOO_SHORT",
                title="Meta Description Is Too Short",
                category="Meta Tags",
                severity="Low",
                priority_score=25,
                affected_url=self.url,
                evidence=f"Meta description is only {desc_len} characters: '{desc_content}'",
                impact="Under-optimized meta descriptions underperform in attracting clicks and conveying context to users.",
                suggested_fix="Expand the meta description to 120–160 characters to provide a compelling snippet in search results."
            ))
        elif desc_len > 165:
            self.issues.append(SEOIssue(
                id=f"desc-long-{hash(self.url) & 0xfffffff}",
                rule_id="META_DESCRIPTION_TOO_LONG",
                title="Meta Description Exceeds SERP Display Limit",
                category="Meta Tags",
                severity="Low",
                priority_score=28,
                affected_url=self.url,
                evidence=f"Meta description is {desc_len} characters (> 165 chars)",
                impact="Descriptions over 160 characters are typically truncated on Google desktop and mobile snippets.",
                suggested_fix="Trim meta description length to under 160 characters, keeping primary keywords in the first 120 characters."
            ))

    def _check_headings(self):
        h1_tags = self.soup.find_all("h1")
        if not h1_tags:
            self.issues.append(SEOIssue(
                id=f"h1-missing-{hash(self.url) & 0xfffffff}",
                rule_id="H1_HEADING_MISSING",
                title="Missing H1 Heading",
                category="Content Structure",
                severity="High",
                priority_score=80,
                affected_url=self.url,
                evidence="No <h1> tag exists in the HTML document.",
                impact="The H1 tag clarifies the main topic of the page for both users and search bots. Missing H1 hurts semantic structure.",
                suggested_fix="Add exactly one clear, prominent <h1> heading matching the page's primary intent."
            ))
        elif len(h1_tags) > 1:
            h1_texts = [f"'{h.get_text().strip()[:40]}'" for h in h1_tags[:3]]
            self.issues.append(SEOIssue(
                id=f"h1-multiple-{hash(self.url) & 0xfffffff}",
                rule_id="H1_HEADING_MULTIPLE",
                title="Multiple H1 Headings Detected",
                category="Content Structure",
                severity="Medium",
                priority_score=55,
                affected_url=self.url,
                affected_count=len(h1_tags),
                evidence=f"Found {len(h1_tags)} H1 headings: {', '.join(h1_texts)}",
                impact="While HTML5 technically allows multiple H1s, best practice is a single H1 to emphasize the primary page focus.",
                suggested_fix="Keep only one primary H1 for the page title and convert secondary headings to H2 or H3."
            ))

        # Hierarchy check (e.g. H3 before H2, skipping heading levels)
        headings = self.soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        levels = [int(h.name[1]) for h in headings]
        skipped_hierarchy = False
        prev_lvl = 0
        for lvl in levels:
            if prev_lvl != 0 and lvl > prev_lvl + 1:
                skipped_hierarchy = True
                break
            prev_lvl = lvl

        if skipped_hierarchy:
            self.issues.append(SEOIssue(
                id=f"heading-hierarchy-{hash(self.url) & 0xfffffff}",
                rule_id="HEADING_HIERARCHY_SKIPPED",
                title="Heading Hierarchy Levels Skipped",
                category="Content Structure",
                severity="Low",
                priority_score=30,
                affected_url=self.url,
                evidence=f"Headings skip structural levels (sequence: {' -> '.join([f'H{l}' for l in levels[:6]])})",
                impact="Skipping heading tags (e.g. jumping from H1 directly to H3) compromises accessibility for screen readers and semantic clarity.",
                suggested_fix="Nest headings sequentially: use H2 tags under H1, and H3 tags under H2."
            ))

    def _check_images(self):
        imgs = self.soup.find_all("img")
        missing_alt_srcs = []
        for img in imgs:
            alt = img.get("alt")
            if alt is None or alt.strip() == "":
                src = img.get("src", "unknown-source")
                missing_alt_srcs.append(src)

        if missing_alt_srcs:
            count = len(missing_alt_srcs)
            sample_srcs = missing_alt_srcs[:3]
            self.issues.append(SEOIssue(
                id=f"img-alt-missing-{hash(self.url) & 0xfffffff}",
                rule_id="IMAGE_ALT_MISSING",
                title="Images Missing Alt Attributes",
                category="Content Structure",
                severity="Medium",
                priority_score=60,
                affected_url=self.url,
                affected_count=count,
                evidence=f"{count} image(s) lack an 'alt' attribute. Samples: {', '.join(sample_srcs)}",
                impact="Alt tags provide image context to search engines for Google Image Search and enable accessibility for screen readers.",
                suggested_fix="Add descriptive, keyword-relevant alt attributes to all content images. Use alt='' only for purely decorative graphics."
            ))

    def _check_canonical(self):
        canonical_tags = self.soup.find_all("link", attrs={"rel": lambda x: x and "canonical" in x})
        if not canonical_tags:
            self.issues.append(SEOIssue(
                id=f"canonical-missing-{hash(self.url) & 0xfffffff}",
                rule_id="CANONICAL_TAG_MISSING",
                title="Missing Canonical Tag",
                category="Indexability & Crawling",
                severity="Medium",
                priority_score=50,
                affected_url=self.url,
                evidence="No <link rel='canonical'> found in HTML head.",
                impact="Without canonical tags, search engines may treat tracking parameters (UTMs), session IDs, or trailing slashes as duplicate pages.",
                suggested_fix="Add a self-referential canonical tag: <link rel='canonical' href='https://yourdomain.com/exact-page-path' />"
            ))
            return

        if len(canonical_tags) > 1:
            self.issues.append(SEOIssue(
                id=f"canonical-multiple-{hash(self.url) & 0xfffffff}",
                rule_id="CANONICAL_TAG_MULTIPLE",
                title="Multiple Canonical Tags Detected",
                category="Indexability & Crawling",
                severity="Critical",
                priority_score=90,
                affected_url=self.url,
                evidence=f"Found {len(canonical_tags)} canonical tags.",
                impact="Conflicting canonical URLs cause search engines to ignore all canonical declarations on the page, leading to duplicate indexing.",
                suggested_fix="Ensure only one canonical tag is generated in the <head>."
            ))
            return

        canonical_href = canonical_tags[0].get("href", "").strip()
        if not canonical_href:
            self.issues.append(SEOIssue(
                id=f"canonical-empty-{hash(self.url) & 0xfffffff}",
                rule_id="CANONICAL_TAG_EMPTY",
                title="Empty Canonical Tag",
                category="Indexability & Crawling",
                severity="High",
                priority_score=78,
                affected_url=self.url,
                evidence="Canonical href attribute is empty.",
                impact="Invalid canonical tag syntax invalidates canonical indexing instructions.",
                suggested_fix="Provide an absolute URL pointing to the authoritative version of this page."
            ))
        elif not canonical_href.startswith(("http://", "https://")):
            self.issues.append(SEOIssue(
                id=f"canonical-relative-{hash(self.url) & 0xfffffff}",
                rule_id="CANONICAL_TAG_RELATIVE",
                title="Relative Canonical URL Used",
                category="Indexability & Crawling",
                severity="Medium",
                priority_score=45,
                affected_url=self.url,
                evidence=f"Canonical URL is relative: '{canonical_href}'",
                impact="Google recommends absolute URLs for canonical tags to prevent misinterpretation across protocol or domain variations.",
                suggested_fix=f"Change to absolute URL format: {urljoin(self.url, canonical_href)}"
            ))

    def _check_robots_meta(self):
        # Check <meta name="robots">
        robots_meta = self.soup.find("meta", attrs={"name": lambda x: x and x.lower() == "robots"})
        x_robots_header = self.data.headers.get("x-robots-tag", "").lower()

        directives = []
        if robots_meta and robots_meta.get("content"):
            directives.extend([d.strip().lower() for d in robots_meta.get("content").split(",")])
        if x_robots_header:
            directives.extend([d.strip().lower() for d in x_robots_header.split(",")])

        if "noindex" in directives:
            self.issues.append(SEOIssue(
                id=f"meta-noindex-{hash(self.url) & 0xfffffff}",
                rule_id="ROBOTS_NOINDEX_DIRECTIVE",
                title="Page Has 'noindex' Directive",
                category="Indexability & Crawling",
                severity="High",
                priority_score=85,
                affected_url=self.url,
                evidence=f"Robots directive contains 'noindex'.",
                impact="This page is explicitly blocked from appearing in search engine results. If unintended, organic traffic will drop to zero.",
                suggested_fix="Remove 'noindex' from the robots meta tag or X-Robots-Tag header if this page should receive organic traffic."
            ))

        if "nofollow" in directives:
            self.issues.append(SEOIssue(
                id=f"meta-nofollow-{hash(self.url) & 0xfffffff}",
                rule_id="ROBOTS_NOFOLLOW_DIRECTIVE",
                title="Page Has 'nofollow' Directive",
                category="Indexability & Crawling",
                severity="Medium",
                priority_score=50,
                affected_url=self.url,
                evidence="Robots directive contains 'nofollow'.",
                impact="Search bots will not crawl or pass PageRank through links discovered on this page.",
                suggested_fix="Remove 'nofollow' from the page-level robots tag unless outbound links must not be endorsed."
            ))

    def _check_viewport_and_charset(self):
        viewport = self.soup.find("meta", attrs={"name": lambda x: x and x.lower() == "viewport"})
        if not viewport:
            self.issues.append(SEOIssue(
                id=f"viewport-missing-{hash(self.url) & 0xfffffff}",
                rule_id="VIEWPORT_TAG_MISSING",
                title="Missing Mobile Viewport Meta Tag",
                category="Indexability & Crawling",
                severity="High",
                priority_score=75,
                affected_url=self.url,
                evidence="No <meta name='viewport'> tag detected.",
                impact="Google uses mobile-first indexing. Pages without a viewport tag will fail mobile-friendliness checks and suffer in mobile search.",
                suggested_fix="Add <meta name='viewport' content='width=device-width, initial-scale=1.0'> to the HTML head."
            ))

        charset = self.soup.find("meta", attrs={"charset": True}) or self.soup.find("meta", attrs={"http-equiv": lambda x: x and x.lower() == "content-type"})
        if not charset:
            self.issues.append(SEOIssue(
                id=f"charset-missing-{hash(self.url) & 0xfffffff}",
                rule_id="CHARSET_DECLARATION_MISSING",
                title="Missing Character Encoding Declaration",
                category="Indexability & Crawling",
                severity="Low",
                priority_score=20,
                affected_url=self.url,
                evidence="No character set declaration (<meta charset='utf-8'>) detected.",
                impact="Browsers and crawlers might misinterpret special characters, hurting readability and content extraction.",
                suggested_fix="Add <meta charset='UTF-8'> as the first element in the HTML <head>."
            ))

    def _check_broken_internal_links(self):
        # We check against crawled pages map in domain context
        all_pages = self.domain_context.get("scanned_pages", {})
        broken_links_on_this_page = []

        for target in self.data.internal_links:
            if target in all_pages:
                res = all_pages[target]
                if res.status_code and res.status_code >= 400:
                    broken_links_on_this_page.append(f"{target} (HTTP {res.status_code})")
                elif res.error:
                    broken_links_on_this_page.append(f"{target} (Network Error)")

        if broken_links_on_this_page:
            count = len(broken_links_on_this_page)
            sample = broken_links_on_this_page[:3]
            self.issues.append(SEOIssue(
                id=f"broken-links-{hash(self.url) & 0xfffffff}",
                rule_id="INTERNAL_BROKEN_LINKS",
                title="Internal Broken Links Found on Page",
                category="Links & Navigation",
                severity="High",
                priority_score=82,
                affected_url=self.url,
                affected_count=count,
                evidence=f"{count} broken internal links detected on this page: {', '.join(sample)}",
                impact="Broken internal links create dead ends for visitors, increase bounce rate, and waste search bot crawl capacity.",
                suggested_fix="Update or remove the broken hyperlinks in this page's content or template."
            ))
