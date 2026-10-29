"""
FastAPI Backend Application for SEO Insight — Website SEO Audit & Fix Prioritizer.
With SQLite database persistence for audit history and reports.
"""

import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from crawler.ssrf import validate_url_ssrf
from crawler.crawler import WebsiteCrawler
from analyzer.seo_rules import PageAnalyzer
from analyzer.duplicate_detector import analyze_cross_page_issues
from analyzer.prioritizer import calculate_health_score, sort_prioritized_issues
from reports.csv_exporter import generate_csv_report
from reports.html_exporter import generate_html_report
from database import init_db, save_audit, get_audit_by_id, get_audit_history, delete_audit_by_id

app = FastAPI(
    title="SEO Insight API",
    description="Website SEO Audit & Fix Prioritizer API with Database History",
    version="1.1.0"
)

# Initialize database schema and seeds on startup
init_db()

# Enable CORS for frontend Vite dev server and deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for active audit sessions
AUDITS_STORE: dict[str, dict] = {}

SAMPLE_DATA_PATH = Path(__file__).parent / "sample_data" / "sample_audit.json"


class AuditRequest(BaseModel):
    url: str
    max_pages: Optional[int] = 12
    allow_test_local: Optional[bool] = False


def run_crawler_sync(crawler: WebsiteCrawler):
    """Helper to run crawler coroutine."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(crawler.crawl())
    finally:
        loop.close()


def execute_audit_task(audit_id: str, target_url: str, max_pages: int, allow_test_local: bool):
    session = AUDITS_STORE.get(audit_id)
    if not session:
        return

    crawler = WebsiteCrawler(
        start_url=target_url,
        max_pages=max_pages,
        allow_test_local=allow_test_local
    )
    session["crawler"] = crawler
    session["status"] = "crawling"

    try:
        scanned_pages = run_crawler_sync(crawler)
        session["status"] = "analyzing"
        session["status_message"] = "Analyzing SEO rules and calculating priority scores..."

        # Page-level analysis
        all_issues = []
        domain_context = {"scanned_pages": scanned_pages}

        for page_url, crawl_res in scanned_pages.items():
            analyzer = PageAnalyzer(page_url, crawl_res, domain_context)
            page_issues = analyzer.analyze()
            all_issues.extend(page_issues)

        # Site-wide & cross-page analysis
        cross_issues = analyze_cross_page_issues(crawler, scanned_pages)
        all_issues.extend(cross_issues)

        # Health score calculation & sorting
        health_data = calculate_health_score(all_issues, crawler.pages_scanned)
        sorted_issues = sort_prioritized_issues(all_issues)

        # Build final audit result
        result_data = {
            "audit_id": audit_id,
            "is_sample": False,
            "target_url": target_url,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "pages_scanned": crawler.pages_scanned,
            "pages_discovered": crawler.pages_discovered,
            "pages_failed": crawler.pages_failed,
            "robots_txt_found": crawler.robots_handler.found if crawler.robots_handler else False,
            "sitemap_found": crawler.sitemap_found,
            "health_score": health_data,
            "issues": [issue.dict() for issue in sorted_issues],
            "crawled_urls": [
                {
                    "url": u,
                    "status_code": r.status_code,
                    "response_time_ms": r.response_time_ms,
                    "is_html": r.is_html,
                    "error": r.error
                }
                for u, r in scanned_pages.items()
            ]
        }

        session["status"] = "completed"
        session["status_message"] = "Audit completed successfully."
        session["result"] = result_data

        # Persist directly into SQLite database
        try:
            save_audit(result_data)
        except Exception as db_err:
            print(f"Warning: Failed to save audit to DB: {db_err}")

    except Exception as e:
        session["status"] = "failed"
        session["error"] = str(e)
        session["status_message"] = f"Audit failed: {e}"


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "SEO Insight API", "version": "1.1.0"}


@app.get("/api/audits/history")
def get_audits_history():
    """Retrieve all previously audited reports from the database."""
    history = get_audit_history()
    return {"history": history, "total": len(history)}


@app.post("/api/audit")
def start_audit(req: AuditRequest, background_tasks: BackgroundTasks):
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty.")

    # Upfront SSRF and syntax validation
    is_safe, error_msg = validate_url_ssrf(url, allow_test_local=req.allow_test_local)
    if not is_safe:
        raise HTTPException(status_code=400, detail=f"Invalid or prohibited URL: {error_msg}")

    audit_id = str(uuid.uuid4())
    AUDITS_STORE[audit_id] = {
        "audit_id": audit_id,
        "target_url": url,
        "status": "queued",
        "status_message": "Initializing audit session...",
        "crawler": None,
        "result": None,
        "error": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    background_tasks.add_task(
        execute_audit_task,
        audit_id=audit_id,
        target_url=url,
        max_pages=req.max_pages or 12,
        allow_test_local=req.allow_test_local
    )

    return {
        "audit_id": audit_id,
        "status": "queued",
        "message": "Audit successfully initiated."
    }


@app.get("/api/audit/status/{audit_id}")
def get_audit_status(audit_id: str):
    session = AUDITS_STORE.get(audit_id)
    if not session:
        # Check if already completed and in database
        saved = get_audit_by_id(audit_id)
        if saved:
            return {
                "audit_id": audit_id,
                "status": "completed",
                "status_message": "Audit completed.",
                "error": None,
                "pages_discovered": saved.get("pages_discovered", 0),
                "pages_scanned": saved.get("pages_scanned", 0),
                "pages_failed": saved.get("pages_failed", 0),
                "current_url": None,
            }
        raise HTTPException(status_code=404, detail="Audit session not found.")

    crawler = session.get("crawler")
    return {
        "audit_id": audit_id,
        "status": session["status"],
        "status_message": session.get("status_message", ""),
        "error": session.get("error"),
        "pages_discovered": crawler.pages_discovered if crawler else 0,
        "pages_scanned": crawler.pages_scanned if crawler else 0,
        "pages_failed": crawler.pages_failed if crawler else 0,
        "current_url": crawler.current_url if crawler else None,
    }


@app.get("/api/audit/{audit_id}")
def get_audit_result(audit_id: str):
    # Check if in active memory
    session = AUDITS_STORE.get(audit_id)
    if session:
        if session["status"] == "failed":
            return {
                "audit_id": audit_id,
                "status": "failed",
                "error": session.get("error"),
                "status_message": session.get("status_message")
            }
        if session["status"] != "completed":
            return {
                "audit_id": audit_id,
                "status": session["status"],
                "status_message": session.get("status_message")
            }
        return session["result"]

    # Check database persistence
    saved_audit = get_audit_by_id(audit_id)
    if saved_audit:
        return saved_audit

    # Check sample audit fallback
    if audit_id == "sample-audit-acme-2025":
        return get_sample_audit()

    raise HTTPException(status_code=404, detail="Audit report not found.")


@app.delete("/api/audit/{audit_id}")
def delete_audit(audit_id: str):
    """Delete an audit from database and active sessions."""
    AUDITS_STORE.pop(audit_id, None)
    deleted = delete_audit_by_id(audit_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Audit not found in database.")
    return {"status": "ok", "message": f"Audit {audit_id} deleted."}


@app.get("/api/sample-audit")
def get_sample_audit():
    if not SAMPLE_DATA_PATH.exists():
        raise HTTPException(status_code=404, detail="Sample audit file not found.")
    with open(SAMPLE_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


@app.get("/api/audit/{audit_id}/csv")
def export_audit_csv(audit_id: str):
    data = None
    session = AUDITS_STORE.get(audit_id)
    if session and session.get("result"):
        data = session["result"]
    else:
        data = get_audit_by_id(audit_id)

    if not data and audit_id == "sample-audit-acme-2025":
        data = get_sample_audit()

    if not data:
        raise HTTPException(status_code=404, detail="Audit result not ready or not found.")

    csv_content = generate_csv_report(data)
    filename = f"seo-audit-{audit_id[:8]}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.get("/api/audit/{audit_id}/report")
def export_audit_html(audit_id: str):
    data = None
    session = AUDITS_STORE.get(audit_id)
    if session and session.get("result"):
        data = session["result"]
    else:
        data = get_audit_by_id(audit_id)

    if not data and audit_id == "sample-audit-acme-2025":
        data = get_sample_audit()

    if not data:
        raise HTTPException(status_code=404, detail="Audit result not ready or not found.")

    html_content = generate_html_report(data)
    filename = f"seo-audit-{audit_id[:8]}.html"
    return Response(
        content=html_content,
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
