import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ScoreCard from '../components/ScoreCard';

describe('ScoreCard Component', () => {
  const mockGetScoreColor = (score) => (score >= 80 ? '#10b981' : '#f59e0b');
  const mockGetScoreBg = (score) => (score >= 80 ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)');

  it('renders ATS score correctly', () => {
    render(
      <ScoreCard
        atsScore={92}
        getScoreColor={mockGetScoreColor}
        getScoreBg={mockGetScoreBg}
        setShowHelpModal={() => {}}
      />
    );

    expect(screen.getByText('92')).toBeInTheDocument();
    expect(screen.getByText('ATS Score')).toBeInTheDocument();
    expect(screen.getByText('Highly Competitive')).toBeInTheDocument();
  });

  it('renders intermediate score tier labels correctly', () => {
    const { rerender } = render(
      <ScoreCard
        atsScore={75}
        getScoreColor={mockGetScoreColor}
        getScoreBg={mockGetScoreBg}
        setShowHelpModal={() => {}}
      />
    );
    expect(screen.getByText('Good Baseline')).toBeInTheDocument();

    rerender(
      <ScoreCard
        atsScore={55}
        getScoreColor={mockGetScoreColor}
        getScoreBg={mockGetScoreBg}
        setShowHelpModal={() => {}}
      />
    );
    expect(screen.getByText('Needs Optimization')).toBeInTheDocument();
  });

  it('triggers help modal callback when question mark button is clicked', () => {
    const setShowHelpModal = vi.fn();
    render(
      <ScoreCard
        atsScore={88}
        getScoreColor={mockGetScoreColor}
        getScoreBg={mockGetScoreBg}
        setShowHelpModal={setShowHelpModal}
      />
    );

    const helpBtn = screen.getByTitle('How is this calculated?');
    fireEvent.click(helpBtn);
    expect(setShowHelpModal).toHaveBeenCalledWith(true);
  });
});
