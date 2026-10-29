import React from 'react';
import { Info } from 'lucide-react';

export default function HealthScoreCard({ healthScore, pagesScanned }) {
  const score = healthScore?.score ?? 0;
  const rating = healthScore?.rating ?? 'N/A';
  const formula = healthScore?.calculation_formula ?? 'Score calculated based on weighted severity deductions normalized per page.';

  // Color scheme
  let scoreColor = '#16a34a'; // green
  let scoreBg = '#f0fdf4';
  let ratingBadgeClass = 'badge-medium';

  if (score >= 80) {
    scoreColor = '#16a34a';
    scoreBg = '#f0fdf4';
    ratingBadgeClass = 'badge-low';
  } else if (score >= 60) {
    scoreColor = '#d97706';
    scoreBg = '#fffbeb';
    ratingBadgeClass = 'badge-high';
  } else {
    scoreColor = '#dc2626';
    scoreBg = '#fef2f2';
    ratingBadgeClass = 'badge-critical';
  }

  return (
    <div className="card health-score-card">
      <div
        className="radial-score-container"
        style={{
          background: scoreBg,
          borderRadius: '50%',
          border: `5px solid ${scoreColor}`
        }}
      >
        <div className="score-number" style={{ color: scoreColor }}>
          {score}
        </div>
      </div>

      <div
        className={`score-rating-badge`}
        style={{ background: scoreBg, color: scoreColor, border: `1px solid ${scoreColor}` }}
      >
        {rating}
      </div>

      <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#0f172a', marginBottom: '0.25rem' }}>
        Technical Health Score
      </div>

      <div className="score-explanation">
        <strong>Calculation:</strong> {formula}
      </div>

      <div style={{ marginTop: '0.75rem', fontSize: '0.72rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
        <Info size={12} />
        Priorities represent technical hygiene, not guaranteed search rankings.
      </div>
    </div>
  );
}
