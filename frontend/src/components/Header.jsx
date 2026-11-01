import React from 'react';
import { FileCheck2, HelpCircle, FileText, Users, Zap } from 'lucide-react';

export default function Header({ theme, setTheme, apiOnline, setShowHelpModal, appMode = 'audit', setAppMode }) {
  const MODES = [
    { id: 'audit', label: 'Resume Audit', icon: FileText, title: 'Audit and optimize a single resume' },
    { id: 'compare', label: 'Compare Resumes', icon: Users, title: 'Compare multiple candidates or resume versions side-by-side' },
    { id: 'xyz', label: 'Bullet Optimizer', icon: Zap, title: "Optimize bullet points using Google's XYZ impact formula" }
  ];

  const handleNavKeyDown = (e) => {
    if (!setAppMode) return;
    const currentIndex = MODES.findIndex(m => m.id === appMode);
    if (currentIndex === -1) return;

    if (e.key === 'ArrowRight') {
      e.preventDefault();
      const nextIndex = (currentIndex + 1) % MODES.length;
      setAppMode(MODES[nextIndex].id);
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      const prevIndex = (currentIndex - 1 + MODES.length) % MODES.length;
      setAppMode(MODES[prevIndex].id);
    } else if (e.key === 'Home') {
      e.preventDefault();
      setAppMode(MODES[0].id);
    } else if (e.key === 'End') {
      e.preventDefault();
      setAppMode(MODES[MODES.length - 1].id);
    }
  };

  return (
    <header className="app-header">
      <div className="header-left logo-section" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{
          width: '34px',
          height: '34px',
          borderRadius: '9px',
          background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
          border: '1px solid rgba(255, 255, 255, 0.25)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 2px 8px rgba(37, 99, 235, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.3)'
        }}>
          <FileCheck2 style={{ width: '18px', height: '18px', color: '#ffffff' }} />
        </div>
        <h1><span className="text-gradient">ATS Resume Analyser AI</span></h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span style={{
            fontSize: '0.68rem',
            padding: '2px 8px',
            borderRadius: '6px',
            background: 'rgba(255, 255, 255, 0.05)',
            color: 'var(--text-secondary)',
            fontWeight: 600,
            fontFamily: 'var(--font-mono)',
            border: '1px solid var(--border-color)',
            letterSpacing: '-0.01em'
          }}>v1.9.0</span>
          <span style={{
            fontSize: '0.68rem',
            padding: '2px 8px',
            borderRadius: '6px',
            background: 'rgba(16, 185, 129, 0.08)',
            color: '#34d399',
            fontWeight: 600,
            fontFamily: 'var(--font-mono)',
            border: '1px solid rgba(16, 185, 129, 0.25)',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '5px',
            letterSpacing: '-0.01em'
          }}>
            <span style={{ width: '5px', height: '5px', borderRadius: '50%', background: '#10b981' }} />
            Spam Shield Active
          </span>
        </div>
      </div>

      {setAppMode && (
        <div className="header-center no-print">
          <nav 
            className="app-mode-nav" 
            role="tablist" 
            aria-label="Workspace Modes"
            onKeyDown={handleNavKeyDown}
          >
            {MODES.map(mode => {
              const Icon = mode.icon;
              const isActive = appMode === mode.id;
              return (
                <button
                  key={mode.id}
                  role="tab"
                  tabIndex={isActive ? 0 : -1}
                  aria-selected={isActive}
                  onClick={() => setAppMode(mode.id)}
                  className={`mode-nav-btn ${isActive ? 'active' : ''}`}
                  title={mode.title}
                >
                  <Icon className="mode-icon" />
                  <span>{mode.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      )}

      <div className="header-right no-print" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <button
          onClick={() => setShowHelpModal(true)}
          style={{
            background: 'rgba(255, 255, 255, 0.04)',
            border: '1px solid var(--border-color)',
            borderRadius: '6px',
            color: 'var(--text-secondary)',
            padding: '0.35rem 0.75rem',
            fontSize: '0.78rem',
            cursor: 'pointer',
            fontWeight: 500,
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem',
            transition: 'all 0.15s ease'
          }}
          className="btn-help-guide"
          title="How ATS Score is calculated"
        >
          <HelpCircle style={{ width: '14px', height: '14px' }} />
          <span>Help Guide</span>
        </button>
        <div className="theme-selector" style={{ display: 'flex', gap: '0.35rem', background: 'rgba(0, 0, 0, 0.25)', border: '1px solid var(--border-color)', padding: '0.25rem 0.45rem', borderRadius: '8px' }}>
          {[
            { id: 'dark', color: '#2563eb', name: 'Dark Slate' },
            { id: 'light', color: '#e2e8f0', name: 'Light Mode', isLight: true },
            { id: 'emerald', color: '#10b981', name: 'Emerald Green' },
            { id: 'violet', color: '#475569', name: 'Steel Slate' },
            { id: 'amber', color: '#f59e0b', name: 'Amber Gold' }
          ].map(t => (
            <button
              key={t.id}
              onClick={() => setTheme(t.id)}
              title={t.name}
              style={{
                width: '16px',
                height: '16px',
                borderRadius: '50%',
                background: t.isLight ? '#ffffff' : t.color,
                border: theme === t.id ? '2px solid white' : '1px solid rgba(255,255,255,0.2)',
                cursor: 'pointer',
                padding: 0,
                transform: theme === t.id ? 'scale(1.15)' : 'scale(1)',
                transition: 'all 0.15s ease'
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
