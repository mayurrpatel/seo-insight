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
import AuditHistoryModal from './components/AuditHistoryModal';

import {
  startAudit,
  fetchAuditStatus,
  fetchAuditResult,
  fetchSampleAudit,
  fetchAuditHistory,
  deleteAudit
} from './utils/api';
import { ExternalLink, AlertTriangle, ShieldCheck, History } from 'lucide-react';

export default function App() {
  const [viewState, setViewState] = useState('IDLE'); // IDLE, SCANNING, RESULTS, ERROR
  const [auditId, setAuditId] = useState(null);
  const [statusData, setStatusData] = useState(null);
  const [auditResult, setAuditResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [selectedIssue, setSelectedIssue] = useState(null);

  // History state
  const [history, setHistory] = useState([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  const pollIntervalRef = useRef(null);

  const loadHistory = async () => {
    try {
      const resp = await fetchAuditHistory();
      if (resp && resp.history) {
        setHistory(resp.history);
      }
    } catch {
      // Non-fatal if backend is warming up
    }
  };

  useEffect(() => {
    loadHistory();
    return () => stopPolling();
  }, []);

  const stopPolling = () => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  };

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
            // Refresh saved database history
            loadHistory();
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
      loadHistory();
    } catch {
      setErrorMessage('Failed to load sample audit report.');
      setViewState('ERROR');
    }
  };

  const handleSelectAudit = async (id) => {
    stopPolling();
    setErrorMessage('');
    try {
      const data = await fetchAuditResult(id);
      setAuditId(id);
      setAuditResult(data);
      setViewState('RESULTS');
    } catch (err) {
      setErrorMessage(`Failed to load audit report ${id}: ${err.message}`);
      setViewState('ERROR');
    }
  };

  const handleDeleteAudit = async (id) => {
    await deleteAudit(id);
    await loadHistory();
    if (auditId === id) {
      handleReset();
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
    loadHistory();
  };

  return (
    <div className="app-wrapper">
      <Header
        onReset={handleReset}
        onLoadSample={handleLoadSample}
        onOpenHistory={() => setIsHistoryOpen(true)}
        historyCount={history.length}
        isScanning={viewState === 'SCANNING'}
        hasResults={viewState === 'RESULTS'}
      />

      <main className="main-content">
        {viewState === 'IDLE' && (
          <AuditForm
            onStartAudit={handleStartAudit}
            onLoadSample={handleLoadSample}
            onOpenHistory={() => setIsHistoryOpen(true)}
            history={history}
            onSelectAudit={handleSelectAudit}
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
            <div style={{ display: 'flex', justifyContent: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
              <button className="btn btn-primary" onClick={handleReset}>
                Try Another URL
              </button>
              <button className="btn btn-secondary" onClick={handleLoadSample}>
                View Sample Report
              </button>
              {history.length > 0 && (
                <button className="btn btn-secondary" onClick={() => setIsHistoryOpen(true)}>
                  <History size={15} />
                  Open Saved Reports ({history.length})
                </button>
              )}
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

              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setIsHistoryOpen(true)}
                  title="View saved audits database"
                >
                  <History size={16} />
                  History ({history.length})
                </button>
                <ExportActions auditId={auditResult.audit_id} />
              </div>
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

      <AuditHistoryModal
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        history={history}
        onSelectAudit={handleSelectAudit}
        onDeleteAudit={handleDeleteAudit}
      />

      <footer className="app-footer">
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
          <span>SEO Insight — Website SEO Audit &amp; Fix Prioritizer • Internship Assessment</span>
          <span>SQLite Database Persistence Active</span>
        </div>
      </footer>
    </div>
  );
}
