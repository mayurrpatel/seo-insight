import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import AuditForm from './components/AuditForm';
import AuditProgress from './components/AuditProgress';
import HealthScoreCard from './components/HealthScoreCard';
import StatsOverview from './components/StatsOverview';
import IssueDistributionChart from './components/IssueDistributionChart';
import IssueTable from './components/IssueTable';
import IssueDetailModal from './components/IssueDetailModal';
import CrawlSummary from './components/CrawlSummary';
import ExportActions from './components/ExportActions';

import {
  startAudit,
  fetchAuditStatus,
  fetchAuditResult,
  fetchSampleAudit
} from './utils/api';
import { ExternalLink, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function App() {
  const [viewState, setViewState] = useState('IDLE'); // IDLE, SCANNING, RESULTS, ERROR
  const [auditId, setAuditId] = useState(null);
  const [statusData, setStatusData] = useState(null);
  const [auditResult, setAuditResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [selectedIssue, setSelectedIssue] = useState(null);

  const pollIntervalRef = useRef(null);

  // Clean up polling timer
  const stopPolling = () => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  };

  useEffect(() => {
    return () => stopPolling();
  }, []);

  const handleStartAudit = async (targetUrl, maxPages) => {
    setErrorMessage('');
    setViewState('SCANNING');
    setStatusData({ pages_scanned: 0, pages_discovered: 1, status_message: 'Submitting audit request...' });

    try {
      const initResp = await startAudit(targetUrl, maxPages);
      const newAuditId = initResp.audit_id;
      setAuditId(newAuditId);

      // Begin polling status
      pollIntervalRef.current = setInterval(async () => {
        try {
          const statusResp = await fetchAuditStatus(newAuditId);
          setStatusData(statusResp);

          if (statusResp.status === 'completed') {
            stopPolling();
            const resultResp = await fetchAuditResult(newAuditId);
            setAuditResult(resultResp);
            setViewState('RESULTS');
          } else if (statusResp.status === 'failed') {
            stopPolling();
            setErrorMessage(statusResp.error || statusResp.status_message || 'Audit crawl encountered a fatal error.');
            setViewState('ERROR');
          }
        } catch (pollErr) {
          stopPolling();
          setErrorMessage(pollErr.message || 'Lost connection to audit service.');
          setViewState('ERROR');
        }
      }, 1000);
    } catch (err) {
      setErrorMessage(err.message || 'Failed to start audit.');
      setViewState('ERROR');
    }
  };

  const handleLoadSample = async () => {
    stopPolling();
    setErrorMessage('');
    try {
      const sampleData = await fetchSampleAudit();
      setAuditId(sampleData.audit_id);
      setAuditResult(sampleData);
      setViewState('RESULTS');
    } catch (err) {
      setErrorMessage('Failed to load sample audit report.');
      setViewState('ERROR');
    }
  };

  const handleReset = () => {
    stopPolling();
    setAuditId(null);
    setStatusData(null);
    setAuditResult(null);
    setErrorMessage('');
    setSelectedIssue(null);
    setViewState('IDLE');
  };

  return (
    <div className="app-wrapper">
      <Header
        onReset={handleReset}
        onLoadSample={handleLoadSample}
        isScanning={viewState === 'SCANNING'}
        hasResults={viewState === 'RESULTS'}
      />

      <main className="main-content">
        {viewState === 'IDLE' && (
          <AuditForm
            onStartAudit={handleStartAudit}
            onLoadSample={handleLoadSample}
            isLoading={false}
          />
        )}

        {viewState === 'SCANNING' && (
          <AuditProgress
            statusData={statusData}
            onCancel={handleReset}
          />
        )}

        {viewState === 'ERROR' && (
          <div className="card" style={{ maxWidth: '640px', margin: '3rem auto', textAlign: 'center', padding: '2.5rem' }}>
            <div style={{
              width: '54px',
              height: '54px',
              borderRadius: '50%',
              background: '#fef2f2',
              color: '#dc2626',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.25rem'
            }}>
              <AlertTriangle size={28} />
            </div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.75rem' }}>
              Audit Interrupted
            </h2>
            <p style={{ color: '#64748b', fontSize: '0.95rem', marginBottom: '1.75rem', lineHeight: 1.6 }}>
              {errorMessage}
            </p>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '0.75rem' }}>
              <button className="btn btn-primary" onClick={handleReset}>
                Try Another URL
              </button>
              <button className="btn btn-secondary" onClick={handleLoadSample}>
                View Sample Report Instead
              </button>
            </div>
          </div>
        )}

        {viewState === 'RESULTS' && auditResult && (
          <div>
            {auditResult.is_sample && (
              <div className="sample-notice-banner">
                <ShieldCheck size={18} />
                <span>
                  <strong>Sample Audit Report:</strong> {auditResult.sample_notice || 'This is an illustrative report for evaluation and demonstration purposes.'}
                </span>
              </div>
            )}

            <div className="dashboard-header">
              <div className="dashboard-title-group">
                <h1>SEO Audit Dashboard</h1>
                <div className="dashboard-target-url">
                  <strong>Target:</strong>
                  <a
                    href={auditResult.target_url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {auditResult.target_url}
                    <ExternalLink size={13} style={{ marginLeft: '4px', verticalAlign: 'middle' }} />
                  </a>
                  <span style={{ color: '#94a3b8', margin: '0 0.5rem' }}>•</span>
                  <span>{auditResult.timestamp}</span>
                </div>
              </div>

              <ExportActions auditId={auditResult.audit_id} />
            </div>

            <div className="score-overview-grid">
              <HealthScoreCard
                healthScore={auditResult.health_score}
                pagesScanned={auditResult.pages_scanned}
              />
              <StatsOverview auditData={auditResult} />
            </div>

            <IssueDistributionChart healthScore={auditResult.health_score} />

            <IssueTable
              issues={auditResult.issues || []}
              onSelectIssue={(issue) => setSelectedIssue(issue)}
            />

            <CrawlSummary crawledUrls={auditResult.crawled_urls || []} />
          </div>
        )}
      </main>

      <IssueDetailModal
        issue={selectedIssue}
        onClose={() => setSelectedIssue(null)}
      />

      <footer className="app-footer">
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 1.5rem' }}>
          SEO Insight — Website SEO Audit &amp; Fix Prioritizer • Internship Assessment
        </div>
      </footer>
    </div>
  );
}
