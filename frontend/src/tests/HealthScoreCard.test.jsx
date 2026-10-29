import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import HealthScoreCard from '../components/HealthScoreCard';

describe('HealthScoreCard component', () => {
  it('renders health score number, rating, and toggleable formula', () => {
    const mockHealth = {
      score: 85,
      rating: 'Good',
      calculation_formula: 'Score = 100 - (Normalized Penalty / Pages^0.65).',
    };

    render(<HealthScoreCard healthScore={mockHealth} pagesScanned={10} />);

    expect(screen.getByText('85')).toBeDefined();
    expect(screen.getByText('Good')).toBeDefined();

    // Click formula trigger button
    const formulaBtn = screen.getByRole('button', { name: /How is this calculated/i });
    expect(formulaBtn).toBeDefined();
    fireEvent.click(formulaBtn);

    expect(screen.getByText(/Normalized Penalty/)).toBeDefined();
  });

  it('renders fallback for zero or missing values gracefully', () => {
    render(<HealthScoreCard healthScore={null} pagesScanned={0} />);
    expect(screen.getByText('0')).toBeDefined();
    expect(screen.getByText('N/A')).toBeDefined();
  });
});
