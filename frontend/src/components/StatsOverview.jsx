import React from 'react';
import { Check, X, FileText, Layers, ShieldAlert } from 'lucide-react';

export default function StatsOverview({ auditData }) {
  const health = auditData?.health_score || {};
  const pagesScanned = auditData?.pages_scanned || 0;
  const totalIssues = health?.total_issues || 0;
  const critical = health?.critical_count || 0;
  const high = health?.high_count || 0;
  const medium = health?.medium_count || 0;
  const low = health?.low_count || 0;

  const robotsFound = auditData?.robots_txt_found;
  const sitemapFound = auditData?.sitemap_found;

  return (
    <div className="stats-grid">
      <div className="metric-tile">
        <div className="metric-tile-title">Pages Scanned</div>
        <div className="metric-tile-value">{pagesScanned}</div>
        <div style={{ marginTop: '0.4rem', fontSize: '0.75rem', color: '#64748b' }}>
          Crawl depth target
        </div>
      </div>

      <div className="metric-tile">
        <div className="metric-tile-title">Total Issues</div>
        <div className="metric-tile-value">{totalIssues}</div>
        <div style={{ marginTop: '0.4rem', fontSize: '0.75rem', color: '#64748b' }}>
          Across all categories
        </div>
      </div>

      <div className="metric-tile" style={{ borderLeft: '4px solid #dc2626' }}>
        <div className="metric-tile-title" style={{ color: '#dc2626' }}>Critical</div>
        <div className="metric-tile-value" style={{ color: '#dc2626' }}>{critical}</div>
        <div style={{ marginTop: '0.4rem', fontSize: '0.75rem', color: '#64748b' }}>
          Immediate action
        </div>
      </div>

      <div className="metric-tile" style={{ borderLeft: '4px solid #ea580c' }}>
        <div className="metric-tile-title" style={{ color: '#ea580c' }}>High</div>
        <div className="metric-tile-value" style={{ color: '#ea580c' }}>{high}</div>
        <div style={{ marginTop: '0.4rem', fontSize: '0.75rem', color: '#64748b' }}>
          Key optimization
        </div>
      </div>

      <div className="metric-tile" style={{ borderLeft: '4px solid #2563eb' }}>
        <div className="metric-tile-title" style={{ color: '#2563eb' }}>Medium</div>
        <div className="metric-tile-value" style={{ color: '#2563eb' }}>{medium}</div>
        <div style={{ marginTop: '0.4rem', fontSize: '0.75rem', color: '#64748b' }}>
          Recommended
        </div>
      </div>

      <div className="metric-tile" style={{ borderLeft: '4px solid #64748b' }}>
        <div className="metric-tile-title">Low</div>
        <div className="metric-tile-value" style={{ color: '#64748b' }}>{low}</div>
        <div style={{ marginTop: '0.4rem', fontSize: '0.75rem', color: '#64748b' }}>
          Minor hygiene
        </div>
      </div>

      <div className="metric-tile" style={{ gridColumn: 'span 2' }}>
        <div className="metric-tile-title">Crawl Directives</div>
        <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.35rem', flexWrap: 'wrap' }}>
          <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.3rem',
            fontSize: '0.8rem',
            padding: '0.2rem 0.5rem',
            borderRadius: '4px',
            background: robotsFound ? '#f0fdf4' : '#fef2f2',
            color: robotsFound ? '#166534' : '#991b1b',
            border: `1px solid ${robotsFound ? '#bbf7d0' : '#fecaca'}`
          }}>
            {robotsFound ? <Check size={13} /> : <X size={13} />}
            robots.txt: {robotsFound ? 'Detected' : 'Missing'}
          </span>

          <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.3rem',
            fontSize: '0.8rem',
            padding: '0.2rem 0.5rem',
            borderRadius: '4px',
            background: sitemapFound ? '#f0fdf4' : '#fffbeb',
            color: sitemapFound ? '#166534' : '#92400e',
            border: `1px solid ${sitemapFound ? '#bbf7d0' : '#fde68a'}`
          }}>
            {sitemapFound ? <Check size={13} /> : <X size={13} />}
            sitemap.xml: {sitemapFound ? 'Detected' : 'Missing'}
          </span>
        </div>
      </div>
    </div>
  );
}
