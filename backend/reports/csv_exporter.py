"""
CSV Report Exporter for SEO Insight Audit Findings.
"""

import csv
import io
from analyzer.seo_rules import SEOIssue


def generate_csv_report(audit_data: dict) -> str:
    """Generate an RFC 4180 compliant CSV string from audit findings."""
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    # Header metadata rows
    writer.writerow(["# SEO Insight - Audit Findings Export"])
    writer.writerow(["# Target URL", audit_data.get("target_url", "")])
    writer.writerow(["# Audit Date", audit_data.get("timestamp", "")])
    writer.writerow(["# Pages Scanned", audit_data.get("pages_scanned", 0)])
    writer.writerow(["# Health Score", f"{audit_data.get('health_score', {}).get('score', 0)} / 100 ({audit_data.get('health_score', {}).get('rating', '')})"])
    writer.writerow([])

    # Table columns
    writer.writerow([
        "Issue ID",
        "Title",
        "Category",
        "Severity",
        "Priority Score",
        "Affected URL",
        "Affected Occurrences",
        "Evidence",
        "Why It Matters",
        "Suggested Fix",
    ])

    issues = audit_data.get("issues", [])
    for issue in issues:
        writer.writerow([
            issue.get("id", ""),
            issue.get("title", ""),
            issue.get("category", ""),
            issue.get("severity", ""),
            issue.get("priority_score", 0),
            issue.get("affected_url", ""),
            issue.get("affected_count", 1),
            issue.get("evidence", ""),
            issue.get("impact", ""),
            issue.get("suggested_fix", ""),
        ])

    return output.getvalue()
