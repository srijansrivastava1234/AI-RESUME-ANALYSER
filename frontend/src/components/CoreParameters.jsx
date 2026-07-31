import React from 'react';

export default function CoreParameters({ metrics, getScoreColor }) {
  return (
    <div className="glass-panel category-card">
      <h4 style={{ fontSize: '1.05rem', fontWeight: 600 }}>ATS Core Parameters</h4>
      
      {metrics.map((metric, i) => (
        <div key={i} className="category-row">
          <div className="category-header">
            <span className="category-name">{metric.name}</span>
            <span className="category-val" style={{ color: getScoreColor(metric.score) }}>{metric.score}/100</span>
          </div>
          <div className="progress-bar-bg">
            <div 
              className="progress-bar-fill" 
              style={{ 
                width: `${metric.score}%`, 
                backgroundColor: getScoreColor(metric.score) 
              }}
            />
          </div>
          <p className="category-feedback">{metric.feedback}</p>
        </div>
      ))}
    </div>
  );
}
