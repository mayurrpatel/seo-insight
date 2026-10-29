"""
Severity Prioritization and Technical SEO Health Score Calculator.
"""

from .seo_rules import SEOIssue


SEVERITY_WEIGHTS = {
    "Critical": 25,
    "High": 15,
    "Medium": 8,
    "Low": 3,
}

SEVERITY_ORDER = {
    "Critical": 1,
    "High": 2,
    "Medium": 3,
    "Low": 4,
}


def calculate_health_score(issues: list[SEOIssue], pages_scanned: int) -> dict:
    """
    Calculate an evidence-backed Technical SEO Health Score from 0 to 100.
    Returns:
    {
        "score": int (0-100),
        "rating": str,
        "calculation_formula": str,
        "severity_counts": dict,
        "category_counts": dict,
        "critical_count": int,
        "high_count": int,
        "medium_count": int,
        "low_count": int,
        "total_issues": int
    }
    """
    severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    category_counts = {}

    for issue in issues:
        sev = issue.severity
        if sev in severity_counts:
            severity_counts[sev] += 1
        else:
            severity_counts["Low"] += 1

        cat = issue.category
        category_counts[cat] = category_counts.get(cat, 0) + 1

    total_issues = len(issues)
    n_pages = max(1, pages_scanned)

    # Calculate weighted penalty normalized across scanned pages
    weighted_penalty = (
        (severity_counts["Critical"] * SEVERITY_WEIGHTS["Critical"])
        + (severity_counts["High"] * SEVERITY_WEIGHTS["High"])
        + (severity_counts["Medium"] * SEVERITY_WEIGHTS["Medium"])
        + (severity_counts["Low"] * SEVERITY_WEIGHTS["Low"])
    )

    # Normalize penalty per page with a dampening factor to prevent one page from immediately dropping to 0
    # For small crawls (1-3 pages), we calibrate the deduction so a single missing title doesn't zero the score
    normalized_deduction = (weighted_penalty / (n_pages ** 0.65)) * 1.8
    score = max(0, min(100, round(100 - normalized_deduction)))

    if score >= 90:
        rating = "Excellent"
    elif score >= 75:
        rating = "Good"
    elif score >= 50:
        rating = "Needs Improvement"
    else:
        rating = "Poor"

    formula_text = (
        f"Score = 100 - (Normalized Penalty / Pages^0.65). "
        f"Weighted deductions: Critical = -{SEVERITY_WEIGHTS['Critical']}pts, "
        f"High = -{SEVERITY_WEIGHTS['High']}pts, Medium = -{SEVERITY_WEIGHTS['Medium']}pts, "
        f"Low = -{SEVERITY_WEIGHTS['Low']}pts. Evaluated across {n_pages} page(s)."
    )

    return {
        "score": score,
        "rating": rating,
        "calculation_formula": formula_text,
        "severity_counts": severity_counts,
        "category_counts": category_counts,
        "critical_count": severity_counts["Critical"],
        "high_count": severity_counts["High"],
        "medium_count": severity_counts["Medium"],
        "low_count": severity_counts["Low"],
        "total_issues": total_issues,
    }


def sort_prioritized_issues(issues: list[SEOIssue]) -> list[SEOIssue]:
    """Sort issues by priority score descending, then severity rank."""
    return sorted(
        issues,
        key=lambda x: (
            -x.priority_score,
            SEVERITY_ORDER.get(x.severity, 5),
            x.title
        )
    )
