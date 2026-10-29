"""
Self-contained HTML Audit Report Generator.
Renders a complete, beautifully styled executive and technical SEO report
that can be opened in any browser or printed/saved to PDF.
"""

import html


def generate_html_report(audit_data: dict) -> str:
    target_url = html.escape(audit_data.get("target_url", ""))
    timestamp = html.escape(str(audit_data.get("timestamp", "")))
    pages_scanned = audit_data.get("pages_scanned", 0)
    health_score_data = audit_data.get("health_score", {})
    score = health_score_data.get("score", 0)
    rating = html.escape(health_score_data.get("rating", "N/A"))
    formula = html.escape(health_score_data.get("calculation_formula", ""))

    crit_count = health_score_data.get("critical_count", 0)
    high_count = health_score_data.get("high_count", 0)
    med_count = health_score_data.get("medium_count", 0)
    low_count = health_score_data.get("low_count", 0)
    total_issues = health_score_data.get("total_issues", 0)

    robots_found = audit_data.get("robots_txt_found", False)
    sitemap_found = audit_data.get("sitemap_found", False)

    # Score color
    if score >= 80:
        score_color = "#16a34a"  # green
        score_bg = "#f0fdf4"
    elif score >= 60:
        score_color = "#d97706"  # amber
        score_bg = "#fffbeb"
    else:
        score_color = "#dc2626"  # red
        score_bg = "#fef2f2"

    issues_html = []
    for issue in audit_data.get("issues", []):
        sev = html.escape(issue.get("severity", "Low"))
        sev_class = sev.lower()
        iss_title = html.escape(issue.get("title", ""))
        category = html.escape(issue.get("category", ""))
        priority = issue.get("priority_score", 0)
        url = html.escape(issue.get("affected_url", ""))
        evidence = html.escape(issue.get("evidence", ""))
        impact = html.escape(issue.get("impact", ""))
        fix = html.escape(issue.get("suggested_fix", ""))
        count = issue.get("affected_count", 1)

        issues_html.append(f"""
        <div class="issue-card sev-{sev_class}">
            <div class="issue-header">
                <div class="issue-title-group">
                    <span class="badge badge-{sev_class}">{sev}</span>
                    <span class="badge badge-cat">{category}</span>
                    <h3 class="issue-title">{iss_title}</h3>
                </div>
                <div class="priority-badge">Priority {priority}/100</div>
            </div>
            <div class="issue-meta">
                <strong>Affected URL:</strong> <a href="{url}" target="_blank" rel="noopener">{url}</a>
                {f'<span class="occurrences">({count} affected instances)</span>' if count > 1 else ''}
            </div>
            <div class="issue-evidence">
                <strong>Evidence:</strong>
                <code>{evidence}</code>
            </div>
            <div class="issue-body">
                <div class="issue-impact">
                    <strong>Why It Matters:</strong> {impact}
                </div>
                <div class="issue-fix">
                    <strong>Recommended Fix:</strong> {fix}
                </div>
            </div>
        </div>
        """)

    issues_content = "\n".join(issues_html) if issues_html else "<p class='no-issues'>No SEO issues detected across the scanned pages.</p>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Insight Audit Report - {target_url}</title>
    <style>
        :root {{
            --primary: #0f172a;
            --accent: #2563eb;
            --text: #1e293b;
            --muted: #64748b;
            --border: #e2e8f0;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --crit: #ef4444;
            --high: #f97316;
            --med: #3b82f6;
            --low: #64748b;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.5;
            padding: 2rem 1rem;
        }}
        .container {{
            max-width: 1040px;
            margin: 0 auto;
            background: var(--card-bg);
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--border);
            padding: 2.5rem;
        }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid var(--border);
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        .brand {{
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--primary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .brand span {{ color: var(--accent); }}
        .audit-meta {{
            text-align: right;
            font-size: 0.9rem;
            color: var(--muted);
        }}
        .score-hero {{
            display: grid;
            grid-template-columns: 240px 1fr;
            gap: 2rem;
            background: #f1f5f9;
            border-radius: 10px;
            padding: 2rem;
            margin-bottom: 2rem;
            align-items: center;
        }}
        .score-dial {{
            background: {score_bg};
            border: 4px solid {score_color};
            border-radius: 50%;
            width: 180px;
            height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin: 0 auto;
        }}
        .score-value {{
            font-size: 3.5rem;
            font-weight: 800;
            color: {score_color};
            line-height: 1;
        }}
        .score-label {{
            font-size: 0.85rem;
            text-transform: uppercase;
            font-weight: 700;
            color: {score_color};
            margin-top: 4px;
        }}
        .score-details h2 {{
            font-size: 1.5rem;
            color: var(--primary);
            margin-bottom: 0.5rem;
        }}
        .score-formula {{
            font-size: 0.85rem;
            color: var(--muted);
            margin-top: 0.75rem;
            background: #ffffff;
            padding: 0.6rem 0.9rem;
            border-radius: 6px;
            border: 1px solid var(--border);
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .metric-card {{
            background: #ffffff;
            border: 1px solid var(--border);
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-num {{
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--primary);
        }}
        .metric-title {{
            font-size: 0.8rem;
            text-transform: uppercase;
            font-weight: 600;
            color: var(--muted);
        }}
        .disclaimer-banner {{
            background: #eff6ff;
            border-left: 4px solid var(--accent);
            padding: 0.8rem 1rem;
            font-size: 0.85rem;
            color: #1e40af;
            border-radius: 0 6px 6px 0;
            margin-bottom: 2rem;
        }}
        .section-title {{
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 1.2rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border);
        }}
        .issue-card {{
            background: #ffffff;
            border: 1px solid var(--border);
            border-left: 5px solid #cbd5e1;
            border-radius: 8px;
            padding: 1.25rem;
            margin-bottom: 1.25rem;
        }}
        .issue-card.sev-critical {{ border-left-color: var(--crit); }}
        .issue-card.sev-high {{ border-left-color: var(--high); }}
        .issue-card.sev-medium {{ border-left-color: var(--med); }}
        .issue-card.sev-low {{ border-left-color: var(--low); }}

        .issue-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}
        .issue-title-group {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
            flex-wrap: wrap;
        }}
        .issue-title {{
            font-size: 1.05rem;
            font-weight: 600;
            color: var(--primary);
        }}
        .badge {{
            display: inline-block;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 0.2rem 0.6rem;
            border-radius: 9999px;
            text-transform: uppercase;
        }}
        .badge-critical {{ background: #fef2f2; color: #b91c1c; }}
        .badge-high {{ background: #fff7ed; color: #c2410c; }}
        .badge-medium {{ background: #eff6ff; color: #1d4ed8; }}
        .badge-low {{ background: #f1f5f9; color: #475569; }}
        .badge-cat {{ background: #e2e8f0; color: #334155; font-size: 0.7rem; }}

        .priority-badge {{
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--muted);
            background: #f1f5f9;
            padding: 0.25rem 0.6rem;
            border-radius: 4px;
        }}
        .issue-meta {{
            font-size: 0.85rem;
            color: var(--muted);
            margin-bottom: 0.6rem;
            word-break: break-all;
        }}
        .issue-meta a {{ color: var(--accent); text-decoration: none; }}
        .issue-evidence {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 0.5rem 0.75rem;
            font-size: 0.85rem;
            margin-bottom: 0.75rem;
        }}
        .issue-evidence code {{
            font-family: monospace;
            color: #b91c1c;
            display: block;
            margin-top: 0.2rem;
            word-break: break-all;
        }}
        .issue-body {{
            font-size: 0.9rem;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }}
        .issue-impact {{
            background: #fffbeb;
            padding: 0.6rem 0.8rem;
            border-radius: 6px;
            color: #92400e;
        }}
        .issue-fix {{
            background: #f0fdf4;
            padding: 0.6rem 0.8rem;
            border-radius: 6px;
            color: #166534;
        }}
        footer {{
            margin-top: 3rem;
            text-align: center;
            font-size: 0.8rem;
            color: var(--muted);
            border-top: 1px solid var(--border);
            padding-top: 1.5rem;
        }}

        @media (max-width: 768px) {{
            .score-hero {{ grid-template-columns: 1fr; text-align: center; }}
            .issue-body {{ grid-template-columns: 1fr; }}
            .audit-meta {{ text-align: left; }}
        }}
        @media print {{
            body {{ padding: 0; background: #ffffff; }}
            .container {{ box-shadow: none; border: none; padding: 0; }}
            .issue-card {{ break-inside: avoid; page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="brand">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2.5"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                SEO <span>Insight</span> Audit Report
            </div>
            <div class="audit-meta">
                <div><strong>Audited URL:</strong> {target_url}</div>
                <div><strong>Scan Date:</strong> {timestamp}</div>
            </div>
        </header>

        <div class="score-hero">
            <div class="score-dial">
                <div class="score-value">{score}</div>
                <div class="score-label">{rating}</div>
            </div>
            <div class="score-details">
                <h2>Technical SEO Health Evaluation</h2>
                <p>Comprehensive scan results covering on-page meta tags, semantic headings, crawl directives, internal links, security protocol, and duplicate content.</p>
                <div class="score-formula">
                    <strong>Score Calculation:</strong> {formula}
                </div>
            </div>
        </div>

        <div class="disclaimer-banner">
            <strong>Important Notice:</strong> Findings are prioritized based on technical impact and search engine webmaster guidelines. These priorities represent technical hygiene and crawl accessibility, not guaranteed Google ranking improvements.
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-num">{pages_scanned}</div>
                <div class="metric-title">Pages Scanned</div>
            </div>
            <div class="metric-card">
                <div class="metric-num">{total_issues}</div>
                <div class="metric-title">Total Issues</div>
            </div>
            <div class="metric-card">
                <div class="metric-num" style="color: var(--crit);">{crit_count}</div>
                <div class="metric-title">Critical</div>
            </div>
            <div class="metric-card">
                <div class="metric-num" style="color: var(--high);">{high_count}</div>
                <div class="metric-title">High</div>
            </div>
            <div class="metric-card">
                <div class="metric-num" style="color: var(--med);">{med_count}</div>
                <div class="metric-title">Medium</div>
            </div>
            <div class="metric-card">
                <div class="metric-num" style="color: var(--low);">{low_count}</div>
                <div class="metric-title">Low</div>
            </div>
        </div>

        <h2 class="section-title">Prioritized Action Items & Findings ({total_issues})</h2>
        <div class="issues-container">
            {issues_content}
        </div>

        <footer>
            Report generated by SEO Insight — Website SEO Audit & Fix Prioritizer.<br/>
            Complies with Google Webmaster Guidelines & W3C HTML5 standards.
        </footer>
    </div>
</body>
</html>
"""
    return html_content
