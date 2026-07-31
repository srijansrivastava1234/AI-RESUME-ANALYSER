import React from 'react';

export default function HistoryPanel({
  history,
  loadHistoryItem,
  clearHistory,
  getScoreColor,
  getScoreBg
}) {
  if (history.length === 0) return null;

  return (
    <div className="glass-panel no-print" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h4 style={{ fontSize: '1rem', fontWeight: 600 }}>Recent Scans</h4>
        <button 
          onClick={clearHistory} 
          style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.75rem', fontWeight: 600 }}
        >
          Clear All
        </button>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {history.map((item) => (
          <div 
            key={item.id}
            onClick={() => loadHistoryItem(item)}
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between', 
              padding: '0.75rem', 
              background: 'rgba(255,255,255,0.02)', 
              border: '1px solid var(--border-color)', 
              borderRadius: '8px', 
              cursor: 'pointer',
              transition: 'var(--transition-smooth)'
            }}
            className="history-item"
          >
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.1rem', maxWidth: '180px', overflow: 'hidden' }}>
              <span style={{ fontSize: '0.8rem', fontWeight: 600, textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>{item.filename}</span>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>{item.date}</span>
            </div>
            <span 
              style={{ 
                fontSize: '0.8rem', 
                fontWeight: 700, 
                color: getScoreColor(item.score),
                background: getScoreBg(item.score),
                padding: '0.2rem 0.5rem',
                borderRadius: '12px'
              }}
            >
              {item.score}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
