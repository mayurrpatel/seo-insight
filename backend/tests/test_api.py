"""
API route handler unit tests for FastAPI backend.
"""

import pytest
from fastapi import HTTPException, BackgroundTasks
from main import (
    health_check,
    get_sample_audit,
    export_audit_csv,
    export_audit_html,
    start_audit,
    get_audit_result,
    AuditRequest,
)


def test_health_check_handler():
    res = health_check()
    assert res["status"] == "ok"
    assert res["app"] == "SEO Insight API"


def test_sample_audit_handler():
    data = get_sample_audit()
    assert data["is_sample"] is True
    assert "health_score" in data
    assert len(data["issues"]) > 0
    assert data["target_url"] == "https://acme-analytics-demo.io"


def test_ssrf_validation_on_audit_start():
    bg = BackgroundTasks()
    req = AuditRequest(url="http://127.0.0.1:8000")
    with pytest.raises(HTTPException) as exc_info:
        start_audit(req, bg)
    assert exc_info.value.status_code == 400
    assert "prohibited URL" in exc_info.value.detail


def test_csv_export_handler():
    resp = export_audit_csv("sample-audit-acme-2025")
    assert resp.media_type == "text/csv"
    content = resp.body.decode("utf-8")
    assert "SEO Insight - Audit Findings Export" in content
    assert "Missing or Empty Title Tag" in content


def test_html_export_handler():
    resp = export_audit_html("sample-audit-acme-2025")
    assert resp.media_type == "text/html"
    content = resp.body.decode("utf-8")
    assert "SEO Insight Audit Report" in content
    assert "Technical SEO Health Evaluation" in content


def test_get_sample_audit_result_handler():
    res = get_audit_result("sample-audit-acme-2025")
    assert res["is_sample"] is True
    assert res["audit_id"] == "sample-audit-acme-2025"
