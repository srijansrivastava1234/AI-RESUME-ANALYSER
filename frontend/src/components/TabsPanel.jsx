import React, { useState } from 'react';
import { CheckCircle, AlertTriangle, BookOpen, Clock, FileText, ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';

export default function TabsPanel({ report, extractedText, activeTab, setActiveTab }) {
  const [showRawText, setShowRawText] = useState(false);
  const [copiedKeyword, setCopiedKeyword] = useState(null);
  const [copiedAll, setCopiedAll] = useState(false);
  const [completedRecommendations, setCompletedRecommendations] = useState({});

  // Helper: word count
  const getWordCount = (text) => {
    if (!text) return 0;
    return text.trim().split(/\s+/).filter(Boolean).length;
  };

  const wordCount = getWordCount(extractedText);
  const readingTimeSec = Math.round((wordCount / 200) * 60); // 200 words per minute average reading speed
  
  // Word count health status
  const wordCountStatus = wordCount === 0 
    ? "No text analyzed" 
    : wordCount < 300 
    ? "Too short (add more detail)" 
    : wordCount > 900 
    ? "Too long (aim for 1-2 pages)" 
    : "Optimal (400-800 words)";

  const wordCountColor = wordCount >= 300 && wordCount <= 900 
    ? "var(--success)" 
    : "var(--warning)";

  // Keyword copy helpers
  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedKeyword(id);
    setTimeout(() => setCopiedKeyword(null), 1500);
  };

  const copyAllMissing = () => {
    if (report.keywords.missing && report.keywords.missing.length > 0) {
      navigator.clipboard.writeText(report.keywords.missing.join(', '));
      setCopiedAll(true);
      setTimeout(() => setCopiedAll(false), 2000);
    }
  };

  // Recommendations checklist handlers
  const toggleRecommendation = (index) => {
    setCompletedRecommendations(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const totalRecs = report.actionable_recommendations ? report.actionable_recommendations.length : 0;
  const completedCount = Object.values(completedRecommendations).filter(Boolean).length;
  const percentComplete = totalRecs > 0 ? Math.round((completedCount / totalRecs) * 100) : 0;

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
          
          {/* Readability & Content Stats */}
          {wordCount > 0 && (
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
              gap: '1rem',
              padding: '1rem',
              background: 'rgba(255,255,255,0.02)',
              border: '1px solid var(--border-color)',
              borderRadius: '12px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <FileText style={{ color: 'var(--primary)', width: '20px', height: '20px' }} />
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Resume Length</div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 700 }}>
                    {wordCount} words <span style={{ fontSize: '0.75rem', fontWeight: 600, color: wordCountColor }}>({wordCountStatus})</span>
                  </div>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Clock style={{ color: 'var(--accent)', width: '20px', height: '20px' }} />
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Full Read Time</div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 700 }}>
                    ~{Math.max(1, Math.round(readingTimeSec))} sec
                  </div>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <BookOpen style={{ color: 'var(--success)', width: '20px', height: '20px' }} />
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Recruiter Quick Scan</div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--success)' }}>
                    Passed (Standard format)
                  </div>
                </div>
              </div>
            </div>
          )}

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

          {/* Interactive Parsed Text Viewer accordion */}
          {extractedText && (
            <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1.25rem' }}>
              <button
                onClick={() => setShowRawText(!showRawText)}
                style={{
                  width: '100%',
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid var(--border-color)',
                  padding: '0.75rem 1rem',
                  borderRadius: '8px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  cursor: 'pointer',
                  color: 'white',
                  fontWeight: 600,
                  fontSize: '0.9rem'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <FileText style={{ width: '18px', height: '18px', color: 'var(--primary)' }} />
                  <span>View Extracted Text (What the ATS sees)</span>
                </div>
                {showRawText ? <ChevronUp style={{ width: '16px', height: '16px' }} /> : <ChevronDown style={{ width: '16px', height: '16px' }} />}
              </button>
              
              {showRawText && (
                <div style={{
                  marginTop: '0.5rem',
                  background: 'rgba(0,0,0,0.2)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  padding: '1rem',
                  maxHeight: '250px',
                  overflowY: 'auto',
                  fontFamily: 'monospace',
                  fontSize: '0.8rem',
                  lineHeight: '1.4',
                  whiteSpace: 'pre-wrap',
                  color: 'var(--text-secondary)'
                }}>
                  {extractedText}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Tab: Recommendations */}
      {activeTab === 'recommendations' && (
        <div className="recommendations-list">
          <h4 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Improvement Action Plan</h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1rem' }}>
            Check off recommendations as you implement them to track your improvements:
          </p>
          
          {/* Progress Bar */}
          {totalRecs > 0 && (
            <div style={{ marginBottom: '1.5rem', background: 'rgba(255,255,255,0.03)', padding: '1rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.5rem', fontWeight: 600 }}>
                <span>Resume Enhancement Progress</span>
                <span style={{ color: 'var(--success)' }}>{completedCount} of {totalRecs} edits ({percentComplete}%)</span>
              </div>
              <div style={{ height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${percentComplete}%`, height: '100%', background: 'linear-gradient(90deg, var(--primary), var(--success))', transition: 'width 0.3s ease' }}></div>
              </div>
            </div>
          )}

          {report.actionable_recommendations.map((rec, i) => {
            const isCompleted = completedRecommendations[i] || false;
            return (
              <div 
                key={i} 
                className="rec-card"
                style={{
                  opacity: isCompleted ? 0.6 : 1,
                  transition: 'opacity 0.2s ease',
                  borderLeft: isCompleted ? '3px solid var(--success)' : '3px solid var(--primary)'
                }}
              >
                <div className="rec-top">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <input 
                      type="checkbox"
                      checked={isCompleted}
                      onChange={() => toggleRecommendation(i)}
                      style={{
                        width: '16px',
                        height: '16px',
                        cursor: 'pointer',
                        accentColor: 'var(--success)'
                      }}
                    />
                    <span className="rec-title" style={{ textDecoration: isCompleted ? 'line-through' : 'none' }}>{rec.issue}</span>
                  </div>
                  <span className={`priority-badge ${rec.priority.toLowerCase()}`}>{rec.priority} Priority</span>
                </div>
                <p className="rec-desc" style={{ color: 'var(--text-primary)', fontWeight: 500, textDecoration: isCompleted ? 'line-through' : 'none' }}>{rec.recommendation}</p>
                
                <div className="before-after-container">
                  <div className="block-before">
                    <span className="block-label">Current Bullet</span>
                    <p style={{ textDecoration: isCompleted ? 'line-through' : 'none' }}>"{rec.before_after.before}"</p>
                  </div>
                  <div className="block-after">
                    <span className="block-label">Recommended Rewrite</span>
                    <p>"{rec.before_after.after}"</p>
                  </div>
                </div>
              </div>
            );
          })}
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
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>These keywords match requirements. Click tags to copy:</p>
            <div className="keyword-tags">
              {report.keywords.detected.map((tag, i) => (
                <span 
                  key={i} 
                  className="tag detected"
                  style={{ cursor: 'pointer', position: 'relative' }}
                  onClick={() => copyToClipboard(tag, `detected-${i}`)}
                  title="Click to copy"
                >
                  {copiedKeyword === `detected-${i}` ? 'Copied!' : tag}
                </span>
              ))}
            </div>
          </div>

          <div className="keyword-box">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <h4 style={{ color: 'var(--danger)', margin: 0, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                <AlertTriangle style={{ width: '18px', height: '18px' }} />
                <span>Missing Keywords ({report.keywords.missing.length})</span>
              </h4>
              {report.keywords.missing && report.keywords.missing.length > 0 && (
                <button
                  onClick={copyAllMissing}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.25rem',
                    padding: '0.3rem 0.6rem',
                    borderRadius: '6px',
                    fontSize: '0.75rem',
                    cursor: 'pointer',
                    background: 'rgba(255,255,255,0.05)',
                    border: '1px solid var(--border-color)',
                    color: 'white',
                    fontWeight: 600,
                    transition: 'var(--transition-smooth)'
                  }}
                  title="Copy all missing keywords separated by commas"
                >
                  {copiedAll ? <Check style={{ width: '12px', height: '12px' }} /> : <Copy style={{ width: '12px', height: '12px' }} />}
                  <span>{copiedAll ? 'Copied All!' : 'Copy All'}</span>
                </button>
              )}
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>We recommend inserting these keywords organically into your experiences. Click tags to copy:</p>
            <div className="keyword-tags">
              {report.keywords.missing.map((tag, i) => (
                <span 
                  key={i} 
                  className="tag missing"
                  style={{ cursor: 'pointer', position: 'relative' }}
                  onClick={() => copyToClipboard(tag, `missing-${i}`)}
                  title="Click to copy"
                >
                  {copiedKeyword === `missing-${i}` ? 'Copied!' : tag}
                </span>
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
