import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import CoreParameters from '../components/CoreParameters';

describe('CoreParameters Component', () => {
  const mockMetrics = [
    { name: 'Formatting & Layout', score: 85, feedback: 'Clean single-column layout.' },
    { name: 'Content & Impact', score: 70, feedback: 'Include more measurable metrics.' },
    { name: 'Keyword Alignment', score: 90, feedback: 'Strong match against core domain.' },
  ];

  it('renders title and all metric parameters', () => {
    render(
      <CoreParameters
        metrics={mockMetrics}
        getScoreColor={() => '#10b981'}
      />
    );

    expect(screen.getByText('ATS Core Parameters')).toBeInTheDocument();
    expect(screen.getByText('Formatting & Layout')).toBeInTheDocument();
    expect(screen.getByText('85/100')).toBeInTheDocument();
    expect(screen.getByText('Clean single-column layout.')).toBeInTheDocument();

    expect(screen.getByText('Content & Impact')).toBeInTheDocument();
    expect(screen.getByText('70/100')).toBeInTheDocument();

    expect(screen.getByText('Keyword Alignment')).toBeInTheDocument();
    expect(screen.getByText('90/100')).toBeInTheDocument();
  });
});
