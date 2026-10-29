"""
Unit tests for SQLite database audit history persistence.
"""

from database import init_db, save_audit, get_audit_by_id, get_audit_history, delete_audit_by_id


def test_init_and_seed_db():
    init_db()
    history = get_audit_history()
    assert isinstance(history, list)
    assert len(history) >= 1  # Sample audit is seeded automatically


def test_save_and_retrieve_audit():
    sample_audit = {
        "audit_id": "test-db-audit-1",
        "target_url": "https://test-site.org",
        "timestamp": "2026-10-29 14:00:00 UTC",
        "pages_scanned": 5,
        "pages_discovered": 10,
        "pages_failed": 0,
        "robots_txt_found": True,
        "sitemap_found": True,
        "health_score": {
            "score": 88,
            "rating": "Good",
            "critical_count": 0,
            "high_count": 2,
            "medium_count": 3,
            "low_count": 1,
            "total_issues": 6
        },
        "issues": [],
        "crawled_urls": []
    }

    save_audit(sample_audit)
    retrieved = get_audit_by_id("test-db-audit-1")
    assert retrieved is not None
    assert retrieved["target_url"] == "https://test-site.org"
    assert retrieved["health_score"]["score"] == 88

    # Check that it appears in history list
    history = get_audit_history()
    ids = [h["id"] for h in history]
    assert "test-db-audit-1" in ids

    # Clean up
    delete_audit_by_id("test-db-audit-1")
    assert get_audit_by_id("test-db-audit-1") is None
