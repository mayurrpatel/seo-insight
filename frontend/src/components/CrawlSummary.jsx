import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Link as LinkIcon } from 'lucide-react';

export default function CrawlSummary({ crawledUrls = [] }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!crawledUrls || crawledUrls.length === 0) return null;

  return (
    <div className="card" style={{ marginBottom: '2rem' }}>
      <div
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: 'pointer',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <LinkIcon size={18} color="#2563eb" />
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a' }}>
            Crawled Page Inventory ({crawledUrls.length} pages)
          </h3>
        </div>
        <button
          type="button"
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}
        >
          {isOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </button>
      </div>

      {isOpen && (
        <div style={{ marginTop: '1rem', borderTop: '1px solid #e2e8f0', paddingTop: '1rem' }}>
          <div className="crawl-list">
            {crawledUrls.map((p, idx) => {
              const code = p.status_code || 0;
              let statusBg = '#f0fdf4';
              let statusColor = '#166534';
              if (code >= 400 || p.error) {
                statusBg = '#fef2f2';
                statusColor = '#991b1b';
              } else if (code >= 300) {
                statusBg = '#eff6ff';
                statusColor = '#1d4ed8';
              }

              return (
                <div key={idx} className="crawl-item">
                  <span className="crawl-item-url" title={p.url}>
                    {p.url}
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                      {p.response_time_ms}ms
                    </span>
                    <span style={{
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      padding: '0.15rem 0.45rem',
                      borderRadius: '4px',
                      background: statusBg,
                      color: statusColor
                    }}>
                      {p.error ? 'ERR' : `HTTP ${code}`}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
