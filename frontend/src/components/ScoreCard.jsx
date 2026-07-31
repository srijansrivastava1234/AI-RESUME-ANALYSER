import React from 'react';
import { HelpCircle } from 'lucide-react';

export default function ScoreCard({
  atsScore,
  getScoreColor,
  getScoreBg,
  setShowHelpModal
}) {
  return (
    <div className="glass-panel score-card" style={{ position: 'relative' }}>
      <button 
        onClick={() => setShowHelpModal(true)} 
        className="no-print"
        style={{
          position: 'absolute',
          top: '1rem',
          right: '1rem',
          background: 'transparent',
          border: 'none',
          color: 'var(--text-muted)',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
        title="How is this calculated?"
      >
        <HelpCircle style={{ width: '18px', height: '18px' }} />
      </button>
      <div className="circular-progress">
        <svg className="svg-circle" width="150" height="150">
          <circle className="circle-bg" cx="75" cy="75" r="65" />
          <circle 
            className="circle-value" 
            cx="75" 
            cy="75" 
            r="65" 
            stroke={getScoreColor(atsScore)}
            strokeDasharray={2 * Math.PI * 65}
            strokeDashoffset={2 * Math.PI * 65 * (1 - atsScore / 100)}
          />
        </svg>
        <div className="score-text">
          <span className="score-num">{atsScore}</span>
          <span className="score-label">ATS Score</span>
        </div>
      </div>
      <div style={{ background: getScoreBg(atsScore), padding: '0.4rem 0.8rem', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 700, color: getScoreColor(atsScore) }}>
        {atsScore >= 85 ? 'Highly Competitive' : atsScore >= 70 ? 'Good Baseline' : 'Needs Optimization'}
      </div>
    </div>
  );
}
