"""
Unit tests for Technical SEO Health Score and Prioritization.
"""

from analyzer.prioritizer import calculate_health_score, sort_prioritized_issues
from analyzer.seo_rules import SEOIssue


def test_perfect_health_score():
    health = calculate_health_score([], pages_scanned=5)
    assert health["score"] == 100
    assert health["rating"] == "Excellent"
    assert health["total_issues"] == 0


def test_score_deduction_and_rating():
    issues = [
        SEOIssue(
            id="1", rule_id="TITLE_MISSING", title="Missing Title", category="Meta Tags",
            severity="Critical", priority_score=95, affected_url="https://example.com",
            evidence="", impact="", suggested_fix=""
        ),
        SEOIssue(
            id="2", rule_id="H1_MISSING", title="Missing H1", category="Content Structure",
            severity="High", priority_score=80, affected_url="https://example.com",
            evidence="", impact="", suggested_fix=""
        ),
    ]
    health = calculate_health_score(issues, pages_scanned=1)
    assert health["score"] < 100
    assert health["critical_count"] == 1
    assert health["high_count"] == 1
    assert health["total_issues"] == 2
    assert "Critical = -25pts" in health["calculation_formula"]


def test_sort_prioritized_issues():
    issues = [
        SEOIssue(id="low", rule_id="L", title="Low", category="M", severity="Low", priority_score=30, affected_url="", evidence="", impact="", suggested_fix=""),
        SEOIssue(id="crit", rule_id="C", title="Crit", category="M", severity="Critical", priority_score=95, affected_url="", evidence="", impact="", suggested_fix=""),
        SEOIssue(id="high", rule_id="H", title="High", category="M", severity="High", priority_score=80, affected_url="", evidence="", impact="", suggested_fix=""),
    ]
    sorted_res = sort_prioritized_issues(issues)
    assert sorted_res[0].id == "crit"
    assert sorted_res[1].id == "high"
    assert sorted_res[2].id == "low"
