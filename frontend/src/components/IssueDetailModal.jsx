import React, { useState } from 'react';
import { X, ExternalLink, AlertTriangle, Wrench, Copy, Check } from 'lucide-react';

export default function IssueDetailModal({ issue, onClose }) {
  const [copied, setCopied] = useState(false);

  if (!issue) return null;

  const sevClass = (issue.severity || 'low').toLowerCase();

  const handleCopyFix = () => {
    if (issue.suggested_fix) {
      navigator.clipboard.writeText(issue.suggested_fix);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem', flexWrap: 'wrap' }}>
              <span className={`badge badge-${sevClass}`}>
                {issue.severity}
              </span>
              <span className="badge badge-category">
                {issue.category}
              </span>
              <span className="priority-score-pill">
                Priority Score: {issue.priority_score}/100
              </span>
            </div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f172a' }}>
              {issue.title}
            </h2>
          </div>
          <button className="modal-close-btn" onClick={onClose} title="Close modal">
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          <div className="modal-section">
            <div className="modal-section-title">Affected Page URL</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', wordBreak: 'break-all' }}>
              <code style={{ fontSize: '0.85rem', color: '#0f172a', background: '#f1f5f9', padding: '0.35rem 0.65rem', borderRadius: '4px', flex: 1 }}>
                {issue.affected_url}
              </code>
              <a
                href={issue.affected_url}
                target="_blank"
                rel="noopener noreferrer"
                title="Open page in new window"
                style={{ color: '#2563eb', padding: '0.3rem', borderRadius: '4px' }}
              >
                <ExternalLink size={16} />
              </a>
            </div>
          </div>

          <div className="modal-section">
            <div className="modal-section-title">Detected Evidence</div>
            <div className="evidence-box">
              {issue.evidence}
            </div>
          </div>

          <div className="modal-section">
            <div className="modal-section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <AlertTriangle size={14} color="#d97706" />
              Why It Matters (Search &amp; User Experience Impact)
            </div>
            <div className="impact-box">
              {issue.impact}
            </div>
          </div>

          <div className="modal-section">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
              <div className="modal-section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', margin: 0 }}>
                <Wrench size={14} color="#16a34a" />
                Actionable Fix Guidance
              </div>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ padding: '0.25rem 0.55rem', fontSize: '0.75rem', gap: '0.3rem' }}
                onClick={handleCopyFix}
                title="Copy suggested fix to clipboard"
              >
                {copied ? <Check size={13} color="#16a34a" /> : <Copy size={13} />}
                {copied ? 'Copied!' : 'Copy Fix'}
              </button>
            </div>
            <div className="fix-box">
              {issue.suggested_fix}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
