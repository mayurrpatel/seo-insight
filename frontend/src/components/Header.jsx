import React from 'react';
import { ShieldCheck, PlayCircle, RotateCcw } from 'lucide-react';

export default function Header({ onReset, onLoadSample, isScanning, hasResults }) {
  return (
    <header className="app-header">
      <div className="header-container">
        <div className="brand-group" onClick={onReset} title="Return to home">
          <div className="brand-logo">
            <ShieldCheck size={22} />
          </div>
          <div className="brand-title">
            SEO <span>Insight</span>
            <span className="brand-tag">Audit & Prioritizer</span>
          </div>
        </div>

        <div className="header-actions">
          {hasResults && (
            <button
              className="btn btn-secondary"
              onClick={onReset}
              disabled={isScanning}
            >
              <RotateCcw size={15} />
              New Audit
            </button>
          )}

          <button
            className="btn btn-outline-primary"
            onClick={onLoadSample}
            disabled={isScanning}
            title="Load illustrative audit report"
          >
            <PlayCircle size={16} />
            Try Sample Demo
          </button>
        </div>
      </div>
    </header>
  );
}
