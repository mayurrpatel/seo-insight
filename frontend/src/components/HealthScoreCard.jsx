import React, { useState } from 'react';
import { Info, HelpCircle, CheckCircle2, AlertOctagon, AlertTriangle, AlertCircle } from 'lucide-react';

export default function HealthScoreCard({ healthScore, pagesScanned }) {
  const [showFormulaModal, setShowFormulaModal] = useState(false);

  const score = healthScore?.score ?? 0;
  const rating = healthScore?.rating ?? 'N/A';
  const formula = healthScore?.calculation_formula ?? 'Score calculated based on weighted severity deductions normalized per page.';

  // SVG Gauge calculations
  const size = 180;
  const strokeWidth = 12;
  const center = size / 2;
  const radius = center - strokeWidth;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  let strokeColor = '#16a34a';
  let badgeClass = 'badge-low';
  let glowColor = 'rgba(22, 163, 74, 0.2)';

  if (score >= 80) {
    strokeColor = '#16a34a';
    glowColor = 'rgba(22, 163, 74, 0.25)';
    badgeClass = 'score-pill-excellent';
  } else if (score >= 60) {
    strokeColor = '#d97706';
    glowColor = 'rgba(217, 119, 6, 0.25)';
    badgeClass = 'score-pill-good';
  } else {
    strokeColor = '#dc2626';
    glowColor = 'rgba(220, 38, 38, 0.25)';
    badgeClass = 'score-pill-poor';
  }

  return (
    <div className="card health-score-card">
      <div className="radial-score-container" style={{ width: size, height: size }}>
        <svg width={size} height={size} style={{ transform: 'rotate(-90deg)', filter: `drop-shadow(0 4px 12px ${glowColor})` }}>
          {/* Background track */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            stroke="#f1f5f9"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Animated score stroke */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            fill="transparent"
            style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
          />
        </svg>

        <div className="score-number-overlay">
          <div className="score-number" style={{ color: strokeColor }}>
            {score}
          </div>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase' }}>
            Out of 100
          </span>
        </div>
      </div>

      <div className={`score-rating-badge ${badgeClass}`}>
        {rating}
      </div>

      <div style={{ fontSize: '0.875rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.35rem' }}>
        Technical SEO Health Score
      </div>

      <button
        type="button"
        className="formula-trigger-btn"
        onClick={() => setShowFormulaModal(!showFormulaModal)}
        title="View mathematical deduction formula"
      >
        <HelpCircle size={14} />
        {showFormulaModal ? 'Hide Calculation' : 'How is this calculated?'}
      </button>

      {showFormulaModal && (
        <div className="score-explanation">
          <strong>Formula:</strong> {formula}
          <div style={{ marginTop: '0.4rem', fontSize: '0.75rem' }}>
            Weights: Critical (-25pts), High (-15pts), Medium (-8pts), Low (-3pts).
          </div>
        </div>
      )}

      <div style={{ marginTop: '0.75rem', fontSize: '0.72rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
        <Info size={12} />
        Represents technical crawl health, not guaranteed search rankings.
      </div>
    </div>
  );
}
