import React, { useState } from 'react';
import {
  X,
  History,
  Search,
  ExternalLink,
  Trash2,
  Download,
  ArrowRight,
  ShieldAlert,
  Globe,
  Calendar,
  Layers
} from 'lucide-react';
import { getCsvExportUrl } from '../utils/api';

export default function AuditHistoryModal({
  isOpen,
  onClose,
  history = [],
  onSelectAudit,
  onDeleteAudit
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [deletingId, setDeletingId] = useState(null);

  if (!isOpen) return null;

  const filteredHistory = history.filter((item) => {
    if (!searchTerm.trim()) return true;
    const q = searchTerm.toLowerCase();
    return (
      item.domain?.toLowerCase().includes(q) ||
      item.target_url?.toLowerCase().includes(q)
    );
  });

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this saved audit report?')) {
      setDeletingId(id);
      try {
        await onDeleteAudit(id);
      } finally {
        setDeletingId(null);
      }
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#16a34a';
    if (score >= 60) return '#d97706';
    return '#dc2626';
  };

  const getScoreBg = (score) => {
    if (score >= 80) return '#f0fdf4';
    if (score >= 60) return '#fffbeb';
    return '#fef2f2';
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-container history-modal-container"
        onClick={(e) => e.stopPropagation()}
        style={{ maxWidth: '840px', width: '100%' }}
      >
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div style={{ background: '#eff6ff', color: '#2563eb', padding: '0.5rem', borderRadius: '8px' }}>
              <History size={20} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f172a' }}>
                Audited Reports Database
              </h2>
              <p style={{ fontSize: '0.8rem', color: '#64748b' }}>
                {history.length} saved audit report{history.length !== 1 ? 's' : ''} stored in SQLite
              </p>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose} title="Close history">
            <X size={20} />
          </button>
        </div>

        <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid #e2e8f0', background: '#f8fafc' }}>
          <div className="search-box" style={{ maxWidth: '100%' }}>
            <Search size={16} className="search-icon" />
            <input
              type="text"
              className="search-input"
              placeholder="Search saved audits by domain or URL..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              autoFocus
            />
          </div>
        </div>

        <div className="modal-body" style={{ maxHeight: '65vh', overflowY: 'auto', padding: '1.25rem 1.5rem' }}>
          {filteredHistory.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem 1rem', color: '#64748b' }}>
              <History size={40} style={{ color: '#cbd5e1', marginBottom: '0.75rem' }} />
              <p style={{ fontWeight: 600 }}>No audited reports found.</p>
              <p style={{ fontSize: '0.85rem' }}>Run an audit to automatically save findings in the database.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {filteredHistory.map((item) => {
                const score = item.health_score ?? 0;
                const scoreColor = getScoreColor(score);
                const scoreBg = getScoreBg(score);

                return (
                  <div
                    key={item.id}
                    className="history-card-item"
                    onClick={() => {
                      onSelectAudit(item.id);
                      onClose();
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', flexWrap: 'wrap', flex: 1 }}>
                      {/* Mini Score Gauge */}
                      <div
                        style={{
                          width: '54px',
                          height: '54px',
                          borderRadius: '50%',
                          background: scoreBg,
                          border: `3px solid ${scoreColor}`,
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 800,
                          fontSize: '1.15rem',
                          color: scoreColor,
                          flexShrink: 0
                        }}
                      >
                        {score}
                      </div>

                      {/* Site Details */}
                      <div style={{ flex: 1, minWidth: '220px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
                          <span style={{ fontWeight: 700, fontSize: '1rem', color: '#0f172a' }}>
                            {item.domain}
                          </span>
                          {item.is_sample ? (
                            <span className="badge badge-low" style={{ fontSize: '0.65rem' }}>Sample</span>
                          ) : null}
                        </div>

                        <div style={{ fontSize: '0.8rem', color: '#64748b', wordBreak: 'break-all', marginBottom: '0.4rem' }}>
                          {item.target_url}
                        </div>

                        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                            <Calendar size={12} />
                            {item.timestamp?.split(' ')[0] || item.created_at?.split('T')[0]}
                          </span>
                          <span style={{ color: '#cbd5e1' }}>•</span>
                          <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                            <Layers size={12} />
                            {item.pages_scanned} pages
                          </span>
                          <span style={{ color: '#cbd5e1' }}>•</span>
                          {/* Issue counts */}
                          <div style={{ display: 'flex', gap: '0.35rem' }}>
                            {item.critical_count > 0 && (
                              <span className="badge badge-critical" style={{ fontSize: '0.65rem', padding: '0.1rem 0.4rem' }}>
                                {item.critical_count} Crit
                              </span>
                            )}
                            {item.high_count > 0 && (
                              <span className="badge badge-high" style={{ fontSize: '0.65rem', padding: '0.1rem 0.4rem' }}>
                                {item.high_count} High
                              </span>
                            )}
                            {item.medium_count > 0 && (
                              <span className="badge badge-medium" style={{ fontSize: '0.65rem', padding: '0.1rem 0.4rem' }}>
                                {item.medium_count} Med
                              </span>
                            )}
                            {item.low_count > 0 && (
                              <span className="badge badge-low" style={{ fontSize: '0.65rem', padding: '0.1rem 0.4rem' }}>
                                {item.low_count} Low
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <a
                        href={getCsvExportUrl(item.id)}
                        download
                        className="btn btn-secondary"
                        style={{ padding: '0.4rem 0.6rem', fontSize: '0.8rem' }}
                        title="Download CSV"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <Download size={14} />
                      </a>

                      <button
                        type="button"
                        className="btn btn-secondary"
                        style={{ padding: '0.4rem 0.6rem', color: '#dc2626' }}
                        title="Delete audit"
                        disabled={deletingId === item.id}
                        onClick={(e) => handleDelete(e, item.id)}
                      >
                        <Trash2 size={14} />
                      </button>

                      <button
                        type="button"
                        className="btn btn-primary"
                        style={{ padding: '0.4rem 0.85rem', fontSize: '0.8rem' }}
                      >
                        View Report
                        <ArrowRight size={14} />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
