import React from 'react';
import { Loader2 } from 'lucide-react';

export default function AuditProgress({ statusData, onCancel }) {
  const scanned = statusData?.pages_scanned || 0;
  const discovered = statusData?.pages_discovered || 1;
  const failures = statusData?.pages_failed || 0;
  const statusMsg = statusData?.status_message || 'Initializing crawl and analyzing target...';
  const currentUrl = statusData?.current_url;

  // Estimate progress percentage
  const maxPages = 12;
  const percent = Math.min(Math.round((scanned / maxPages) * 100), 95);

  return (
    <div className="card progress-card">
      <div className="progress-spinner"></div>
      <h2 className="progress-status">Audit In Progress</h2>
      <p className="progress-detail">{statusMsg}</p>

      {currentUrl && (
        <div style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '1rem', wordBreak: 'break-all' }}>
          <strong>Scanning:</strong> <code>{currentUrl}</code>
        </div>
      )}

      <div className="progress-bar-bg">
        <div className="progress-bar-fill" style={{ width: `${percent}%` }}></div>
      </div>

      <div className="progress-stats-row">
        <div>
          <div className="stat-item-num">{discovered}</div>
          <div className="stat-item-label">Pages Discovered</div>
        </div>
        <div>
          <div className="stat-item-num" style={{ color: '#2563eb' }}>{scanned}</div>
          <div className="stat-item-label">Pages Scanned</div>
        </div>
        <div>
          <div className="stat-item-num" style={{ color: failures > 0 ? '#dc2626' : '#64748b' }}>
            {failures}
          </div>
          <div className="stat-item-label">Request Errors</div>
        </div>
      </div>
    </div>
  );
}
