import React, { useState, useMemo } from 'react';
import { Search, Filter, ExternalLink, ArrowUpDown, ChevronRight } from 'lucide-react';

export default function IssueTable({ issues = [], onSelectIssue }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState('PRIORITY_DESC');

  // Extract unique categories
  const categories = useMemo(() => {
    const set = new Set();
    issues.forEach((i) => i.category && set.add(i.category));
    return Array.from(set).sort();
  }, [issues]);

  // Filter & sort issues
  const filteredIssues = useMemo(() => {
    return issues
      .filter((item) => {
        // Severity filter
        if (severityFilter !== 'ALL' && item.severity?.toUpperCase() !== severityFilter) {
          return false;
        }
        // Category filter
        if (categoryFilter !== 'ALL' && item.category !== categoryFilter) {
          return false;
        }
        // Search term
        if (searchTerm.trim()) {
          const q = searchTerm.toLowerCase();
          const matchTitle = item.title?.toLowerCase().includes(q);
          const matchUrl = item.affected_url?.toLowerCase().includes(q);
          const matchEvidence = item.evidence?.toLowerCase().includes(q);
          const matchCategory = item.category?.toLowerCase().includes(q);
          return matchTitle || matchUrl || matchEvidence || matchCategory;
        }
        return true;
      })
      .sort((a, b) => {
        if (sortBy === 'PRIORITY_DESC') {
          return (b.priority_score || 0) - (a.priority_score || 0);
        }
        if (sortBy === 'PRIORITY_ASC') {
          return (a.priority_score || 0) - (b.priority_score || 0);
        }
        if (sortBy === 'SEVERITY') {
          const order = { Critical: 1, High: 2, Medium: 3, Low: 4 };
          return (order[a.severity] || 5) - (order[b.severity] || 5);
        }
        if (sortBy === 'TITLE') {
          return (a.title || '').localeCompare(b.title || '');
        }
        return 0;
      });
  }, [issues, searchTerm, severityFilter, categoryFilter, sortBy]);

  return (
    <div className="card table-card">
      <div className="table-controls">
        <div className="search-box">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search by issue title, affected URL, or evidence..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filters-group">
          <select
            className="filter-select"
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High Priority</option>
            <option value="MEDIUM">Medium Priority</option>
            <option value="LOW">Low Priority</option>
          </select>

          <select
            className="filter-select"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
          >
            <option value="ALL">All Categories</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>

          <select
            className="filter-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="PRIORITY_DESC">Sort: Priority Score (High → Low)</option>
            <option value="PRIORITY_ASC">Sort: Priority Score (Low → High)</option>
            <option value="SEVERITY">Sort: Severity</option>
            <option value="TITLE">Sort: Issue Title</option>
          </select>
        </div>
      </div>

      <div style={{ padding: '0.75rem 1.5rem', background: '#f8fafc', fontSize: '0.8rem', color: '#64748b', display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #e2e8f0' }}>
        <span>Showing <strong>{filteredIssues.length}</strong> of <strong>{issues.length}</strong> prioritized findings</span>
        {searchTerm && (
          <button
            onClick={() => setSearchTerm('')}
            style={{ background: 'none', border: 'none', color: '#2563eb', cursor: 'pointer', fontSize: '0.8rem' }}
          >
            Clear Search
          </button>
        )}
      </div>

      <div className="table-responsive">
        <table className="issues-table">
          <thead>
            <tr>
              <th style={{ width: '80px' }}>Priority</th>
              <th style={{ width: '110px' }}>Severity</th>
              <th>Issue Title &amp; Category</th>
              <th>Affected Target URL</th>
              <th style={{ textAlign: 'right', width: '120px' }}>Fix Guidance</th>
            </tr>
          </thead>
          <tbody>
            {filteredIssues.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center', padding: '3rem 1rem', color: '#64748b' }}>
                  No SEO findings matched your filter or search criteria.
                </td>
              </tr>
            ) : (
              filteredIssues.map((item) => {
                const sevClass = (item.severity || 'low').toLowerCase();
                return (
                  <tr key={item.id} onClick={() => onSelectIssue(item)} style={{ cursor: 'pointer' }}>
                    <td>
                      <span className="priority-score-pill">
                        {item.priority_score}
                      </span>
                    </td>
                    <td>
                      <span className={`badge badge-${sevClass}`}>
                        {item.severity}
                      </span>
                    </td>
                    <td>
                      <div className="table-issue-title">{item.title}</div>
                      <span className="badge badge-category">{item.category}</span>
                      {item.affected_count > 1 && (
                        <span style={{ fontSize: '0.75rem', color: '#64748b', marginLeft: '0.5rem' }}>
                          ({item.affected_count} occurrences)
                        </span>
                      )}
                    </td>
                    <td>
                      <div className="table-issue-url" title={item.affected_url}>
                        {item.affected_url}
                      </div>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        type="button"
                        className="btn btn-secondary"
                        style={{ padding: '0.35rem 0.65rem', fontSize: '0.78rem' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectIssue(item);
                        }}
                      >
                        Inspect
                        <ChevronRight size={14} />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
