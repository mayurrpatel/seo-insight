import React, { useState } from 'react';
import {
  Globe,
  Sliders,
  AlertCircle,
  Play,
  CheckCircle2,
  Lock,
  Layers,
  FileCheck
} from 'lucide-react';

export default function AuditForm({ onStartAudit, onLoadSample, isLoading }) {
  const [url, setUrl] = useState('');
  const [maxPages, setMaxPages] = useState(12);
  const [showOptions, setShowOptions] = useState(false);
  const [inputError, setInputError] = useState('');

  const validateUrl = (val) => {
    if (!val.trim()) {
      return 'Please enter a website URL.';
    }
    const clean = val.trim();
    if (!clean.startsWith('http://') && !clean.startsWith('https://')) {
      return 'URL must start with http:// or https:// (e.g. https://example.com)';
    }
    try {
      new URL(clean);
    } catch {
      return 'Please enter a syntactically valid URL.';
    }
    return '';
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const err = validateUrl(url);
    if (err) {
      setInputError(err);
      return;
    }
    setInputError('');
    onStartAudit(url.trim(), maxPages);
  };

  return (
    <div>
      <div className="landing-hero">
        <div className="hero-pill">
          <FileCheck size={14} />
          Rule-Based Technical SEO Auditor
        </div>
        <h1 className="hero-title">
          Website SEO Audit &amp; Fix Prioritizer
        </h1>
        <p className="hero-subtitle">
          Crawl authorized public websites, detect technical and on-page SEO issues,
          and generate evidence-backed, prioritized action items to optimize crawl health.
        </p>
      </div>

      <div className="audit-card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="website-url">
              Permitted Target Website URL
            </label>
            <div className="input-with-button">
              <input
                id="website-url"
                type="text"
                className="url-input"
                placeholder="https://example.com"
                value={url}
                onChange={(e) => {
                  setUrl(e.target.value);
                  if (inputError) setInputError('');
                }}
                disabled={isLoading}
                autoFocus
              />
              <button
                type="submit"
                className="btn btn-primary"
                disabled={isLoading}
              >
                <Play size={16} />
                {isLoading ? 'Starting...' : 'Start Audit'}
              </button>
            </div>
            {inputError && (
              <div className="input-error">
                <AlertCircle size={15} />
                {inputError}
              </div>
            )}
          </div>

          <button
            type="button"
            className="options-toggle"
            onClick={() => setShowOptions(!showOptions)}
          >
            <Sliders size={14} />
            {showOptions ? 'Hide Crawl Settings' : 'Advanced Crawl Settings'}
          </button>

          {showOptions && (
            <div className="options-panel">
              <div>
                <label className="form-label" style={{ fontSize: '0.8rem' }}>
                  Max Crawl Depth / Pages: <strong>{maxPages} pages</strong>
                </label>
                <input
                  type="range"
                  min="3"
                  max="25"
                  value={maxPages}
                  onChange={(e) => setMaxPages(parseInt(e.target.value, 10))}
                  style={{ width: '100%', cursor: 'pointer' }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#64748b' }}>
                  <span>3 pages</span>
                  <span>12 (recommended)</span>
                  <span>25 max</span>
                </div>
              </div>
              <div style={{ fontSize: '0.8rem', color: '#64748b', display: 'flex', alignItems: 'center' }}>
                Restricted to submitted domain. Obeys robots.txt, applies 8s request timeout, and prevents request storms.
              </div>
            </div>
          )}

          <div className="security-notice">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 600, color: '#1e40af', marginBottom: '0.2rem' }}>
              <Lock size={14} />
              Responsible Crawling &amp; SSRF Safeguards
            </div>
            Audits are restricted to public addresses. Requests to localhost, private IP ranges (10.x, 192.168.x, 127.x), and cloud metadata endpoints are strictly blocked.
          </div>
        </form>

        <div className="demo-trigger">
          <div className="demo-info">
            <h4>Want to inspect an instant audit report?</h4>
            <p>Explore an illustrative SaaS company audit report with complete findings and evidence.</p>
          </div>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onLoadSample}
            disabled={isLoading}
          >
            Load Sample Report
          </button>
        </div>
      </div>

      <div className="features-grid">
        <div className="feature-box">
          <div className="feature-icon">
            <Layers size={20} />
          </div>
          <h3 className="feature-title">Multi-Layer SEO Checks</h3>
          <p className="feature-desc">
            Detects missing or duplicate titles, meta descriptions, H1 hierarchy, missing image alts, canonical errors, robots directives, and sitemaps.
          </p>
        </div>

        <div className="feature-box">
          <div className="feature-icon">
            <CheckCircle2 size={20} />
          </div>
          <h3 className="feature-title">Weighted Health Score</h3>
          <p className="feature-desc">
            Calculates an evidence-backed Technical SEO Health Score (0–100) using transparent, normalized deductions based on issue severity per page.
          </p>
        </div>

        <div className="feature-box">
          <div className="feature-icon">
            <Globe size={20} />
          </div>
          <h3 className="feature-title">Actionable Prioritization</h3>
          <p className="feature-desc">
            Every detected issue includes severity ranking, priority score, affected URL, raw evidence, SEO impact explanation, and exact fix guidance.
          </p>
        </div>
      </div>
    </div>
  );
}
