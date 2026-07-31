import React from 'react';

export default function HelpModal({ showHelpModal, setShowHelpModal }) {
  if (!showHelpModal) return null;

  return (
    <div 
      className="modal-overlay no-print" 
      onClick={() => setShowHelpModal(false)}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.7)',
        backdropFilter: 'blur(8px)',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.5rem'
      }}
    >
      <div 
        className="glass-panel modal-content" 
        onClick={(e) => e.stopPropagation()}
        style={{
          maxWidth: '500px',
          width: '100%',
          padding: '2rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1.25rem',
          position: 'relative'
        }}
      >
        <h3 style={{ fontSize: '1.4rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>How is the ATS Score calculated?</h3>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
          The Applicant Tracking System (ATS) score evaluates your resume based on 4 primary criteria:
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', fontSize: '0.85rem' }}>
          <div>
            <strong style={{ color: 'var(--primary)' }}>Layout & Formatting (25%):</strong>
            <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Scans the visual structure, fonts, margins, and section dividers to ensure automated parser readability.</p>
          </div>
          <div>
            <strong style={{ color: 'var(--secondary)' }}>Grammar & Readability (25%):</strong>
            <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Analyzes spelling, grammar, readability index, sentence structures, and passive voice occurrences.</p>
          </div>
          <div>
            <strong style={{ color: 'var(--accent)' }}>Impact & Achievements (25%):</strong>
            <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Evaluates if bullet points describe achievements instead of duties. Looks for quantified results (e.g. percentages, metrics).</p>
          </div>
          <div>
            <strong style={{ color: 'var(--success)' }}>Skills & Keywords (25%):</strong>
            <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>Matches the technical and soft skills in your resume against industry standards and job description keywords.</p>
          </div>
        </div>
        <button 
          className="btn-primary" 
          onClick={() => setShowHelpModal(false)}
          style={{ marginTop: '0.5rem', padding: '0.65rem' }}
        >
          Close Guide
        </button>
      </div>
    </div>
  );
}
