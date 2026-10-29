/**
 * API client for communicating with the FastAPI backend.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) throw new Error('Backend server is not reachable');
  return res.json();
}

export async function fetchAuditHistory() {
  const res = await fetch(`${API_BASE}/api/audits/history`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch audit history');
  }
  return res.json();
}

export async function startAudit(url, maxPages = 12) {
  const res = await fetch(`${API_BASE}/api/audit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, max_pages: maxPages }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Audit failed with status ${res.status}`);
  }

  return res.json();
}

export async function fetchAuditStatus(auditId) {
  const res = await fetch(`${API_BASE}/api/audit/status/${auditId}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch audit status');
  }
  return res.json();
}

export async function fetchAuditResult(auditId) {
  const res = await fetch(`${API_BASE}/api/audit/${auditId}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch audit result');
  }
  return res.json();
}

export async function deleteAudit(auditId) {
  const res = await fetch(`${API_BASE}/api/audit/${auditId}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to delete audit');
  }
  return res.json();
}

export async function fetchSampleAudit() {
  const res = await fetch(`${API_BASE}/api/sample-audit`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to load sample audit');
  }
  return res.json();
}

export function getCsvExportUrl(auditId) {
  return `${API_BASE}/api/audit/${auditId}/csv`;
}

export function getHtmlReportUrl(auditId) {
  return `${API_BASE}/api/audit/${auditId}/report`;
}
