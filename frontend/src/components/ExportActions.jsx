import React from 'react';
import { Download, FileCode, Printer } from 'lucide-react';
import { getCsvExportUrl, getHtmlReportUrl } from '../utils/api';

export default function ExportActions({ auditId }) {
  if (!auditId) return null;

  const csvUrl = getCsvExportUrl(auditId);
  const htmlUrl = getHtmlReportUrl(auditId);

  const handlePrint = () => {
    // Open HTML report in a new tab for printing to PDF
    window.open(htmlUrl, '_blank');
  };

  return (
    <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
      <a
        href={csvUrl}
        className="btn btn-secondary"
        download
        title="Download audit findings as RFC 4180 CSV"
      >
        <Download size={16} />
        Download CSV
      </a>

      <a
        href={htmlUrl}
        className="btn btn-secondary"
        download
        title="Download standalone HTML report"
      >
        <FileCode size={16} />
        Download HTML Report
      </a>

      <button
        type="button"
        className="btn btn-primary"
        onClick={handlePrint}
        title="Open printable executive report"
      >
        <Printer size={16} />
        Print / Save PDF
      </button>
    </div>
  );
}
