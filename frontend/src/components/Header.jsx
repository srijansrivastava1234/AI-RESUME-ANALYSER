import React from 'react';
import { FileCheck2, HelpCircle } from 'lucide-react';

export default function Header({ theme, setTheme, apiOnline, setShowHelpModal, appMode = 'audit', setAppMode }) {
  return (
    <header className="app-header">
      <div className="logo-section" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '8px',
          background: 'var(--primary)',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.3)'
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
        <div style={{
          display: 'flex',
          background: 'rgba(0, 0, 0, 0.3)',
          borderRadius: '8px',
          padding: '3px',
          border: '1px solid var(--border-color)',
          gap: '3px'
        }} className="no-print">
          <button
            onClick={() => setAppMode('audit')}
            style={{
              background: appMode === 'audit' ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              color: appMode === 'audit' ? '#ffffff' : 'var(--text-secondary)',
              border: appMode === 'audit' ? '1px solid rgba(255, 255, 255, 0.12)' : '1px solid transparent',
              borderRadius: '6px',
              padding: '0.35rem 0.85rem',
              fontSize: '0.78rem',
              fontWeight: appMode === 'audit' ? 600 : 500,
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            Single Audit
          </button>
          <button
            onClick={() => setAppMode('compare')}
            style={{
              background: appMode === 'compare' ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              color: appMode === 'compare' ? '#ffffff' : 'var(--text-secondary)',
              border: appMode === 'compare' ? '1px solid rgba(255, 255, 255, 0.12)' : '1px solid transparent',
              borderRadius: '6px',
              padding: '0.35rem 0.85rem',
              fontSize: '0.78rem',
              fontWeight: appMode === 'compare' ? 600 : 500,
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            Batch Compare
          </button>
          <button
            onClick={() => setAppMode('xyz')}
            style={{
              background: appMode === 'xyz' ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              color: appMode === 'xyz' ? '#ffffff' : 'var(--text-secondary)',
              border: appMode === 'xyz' ? '1px solid rgba(255, 255, 255, 0.12)' : '1px solid transparent',
              borderRadius: '6px',
              padding: '0.35rem 0.85rem',
              fontSize: '0.78rem',
              fontWeight: appMode === 'xyz' ? 600 : 500,
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            XYZ Impact Lab
          </button>
        </div>
      )}

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }} className="no-print">
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
            { id: 'violet', color: '#8b5cf6', name: 'Royal Purple' },
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
