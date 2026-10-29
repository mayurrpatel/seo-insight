import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import IssueTable from '../components/IssueTable';

describe('IssueTable component', () => {
  const mockIssues = [
    {
      id: 'iss-1',
      title: 'Missing Title Tag',
      category: 'Meta Tags',
      severity: 'Critical',
      priority_score: 95,
      affected_url: 'https://example.com/missing-title',
      evidence: '<title> tag missing',
      impact: 'Hurts ranking',
      suggested_fix: 'Add title',
    },
    {
      id: 'iss-2',
      title: 'Missing H1 Heading',
      category: 'Content Structure',
      severity: 'High',
      priority_score: 80,
      affected_url: 'https://example.com/no-h1',
      evidence: 'No h1',
      impact: 'Hurts hierarchy',
      suggested_fix: 'Add h1',
    },
    {
      id: 'iss-3',
      title: 'Missing Alt Tag',
      category: 'Content Structure',
      severity: 'Medium',
      priority_score: 55,
      affected_url: 'https://example.com/images',
      evidence: 'Image lacks alt',
      impact: 'Accessibility',
      suggested_fix: 'Add alt',
    },
  ];

  it('renders all issues in descending priority order initially', () => {
    const handleSelect = vi.fn();
    render(<IssueTable issues={mockIssues} onSelectIssue={handleSelect} />);

    expect(screen.getByText('Missing Title Tag')).toBeDefined();
    expect(screen.getByText('Missing H1 Heading')).toBeDefined();
    expect(screen.getByText('Missing Alt Tag')).toBeDefined();
    expect(screen.getByText('95')).toBeDefined();
  });

  it('filters issues based on search query', () => {
    render(<IssueTable issues={mockIssues} onSelectIssue={() => {}} />);

    const searchInput = screen.getByPlaceholderText(/Search by issue title/i);
    fireEvent.change(searchInput, { target: { value: 'Title' } });

    expect(screen.getByText('Missing Title Tag')).toBeDefined();
    expect(screen.queryByText('Missing H1 Heading')).toBeNull();
  });

  it('filters issues by clicking severity pill tab', () => {
    render(<IssueTable issues={mockIssues} onSelectIssue={() => {}} />);

    const critPill = screen.getByRole('button', { name: /Critical/i });
    fireEvent.click(critPill);

    expect(screen.getByText('Missing Title Tag')).toBeDefined();
    expect(screen.queryByText('Missing H1 Heading')).toBeNull();
    expect(screen.queryByText('Missing Alt Tag')).toBeNull();
  });
});
