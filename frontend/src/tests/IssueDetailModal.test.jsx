import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import IssueDetailModal from '../components/IssueDetailModal';

describe('IssueDetailModal component', () => {
  const mockIssue = {
    id: 'iss-1',
    title: 'Missing or Empty Title Tag',
    category: 'Meta Tags',
    severity: 'Critical',
    priority_score: 95,
    affected_url: 'https://example.com/checkout',
    evidence: '<title> tag is completely missing from <head>',
    impact: 'Search engines cannot identify primary page theme and display fallback snippets.',
    suggested_fix: 'Add a distinct <title> tag between 50-60 characters summarizing the page.',
  };

  it('renders modal details including evidence, impact, and fix guidance', () => {
    const handleClose = vi.fn();
    render(<IssueDetailModal issue={mockIssue} onClose={handleClose} />);

    expect(screen.getByText('Missing or Empty Title Tag')).toBeDefined();
    expect(screen.getByText(/<title> tag is completely missing/)).toBeDefined();
    expect(screen.getByText(/Search engines cannot identify primary page theme/)).toBeDefined();
    expect(screen.getByText(/Add a distinct <title> tag between 50-60 characters/)).toBeDefined();
  });

  it('invokes onClose when close button is clicked', () => {
    const handleClose = vi.fn();
    render(<IssueDetailModal issue={mockIssue} onClose={handleClose} />);

    const closeBtn = screen.getByTitle('Close modal');
    fireEvent.click(closeBtn);
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});
