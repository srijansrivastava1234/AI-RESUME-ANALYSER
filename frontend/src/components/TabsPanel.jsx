import React from 'react';
import { CheckCircle, AlertTriangle } from 'lucide-react';

export default function TabsPanel({ report, activeTab, setActiveTab }) {
  return (
    <div className="glass-panel" style={{ padding: '1.5rem' }}>
      <div className="dashboard-tabs">
        <button 
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab-btn ${activeTab === 'recommendations' ? 'active' : ''}`}
          onClick={() => setActiveTab('recommendations')}
        >
          Actionable Edits
        </button>
        <button 
          className={`tab-btn ${activeTab === 'keywords' ? 'active' : ''}`}
          onClick={() => setActiveTab('keywords')}
        >
          Keywords & Terms
        </button>
        <button 
          className={`tab-btn ${activeTab === 'sections' ? 'active' : ''}`}
          onClick={() => setActiveTab('sections')}
        >
          Section Auditing
        </button>
        <button 
          className={`tab-btn ${activeTab === 'templates' ? 'active' : ''}`}
          onClick={() => setActiveTab('templates')}
        >
          ATS Templates & Guide
        </button>
      </div>

      {/* Tab: Overview */}
      {activeTab === 'overview' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
            <h4 style={{ fontSize: '1.1rem', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <CheckCircle style={{ color: 'var(--success)', width: '20px', height: '20px' }} />
              <span>Key Strengths Detected</span>
            </h4>
            <div className="strengths-list">
              {report.key_strengths.map((str, index) => (
                <div key={index} className="strength-item">
                  <span className="strength-icon">✓</span>
                  <span>{str}</span>
                </div>
              ))}
            </div>
          </div>

          <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1.25rem' }}>
            <h4 style={{ fontSize: '1.1rem', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertTriangle style={{ color: 'var(--warning)', width: '20px', height: '20px' }} />
              <span>Top Priority Enhancements</span>
            </h4>
            <div className="recommendations-list">
              {report.actionable_recommendations.slice(0, 2).map((rec, index) => (
                <div key={index} className="rec-card" style={{ borderLeft: '3px solid var(--warning)' }}>
                  <div className="rec-top">
                    <span className="rec-title">{rec.issue}</span>
                    <span className="priority-badge high">{rec.priority}</span>
                  </div>
                  <p className="rec-desc">{rec.recommendation}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab: Recommendations */}
      {activeTab === 'recommendations' && (
        <div className="recommendations-list">
          <h4 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Improvement Action Plan</h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1rem' }}>
            Here is the side-by-side breakdown of the issues identified in your resume text, along with recommended bullet-point rephrasings:
          </p>
          
          {report.actionable_recommendations.map((rec, i) => (
            <div key={i} className="rec-card">
              <div className="rec-top">
                <span className="rec-title">{rec.issue}</span>
                <span className={`priority-badge ${rec.priority.toLowerCase()}`}>{rec.priority} Priority</span>
              </div>
              <p className="rec-desc" style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{rec.recommendation}</p>
              
              <div className="before-after-container">
                <div className="block-before">
                  <span className="block-label">Current Bullet</span>
                  <p>"{rec.before_after.before}"</p>
                </div>
                <div className="block-after">
                  <span className="block-label">Recommended Rewrite</span>
                  <p>"{rec.before_after.after}"</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab: Keywords */}
      {activeTab === 'keywords' && (
        <div className="keywords-panel">
          <div className="keyword-box">
            <h4 style={{ color: 'var(--success)' }}>
              <CheckCircle style={{ width: '18px', height: '18px' }} />
              <span>Detected Keywords ({report.keywords.detected.length})</span>
            </h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>These keywords are well matching and will trigger positive scores in ATS queries:</p>
            <div className="keyword-tags">
              {report.keywords.detected.map((tag, i) => (
                <span key={i} className="tag detected">{tag}</span>
              ))}
            </div>
          </div>

          <div className="keyword-box">
            <h4 style={{ color: 'var(--danger)' }}>
              <AlertTriangle style={{ width: '18px', height: '18px' }} />
              <span>Missing Keywords ({report.keywords.missing.length})</span>
            </h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>We recommend inserting these keywords organically into your experiences or skills section:</p>
            <div className="keyword-tags">
              {report.keywords.missing.map((tag, i) => (
                <span key={i} className="tag missing">{tag}</span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab: Sections */}
      {activeTab === 'sections' && (
        <div className="sections-layout">
          <h4 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Resume Section Integrity Check</h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1rem' }}>Individual ratings for the core building blocks of your resume:</p>
          
          {report.section_analysis.map((sec, i) => {
            const rating = sec.score >= 85 ? 'High' : sec.score >= 70 ? 'Moderate' : 'Critical';
            const badgeClass = sec.score >= 85 ? 'badge-success' : sec.score >= 70 ? 'badge-warning' : 'badge-danger';
            return (
              <div key={i} className="section-review-card">
                <div className="section-review-info">
                  <span className="section-review-title">{sec.section}</span>
                  <span className="section-review-desc">{sec.comments}</span>
                </div>
                <span className={`section-review-badge ${badgeClass}`}>{rating} ({sec.score}%)</span>
              </div>
            );
          })}
        </div>
      )}

      {/* Tab: Templates */}
      {activeTab === 'templates' && (
        <div className="templates-layout" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <h4 style={{ fontSize: '1.1rem', marginBottom: '0.25rem' }}>ATS-Compliant Resume Guidelines</h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            To bypass automatic filters, your resume layout should remain clean and use strong action verbs. Use the templates and resources below:
          </p>
          
          <div className="glass-panel" style={{ padding: '1.25rem', background: 'rgba(0,0,0,0.1)' }}>
            <span style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--primary)', display: 'block', marginBottom: '0.5rem' }}>Standard Chronological Template</span>
            <pre style={{ background: 'rgba(0,0,0,0.2)', padding: '0.75rem', borderRadius: '8px', fontSize: '0.75rem', color: 'var(--text-secondary)', overflowX: 'auto', fontFamily: 'monospace' }}>
{`# [YOUR NAME]
[Phone] | [Email] | [LinkedIn] | [GitHub]

## PROFESSIONAL SUMMARY
[2-3 sentences summarizing your experience, key skills, and impact.]

## TECHNICAL SKILLS
- Languages: [Python, JavaScript, SQL...]
- Frameworks & Libraries: [React, FastAPI, Docker...]

## WORK EXPERIENCE
**[Company Name]** - [Job Title] | [Start Date] – [End Date]
- [Action Verb] + [Project description] + resulting in [Quantified metric (e.g. +20% efficiency)].
- [Action Verb] + [Feature implemented] + using [Technologies] for [User base].

## PROJECTS
**[Project Title]** | [Technologies Used]
- Designed and built [system] which [impact/metric].`}
            </pre>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <span style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--accent)' }}>High-Impact Action Verbs</span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              <span className="tag detected" style={{ fontSize: '0.8rem' }}>Optimized</span>
              <span className="tag detected" style={{ fontSize: '0.8rem' }}>Streamlined</span>
              <span className="tag detected" style={{ fontSize: '0.8rem' }}>Engineered</span>
              <span className="tag detected" style={{ fontSize: '0.8rem' }}>Spearheaded</span>
              <span className="tag detected" style={{ fontSize: '0.8rem' }}>Architected</span>
              <span className="tag detected" style={{ fontSize: '0.8rem' }}>Implemented</span>
              <span className="tag detected" style={{ fontSize: '0.8rem' }}>Accelerated</span>
              <span className="tag detected" style={{ fontSize: '0.8rem' }}>Automated</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
