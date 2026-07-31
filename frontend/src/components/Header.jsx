import React from 'react';
import { Sparkles } from 'lucide-react';

export default function Header({ theme, setTheme, apiOnline }) {
  return (
    <header className="app-header">
      <div className="logo-section">
        <Sparkles className="upload-icon" style={{ margin: 0, width: '28px', height: '28px' }} />
        <h1><span className="text-gradient">ATS Resume Analyser AI</span></h1>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }} className="no-print">
        <button
          onClick={() => setTheme(prev => prev === 'dark' ? 'light' : 'dark')}
          className="theme-toggle-btn"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
          style={{
            background: 'rgba(255, 255, 255, 0.03)',
            border: '1px solid var(--border-color)',
            borderRadius: '50%',
            width: '40px',
            height: '40px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-primary)',
            cursor: 'pointer',
            transition: 'var(--transition-smooth)'
          }}
        >
          {theme === 'dark' ? (
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
          )}
        </button>
        <div className="api-status">
          <div className={`status-dot ${apiOnline ? '' : 'offline'}`}></div>
          <span>API: {apiOnline ? 'Online' : 'Simulation Mode'}</span>
        </div>
      </div>
    </header>
  );
}
