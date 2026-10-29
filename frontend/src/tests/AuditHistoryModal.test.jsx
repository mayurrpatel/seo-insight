import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import AuditHistoryModal from '../components/AuditHistoryModal';

describe('AuditHistoryModal component', () => {
  const mockHistory = [
    {
      id: 'audit-1',
      domain: 'example.com',
      target_url: 'https://example.com',
      health_score: 92,
      pages_scanned: 10,
      total_issues: 3,
      critical_count: 0,
      high_count: 1,
      medium_count: 2,
      low_count: 0,
      timestamp: '2026-10-29 12:00:00 UTC',
    },
    {
      id: 'audit-2',
      domain: 'acme.org',
      target_url: 'https://acme.org',
      health_score: 64,
      pages_scanned: 15,
      total_issues: 8,
      critical_count: 1,
      high_count: 3,
      medium_count: 2,
      low_count: 2,
      timestamp: '2026-10-28 10:00:00 UTC',
    },
  ];

  it('renders saved audits history list', () => {
    render(
      <AuditHistoryModal
        isOpen={true}
        onClose={() => {}}
        history={mockHistory}
        onSelectAudit={() => {}}
        onDeleteAudit={() => {}}
      />
    );

    expect(screen.getByText('Audited Reports Database')).toBeDefined();
    expect(screen.getByText('example.com')).toBeDefined();
    expect(screen.getByText('acme.org')).toBeDefined();
    expect(screen.getByText('92')).toBeDefined();
    expect(screen.getByText('64')).toBeDefined();
  });

  it('filters history list by search input', () => {
    render(
      <AuditHistoryModal
        isOpen={true}
        onClose={() => {}}
        history={mockHistory}
        onSelectAudit={() => {}}
        onDeleteAudit={() => {}}
      />
    );

    const input = screen.getByPlaceholderText(/Search saved audits/i);
    fireEvent.change(input, { target: { value: 'acme' } });

    expect(screen.getByText('acme.org')).toBeDefined();
    expect(screen.queryByText('example.com')).toBeNull();
  });
});
