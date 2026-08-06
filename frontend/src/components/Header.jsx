import React from 'react';
import { Sparkles, HelpCircle } from 'lucide-react';

export default function Header({ theme, setTheme, apiOnline, setShowHelpModal }) {
  return (
    <header className="app-header">
      <div className="logo-section">
        <Sparkles className="upload-icon" style={{ margin: 0, width: '28px', height: '28px' }} />
        <h1><span className="text-gradient">ATS Resume Analyser AI</span></h1>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }} className="no-print">
        <button
          onClick={() => setShowHelpModal(true)}
          style={{
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid var(--border-color)',
            borderRadius: '20px',
            color: 'white',
            padding: '0.3rem 0.75rem',
            fontSize: '0.75rem',
            cursor: 'pointer',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem',
            transition: 'all 0.2s ease'
          }}
          className="btn-help-guide"
          title="How ATS Score is calculated"
        >
          <HelpCircle style={{ width: '14px', height: '14px' }} />
          <span>Help Guide</span>
        </button>
        <div className="theme-selector" style={{ display: 'flex', gap: '0.4rem', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-color)', padding: '0.3rem 0.5rem', borderRadius: '20px' }}>
          {[
            { id: 'dark', color: '#6366f1', name: 'Dark Indigo' },
            { id: 'light', color: '#4f46e5', name: 'Light Mode', isLight: true },
            { id: 'emerald', color: '#10b981', name: 'Emerald Green' },
            { id: 'violet', color: '#8b5cf6', name: 'Royal Purple' },
            { id: 'amber', color: '#f59e0b', name: 'Amber Gold' }
          ].map(t => (
            <button
              key={t.id}
              onClick={() => setTheme(t.id)}
              title={t.name}
              style={{
                width: '18px',
                height: '18px',
                borderRadius: '50%',
                background: t.isLight ? '#ffffff' : t.color,
                border: theme === t.id ? '2px solid white' : '1px solid rgba(255,255,255,0.2)',
                cursor: 'pointer',
                padding: 0,
                transform: theme === t.id ? 'scale(1.15)' : 'scale(1)',
                transition: 'all 0.2s ease',
                boxShadow: theme === t.id ? `0 0 8px ${t.color}` : 'none'
              }}
            />
          ))}
        </div>
        <div className="api-status">
          <div className={`status-dot ${apiOnline ? '' : 'offline'}`}></div>
          <span>API: {apiOnline ? 'Online' : 'Simulation Mode'}</span>
        </div>
      </div>
    </header>
  );
}
