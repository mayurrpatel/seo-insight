import React from 'react';
import { BarChart3, PieChart } from 'lucide-react';

export default function IssueDistributionChart({ healthScore }) {
  const sevCounts = healthScore?.severity_counts || { Critical: 0, High: 0, Medium: 0, Low: 0 };
  const catCounts = healthScore?.category_counts || {};
  const total = healthScore?.total_issues || 1;

  const severityConfigs = [
    { key: 'Critical', label: 'Critical', color: '#dc2626', count: sevCounts['Critical'] || 0 },
    { key: 'High', label: 'High Priority', color: '#ea580c', count: sevCounts['High'] || 0 },
    { key: 'Medium', label: 'Medium Priority', color: '#2563eb', count: sevCounts['Medium'] || 0 },
    { key: 'Low', label: 'Low Priority', color: '#64748b', count: sevCounts['Low'] || 0 },
  ];

  const categories = Object.entries(catCounts).map(([cat, count]) => ({
    name: cat,
    count,
    percent: Math.round((count / Math.max(1, total)) * 100),
  })).sort((a, b) => b.count - a.count);

  return (
    <div className="charts-grid">
      <div className="card chart-card">
        <h3>
          <BarChart3 size={18} color="#2563eb" />
          Findings by Severity Level
        </h3>
        {severityConfigs.map((item) => {
          const pct = Math.round((item.count / Math.max(1, total)) * 100);
          return (
            <div key={item.key} className="dist-bar-row">
              <div className="dist-bar-meta">
                <span style={{ color: item.color }}>{item.label}</span>
                <span>{item.count} issues ({pct}%)</span>
              </div>
              <div className="dist-bar-track">
                <div
                  className="dist-bar-inner"
                  style={{
                    width: `${pct}%`,
                    backgroundColor: item.color,
                  }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="card chart-card">
        <h3>
          <PieChart size={18} color="#2563eb" />
          Issues by SEO Domain Category
        </h3>
        {categories.length === 0 ? (
          <div style={{ color: '#64748b', fontSize: '0.85rem' }}>No issues found.</div>
        ) : (
          categories.map((cat, idx) => {
            const colors = ['#2563eb', '#0284c7', '#0d9488', '#d97706', '#64748b'];
            const barColor = colors[idx % colors.length];
            return (
              <div key={cat.name} className="dist-bar-row">
                <div className="dist-bar-meta">
                  <span style={{ color: '#1e293b' }}>{cat.name}</span>
                  <span>{cat.count} ({cat.percent}%)</span>
                </div>
                <div className="dist-bar-track">
                  <div
                    className="dist-bar-inner"
                    style={{
                      width: `${cat.percent}%`,
                      backgroundColor: barColor,
                    }}
                  ></div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
