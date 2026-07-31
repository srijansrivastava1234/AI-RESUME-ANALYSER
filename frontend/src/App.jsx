import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  UploadCloud, 
  Sparkles, 
  CheckCircle, 
  AlertTriangle, 
  ArrowRight, 
  BookOpen, 
  Target, 
  HelpCircle,
  Briefcase,
  Layers,
  Code,
  Printer
} from 'lucide-react';

const BACKEND_URL = 'http://127.0.0.1:8000';

function App() {
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [jobDesc, setJobDesc] = useState('');
  const [loading, setLoading] = useState(false);
  const [apiOnline, setApiOnline] = useState(false);
  const [report, setReport] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [error, setError] = useState('');
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'dark';
  });
  const [showHelpModal, setShowHelpModal] = useState(false);

  // Apply theme class to body and sync with localStorage
  useEffect(() => {
    document.body.className = theme === 'light' ? 'light-theme' : '';
    localStorage.setItem('theme', theme);
  }, [theme]);

  const [history, setHistory] = useState([]);

  // Load history on mount
  useEffect(() => {
    try {
      const savedHistory = JSON.parse(localStorage.getItem('resume_history') || '[]');
      setHistory(savedHistory);
    } catch (e) {
      console.error(e);
    }
  }, []);

  const saveToHistory = (filename, score, reportData) => {
    try {
      const historyItem = {
        id: Date.now().toString(),
        filename,
        score,
        date: new Date().toLocaleDateString(undefined, { 
          month: 'short', 
          day: 'numeric', 
          hour: '2-digit', 
          minute: '2-digit' 
        }),
        report: reportData
      };
      
      const currentHistory = JSON.parse(localStorage.getItem('resume_history') || '[]');
      const updatedHistory = [historyItem, ...currentHistory].slice(0, 5);
      localStorage.setItem('resume_history', JSON.stringify(updatedHistory));
      setHistory(updatedHistory);
    } catch (e) {
      console.error("Error saving history:", e);
    }
  };

  const loadHistoryItem = (item) => {
    setReport(item.report);
    setActiveTab('overview');
  };

  const clearHistory = () => {
    localStorage.removeItem('resume_history');
    setHistory([]);
  };

  // Check API health status on mount
  useEffect(() => {
    fetch(`${BACKEND_URL}/`)
      .then(res => {
        if (res.ok) setApiOnline(true);
      })
      .catch(() => {
        setApiOnline(false);
      });
  }, []);

  // Handle Drag & Drop
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === "application/pdf") {
        setFile(droppedFile);
        setError('');
      } else {
        setError('Only PDF files are supported.');
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === "application/pdf") {
        setFile(selectedFile);
        setError('');
      } else {
        setError('Only PDF files are supported.');
      }
    }
  };

  const removeFile = () => {
    setFile(null);
    setReport(null);
  };

  // Submit to API
  const analyzeResume = async () => {
    if (!file) {
      setError('Please upload a resume first.');
      return;
    }

    setLoading(true);
    setError('');
    
    const formData = new FormData();
    formData.append('file', file);
    if (jobDesc.trim()) {
      formData.append('job_description', jobDesc);
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to analyze resume.');
      }

      const data = await response.json();
      setReport(data.report);
      setActiveTab('overview');
      saveToHistory(file.name, data.report.ats_score, data.report);
    } catch (err) {
      setError(err.message || 'An error occurred during analysis.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Score styling helpers
  const getScoreColor = (score) => {
    if (score >= 85) return 'var(--success)';
    if (score >= 70) return 'var(--warning)';
    return 'var(--danger)';
  };

  const getScoreBg = (score) => {
    if (score >= 85) return 'var(--success-bg)';
    if (score >= 70) return 'var(--warning-bg)';
    return 'var(--danger-bg)';
  };

  return (
    <div className="app-container">
      {/* Header */}
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
              justify-content: 'center',
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

      {/* Grid */}
      <div className="grid-container">
        {/* Sidebar Inputs */}
        <div className="input-sidebar">
          <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Upload Resume</h3>
            
            {!file ? (
              <div 
                className={`dropzone-container ${dragActive ? 'active' : ''}`}
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                onClick={() => document.getElementById('file-upload').click()}
              >
                <UploadCloud className="upload-icon" style={{ width: '40px', height: '40px', margin: '0 auto 0.75rem' }} />
                <p style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.25rem' }}>Drag & drop your resume</p>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>PDF formats only (max. 10MB)</p>
                <input 
                  id="file-upload" 
                  type="file" 
                  accept=".pdf" 
                  onChange={handleFileChange} 
                  style={{ display: 'none' }} 
                />
              </div>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', borderRadius: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <FileText style={{ color: 'var(--primary)' }} />
                  <div style={{ maxWidth: '180px', overflow: 'hidden' }}>
                    <p style={{ fontSize: '0.9rem', fontWeight: 600, textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>{file.name}</p>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                </div>
                <button onClick={removeFile} style={{ background: 'transparent', border: 'none', color: 'var(--danger)', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600 }}>Remove</button>
              </div>
            )}

            {error && (
              <div style={{ padding: '0.75rem', background: 'var(--danger-bg)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '8px', color: 'var(--danger)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <AlertTriangle style={{ width: '16px', height: '16px', flexShrink: 0 }} />
                <span>{error}</span>
              </div>
            )}
          </div>

          <div className="glass-panel job-desc-input">
            <label htmlFor="job-desc">Target Job Description (Optional)</label>
            <textarea 
              id="job-desc" 
              placeholder="Paste the target job description here to check your compatibility, skills alignment, and discover specific keywords gaps..." 
              value={jobDesc}
              onChange={(e) => setJobDesc(e.target.value)}
            />
            <button 
              className="btn-primary" 
              onClick={analyzeResume} 
              disabled={loading || !file}
            >
              {loading ? (
                <>Analyzing...</>
              ) : (
                <>
                  <span>Analyze ATS Match</span>
                  <ArrowRight style={{ width: '18px', height: '18px' }} />
                </>
              )}
            </button>
          </div>

          {history.length > 0 && (
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
                      justify-content: 'space-between', 
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
          )}
        </div>

        {/* Dashboard Main */}
        <div className="dashboard-main">
          {loading && (
            <div className="glass-panel loading-container">
              <div className="spinner"></div>
              <div style={{ textAlign: 'center' }}>
                <h4 style={{ fontSize: '1.2rem', marginBottom: '0.25rem' }}>Evaluating Resume Structure</h4>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Extracting text, evaluating formatting, and matching requirements using Gemini AI...</p>
              </div>
            </div>
          )}

          {!loading && !report && (
            <div className="glass-panel welcome-placeholder">
              <FileText className="placeholder-icon" style={{ width: '64px', height: '64px' }} />
              <div className="placeholder-text">
                <h3>Ready to Audit Your Resume?</h3>
                <p>Upload your resume in PDF format, enter an optional target job description, and hit 'Analyze' to run a deep scanner on your resume's ATS compliance score.</p>
              </div>
            </div>
          )}

          {!loading && report && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }} className="no-print">
                <button 
                  onClick={() => window.print()} 
                  className="btn-print"
                  style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '0.5rem', 
                    padding: '0.5rem 1rem', 
                    background: 'rgba(255,255,255,0.05)', 
                    border: '1px solid var(--border-color)', 
                    borderRadius: '8px', 
                    color: 'white', 
                    cursor: 'pointer', 
                    fontFamily: 'var(--font-header)', 
                    fontWeight: 600, 
                    fontSize: '0.85rem',
                    transition: 'var(--transition-smooth)'
                  }}
                >
                  <Printer style={{ width: '16px', height: '16px' }} />
                  <span>Export Report / Print PDF</span>
                </button>
              </div>
              {/* Job description score header */}
              {report.job_compatibility && (
                <div className="compatibility-box">
                  <div className="compatibility-header">
                    <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.15rem' }}>
                      <Target style={{ color: 'var(--accent)' }} />
                      <span>Job Description Compatibility</span>
                    </h3>
                    <div className="compat-score-wrap">
                      <span className="compat-score-num">{report.job_compatibility.score}%</span>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Match</span>
                    </div>
                  </div>
                  <p className="compat-desc">{report.job_compatibility.match_analysis}</p>
                  
                  {report.job_compatibility.skill_gaps && report.job_compatibility.skill_gaps.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.5rem', marginTop: '0.25rem' }}>
                      <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Key Skill Gaps:</span>
                      {report.job_compatibility.skill_gaps.map((gap, index) => (
                        <span key={index} className="tag missing" style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}>{gap}</span>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Main Scores Row */}
              <div className="dashboard-grid">
                {/* Score Dial */}
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
                      justify-content: 'center'
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
                        stroke={getScoreColor(report.ats_score)}
                        strokeDasharray={2 * Math.PI * 65}
                        strokeDashoffset={2 * Math.PI * 65 * (1 - report.ats_score / 100)}
                      />
                    </svg>
                    <div className="score-text">
                      <span className="score-num">{report.ats_score}</span>
                      <span className="score-label">ATS Score</span>
                    </div>
                  </div>
                  <div style={{ background: getScoreBg(report.ats_score), padding: '0.4rem 0.8rem', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 700, color: getScoreColor(report.ats_score) }}>
                    {report.ats_score >= 85 ? 'Highly Competitive' : report.ats_score >= 70 ? 'Good Baseline' : 'Needs Optimization'}
                  </div>
                </div>

                {/* Score breakdown metrics */}
                <div className="glass-panel category-card">
                  <h4 style={{ fontSize: '1.05rem', fontWeight: 600 }}>ATS Core Parameters</h4>
                  
                  {report.metrics.map((metric, i) => (
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
              </div>

              {/* Tab Navigation */}
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
              </div>
            </div>
          )}
        </div>
      </div>
    </div>

      {showHelpModal && (
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
            justify-content: 'center',
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
      )}
    </div>
  );
}

export default App;
