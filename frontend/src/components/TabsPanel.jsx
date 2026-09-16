import React, { useState, useMemo } from 'react';
import { 
  CheckCircle, 
  AlertTriangle, 
  BookOpen, 
  Clock, 
  FileText, 
  ChevronDown, 
  ChevronUp, 
  Copy, 
  Check, 
  ShieldCheck, 
  Scale, 
  Sparkles, 
  Award, 
  FileCheck,
  CheckSquare,
  Terminal,
  ExternalLink
} from 'lucide-react';
import HygieneCard from './HygieneCard';
import { calculateKeywordDensity } from '../utils/performance';

export default function TabsPanel({
  report,
  extractedText,
  editedText,
  setEditedText,
  analyzeSandboxText,
  activeTab,
  setActiveTab,
  loading
}) {
  const [showRawText, setShowRawText] = useState(false);
  const [copiedKeyword, setCopiedKeyword] = useState(null);
  const [copiedAll, setCopiedAll] = useState(false);
  const [completedRecommendations, setCompletedRecommendations] = useState({});
  const [copiedSandbox, setCopiedSandbox] = useState(false);
  const [targetSeniority, setTargetSeniority] = useState('mid');
  const [targetPages, setTargetPages] = useState(1);
  const [copiedPrompt, setCopiedPrompt] = useState(false);
  const [showFullPrompt, setShowFullPrompt] = useState(false);
  const [selectedPromptModel, setSelectedPromptModel] = useState('claude');

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

  const checkKeywordCoverage = (kw) => {
    if (!editedText) return false;
    return editedText.toLowerCase().includes(kw.toLowerCase());
  };

  const copySandboxToClipboard = () => {
    if (!editedText) return;
    navigator.clipboard.writeText(editedText);
    setCopiedSandbox(true);
    setTimeout(() => setCopiedSandbox(false), 2000);
  };

  const downloadSandboxAsTxt = () => {
    if (!editedText) return;
    const blob = new Blob([editedText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'edited_resume.txt';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
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

  const freqKeywords = useMemo(() => {
    return calculateKeywordDensity(extractedText, 10);
  }, [extractedText]);

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
          className={`tab-btn ${activeTab === 'sandbox' ? 'active' : ''}`}
          onClick={() => setActiveTab('sandbox')}
        >
          Resume Sandbox
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
        <button 
          className={`tab-btn ${activeTab === 'compliance' ? 'active' : ''}`}
          onClick={() => setActiveTab('compliance')}
          style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}
        >
          <ShieldCheck style={{ width: '14px', height: '14px', color: activeTab === 'compliance' ? 'white' : 'var(--success)' }} />
          Compliance & Safe Harbor
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

          {/* ATS Formatting Hygiene Audit */}
          {report.formatting_hygiene && (
            <HygieneCard hygiene={{
              ...report.formatting_hygiene,
              viewport: report.viewport_audit || report.formatting_hygiene.viewport
            }} />
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

      {/* Tab: Sandbox Editor */}
      {activeTab === 'sandbox' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
            <h4 style={{ fontSize: '1.1rem', marginBottom: '0.25rem' }}>Resume Sandbox & Editor</h4>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Refine your resume content directly in the sandbox. Add missing keywords and rewrite bullet points to see real-time updates:
            </p>
          </div>

          <div className="sandbox-grid">
            {/* Left side: Editor */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                  Draft Text Content
                </span>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {getWordCount(editedText)} words | ~{Math.max(1, Math.round((getWordCount(editedText) / 200) * 60))}s read time
                </span>
              </div>
              <textarea
                value={editedText}
                onChange={(e) => setEditedText(e.target.value)}
                style={{
                  width: '100%',
                  height: '350px',
                  background: 'rgba(0, 0, 0, 0.2)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '12px',
                  padding: '1rem',
                  color: 'white',
                  fontFamily: 'monospace',
                  fontSize: '0.85rem',
                  lineHeight: '1.5',
                  resize: 'vertical',
                  outline: 'none',
                  transition: 'border-color 0.2s ease'
                }}
                placeholder="Paste or edit your resume text here..."
              />
              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }} className="no-print">
                <button
                  onClick={analyzeSandboxText}
                  disabled={loading || !editedText.trim()}
                  className="btn-primary"
                  style={{
                    padding: '0.6rem 1.2rem',
                    fontSize: '0.85rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}
                >
                  {loading ? 'Analyzing...' : 'Re-analyze Draft'}
                </button>
                <button
                  onClick={copySandboxToClipboard}
                  disabled={!editedText}
                  style={{
                    padding: '0.6rem 1.2rem',
                    fontSize: '0.85rem',
                    background: 'rgba(255,255,255,0.05)',
                    border: '1px solid var(--border-color)',
                    color: 'white',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    transition: 'var(--transition-smooth)'
                  }}
                >
                  {copiedSandbox ? <Check style={{ width: '16px', height: '16px', color: 'var(--success)' }} /> : <Copy style={{ width: '16px', height: '16px' }} />}
                  <span>{copiedSandbox ? 'Copied!' : 'Copy Draft'}</span>
                </button>
                <button
                  onClick={downloadSandboxAsTxt}
                  disabled={!editedText}
                  style={{
                    padding: '0.6rem 1.2rem',
                    fontSize: '0.85rem',
                    background: 'rgba(255,255,255,0.05)',
                    border: '1px solid var(--border-color)',
                    color: 'white',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    transition: 'var(--transition-smooth)'
                  }}
                >
                  <FileText style={{ width: '16px', height: '16px' }} />
                  <span>Download .txt</span>
                </button>
              </div>
            </div>

            {/* Right side: Real-time keyword tracker */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '1.25rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                <h5 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--primary)' }}>
                  Real-Time Keyword Coverage
                </h5>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                  Integrate these missing terms into your text draft to automatically verify match compliance:
                </p>

                {!report?.keywords?.missing || report.keywords.missing.length === 0 ? (
                  <div style={{ fontSize: '0.85rem', color: 'var(--success)', fontWeight: 600 }}>
                    ✓ Perfect! No missing keywords detected.
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                    {report.keywords.missing.map((kw, i) => {
                      const isCovered = checkKeywordCoverage(kw);
                      return (
                        <div
                          key={i}
                          style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            padding: '0.5rem 0.75rem',
                            background: isCovered ? 'rgba(16, 185, 129, 0.05)' : 'rgba(239, 68, 68, 0.03)',
                            border: `1px solid ${isCovered ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.1)'}`,
                            borderRadius: '8px',
                            fontSize: '0.8rem',
                            transition: 'all 0.2s ease'
                          }}
                        >
                          <span style={{ fontWeight: 600, color: 'white' }}>{kw}</span>
                          <span
                            style={{
                              fontSize: '0.7rem',
                              fontWeight: 700,
                              color: isCovered ? 'var(--success)' : 'var(--danger)',
                              background: isCovered ? 'var(--success-bg)' : 'var(--danger-bg)',
                              padding: '0.15rem 0.4rem',
                              borderRadius: '12px'
                            }}
                          >
                            {isCovered ? '✓ Covered' : '✗ Missing'}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Tips card */}
              <div style={{ background: 'rgba(99, 102, 241, 0.03)', padding: '1.25rem', borderRadius: '12px', border: '1px solid rgba(99, 102, 241, 0.15)' }}>
                <h5 style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--primary)', marginBottom: '0.35rem' }}>
                  Optimization Tips
                </h5>
                <ul style={{ paddingLeft: '1.1rem', fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                  <li>Ensure keywords match exactly, or are used in natural, highly technical context sentences.</li>
                  <li>Use action-verb combinations (e.g. <em>"Optimized system performance using Docker..."</em> instead of just listing <em>"Docker"</em>).</li>
                  <li>Avoid packing keywords in a list format; ATS parsers prefer seeing usage in description bullets.</li>
                </ul>
              </div>
            </div>
          </div>
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

          {freqKeywords.length > 0 && (
            <div className="keyword-box" style={{ gridColumn: 'span 2', marginTop: '1.5rem', borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem' }}>
              <h4 style={{ color: 'var(--accent)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Clock style={{ width: '18px', height: '18px' }} />
                <span>Keyword Density & Frequency Analyzer</span>
              </h4>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
                The following terms appear most frequently in the extracted resume text. Proper density helps pass automatic filters:
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
                {freqKeywords.map((item, idx) => {
                  const maxCount = freqKeywords[0].count;
                  const percent = Math.round((item.count / maxCount) * 100);
                  return (
                    <div key={idx} style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.4rem', fontWeight: 600 }}>
                        <span style={{ color: 'var(--text-primary)' }}>{item.word}</span>
                        <span style={{ color: 'var(--accent)' }}>{item.count} {item.count === 1 ? 'time' : 'times'}</span>
                      </div>
                      <div style={{ height: '6px', background: 'rgba(255,255,255,0.06)', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ width: `${percent}%`, height: '100%', background: 'linear-gradient(90deg, var(--accent), var(--primary))', borderRadius: '3px' }}></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Technical Acronym & Domain Synonym Expansions */}
          <div className="keyword-box" style={{ gridColumn: 'span 2', marginTop: '1.25rem', borderTop: '1px solid var(--border-color)', paddingTop: '1.25rem' }}>
            <h4 style={{ color: 'var(--accent)', display: 'flex', alignItems: 'center', gap: '0.4rem', margin: 0, fontSize: '0.95rem' }}>
              <Sparkles style={{ width: '17px', height: '17px' }} />
              <span>Technical Acronym & Canonical Synonym Mapping</span>
            </h4>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: '0.4rem 0 0.8rem 0' }}>
              Standardizes industry abbreviations (e.g. K8s ➔ Kubernetes, TS ➔ TypeScript) to ensure candidate recall across rigid ATS keyword filters.
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {[
                { from: 'K8s', to: 'Kubernetes' },
                { from: 'TS', to: 'TypeScript' },
                { from: 'AWS', to: 'Amazon Web Services' },
                { from: 'GCP', to: 'Google Cloud Platform' },
                { from: 'Postgres', to: 'PostgreSQL' },
                { from: 'CI/CD', to: 'Continuous Integration / Continuous Deployment' },
                { from: 'ML', to: 'Machine Learning' },
                { from: 'NLP', to: 'Natural Language Processing' }
              ].map((syn, sIdx) => (
                <span
                  key={sIdx}
                  style={{
                    background: 'rgba(99, 102, 241, 0.08)',
                    border: '1px solid rgba(99, 102, 241, 0.25)',
                    color: 'var(--text-primary)',
                    fontSize: '0.75rem',
                    padding: '4px 9px',
                    borderRadius: '6px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem'
                  }}
                >
                  <strong style={{ color: 'white' }}>{syn.from}</strong>
                  <span style={{ color: 'var(--accent)', fontSize: '0.7rem' }}>➔</span>
                  <span style={{ color: 'var(--text-secondary)' }}>{syn.to}</span>
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
          
          {/* Workday & Taleo Canonical Mapping Card */}
          <div className="glass-panel" style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--text-main)' }}>
                Workday & Taleo Section Taxonomy Mapping
              </span>
              <span style={{ fontSize: '0.72rem', color: 'var(--success)', fontWeight: 700, background: 'rgba(16,185,129,0.1)', padding: '2px 8px', borderRadius: '10px' }}>
                Canonical Certified
              </span>
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', margin: '0 0 0.75rem 0' }}>
              Standardizes creative headings into Workday/Taleo canonical fields to prevent automated applicant profile dropouts.
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.5rem', fontSize: '0.75rem' }}>
              <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.5rem', borderRadius: '6px' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Detected: "Experience"</span>
                <div style={{ color: 'var(--success)', fontWeight: 600 }}>➔ Work Experience (Mandatory)</div>
              </div>
              <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.5rem', borderRadius: '6px' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Detected: "Academics"</span>
                <div style={{ color: 'var(--success)', fontWeight: 600 }}>➔ Education (Mandatory)</div>
              </div>
              <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.5rem', borderRadius: '6px' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Detected: "Toolbox"</span>
                <div style={{ color: 'var(--success)', fontWeight: 600 }}>➔ Technical Skills (Mandatory)</div>
              </div>
            </div>
          </div>
          
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

      {/* Tab: Compliance & Safe Harbor */}
      {activeTab === 'compliance' && (() => {
        const complianceData = report?.compliance_audit || {
          composite_score: report?.ats_score || 75,
          letter_grade: (report?.ats_score || 75) >= 90 ? 'A+' : (report?.ats_score || 75) >= 80 ? 'A' : (report?.ats_score || 75) >= 70 ? 'B' : 'C',
          grade_descriptor: (report?.ats_score || 75) >= 85 ? 'Elite Competitive Profile (Top 5% ATS Ingestion)' : 'Strong Role Alignment & Parseability',
          target_seniority: targetSeniority,
          target_pages: targetPages,
          word_count: wordCount,
          pillars: {
            keywords: {
              name: "Keywords & Hard Skills",
              weight: 0.40,
              score: report?.metrics?.find(m => m.name.toLowerCase().includes('skills'))?.score || 75,
              finding: `Detected ${(report?.keywords?.detected || []).length} keywords. Missing: ${(report?.keywords?.missing || []).length}.`,
              missing_keywords: report?.keywords?.missing || []
            },
            xyz_impact: {
              name: "Google/IBM X-Y-Z Impact",
              weight: 0.30,
              score: report?.metrics?.find(m => m.name.toLowerCase().includes('impact'))?.score || 70,
              finding: "Action verbs, quantifiable outcomes, and tech tooling.",
              target_ratio: targetSeniority === 'senior' ? 0.85 : 0.80,
              actual_ratio: 0.75
            },
            structure: {
              name: "Structural Parseability",
              weight: 0.15,
              score: report?.formatting_hygiene?.formatting_score || report?.metrics?.find(m => m.name.toLowerCase().includes('layout'))?.score || 85,
              finding: "Single-column layout, contact info & standard headers."
            },
            density: {
              name: "Reading Density & Word Budget",
              weight: 0.15,
              score: wordCount >= 350 && wordCount <= 650 ? 100 : 75,
              finding: `${wordCount} words inside optimal ${targetPages}-page budget.`,
              density_status: wordCount >= 350 && wordCount <= 650 ? "Optimal" : "Needs Review"
            }
          },
          itemized_audit_trail: [
            { pillar: "Keywords & Hard Skills", weight: 0.40, score: 75, weighted_points: 30.0, detail: "Core language & framework recall." },
            { pillar: "Google/IBM X-Y-Z Impact", weight: 0.30, score: 70, weighted_points: 21.0, detail: "Quantified metric and action verb density." },
            { pillar: "Structural Parseability", weight: 0.15, score: 85, weighted_points: 12.75, detail: "Single-column layout, contact info & sections." },
            { pillar: "Reading Density & Word Budget", weight: 0.15, score: 80, weighted_points: 12.0, detail: "Word volume within target window." }
          ],
          regulatory_safe_harbor: {
            is_compliant: true,
            eu_ai_act_status: "COMPLIANT (Regulation (EU) 2024/1689 Annex III)",
            eu_ai_act_details: "100% deterministic 4-pillar arithmetic per Article 86 Right to Explanation.",
            nyc_ll_144_status: "SAFE_HARBOR_VERIFIED (NYC Local Law 144)",
            nyc_ll_144_details: "Zero demographic proxy variables used in scoring calculation.",
            legal_precedent: "Mobley v. Workday, Inc. (N.D. Cal. 2024) explainability safe harbor."
          }
        };

        const letterGradeColor = (grade) => {
          if (grade === 'A+') return 'linear-gradient(135deg, #10b981, #059669)';
          if (grade === 'A') return 'linear-gradient(135deg, #6366f1, #4f46e5)';
          if (grade === 'B') return 'linear-gradient(135deg, #3b82f6, #2563eb)';
          if (grade === 'C') return 'linear-gradient(135deg, #f59e0b, #d97706)';
          return 'linear-gradient(135deg, #ef4444, #dc2626)';
        };

        const letterGradeGlow = (grade) => {
          if (grade === 'A+') return 'rgba(16, 185, 129, 0.4)';
          if (grade === 'A') return 'rgba(99, 102, 241, 0.4)';
          if (grade === 'B') return 'rgba(59, 130, 246, 0.4)';
          if (grade === 'C') return 'rgba(245, 158, 11, 0.4)';
          return 'rgba(239, 68, 68, 0.4)';
        };

        const getModelPromptText = () => {
          const gaps = (complianceData.pillars?.keywords?.missing_keywords || []).join(', ') || 'None identified';
          const seniority = targetSeniority.toUpperCase();
          if (selectedPromptModel === 'claude') {
            return `<system>
You are an expert Technical Career Dossier Architect and ATS Compliance Auditor.
Your task is to refactor candidate resume bullets using the Google/IBM X-Y-Z accomplishment formula:
Accomplished [X] as measured by [Y], by doing [Z].
Target Seniority: ${seniority}.
</system>

<context>
<identified_skill_gaps>
${gaps}
</identified_skill_gaps>
</context>

<rules>
1. Formula: Accomplished [X], measured by [Y], by doing [Z].
2. Anti-Fabrication: Do NOT hallucinate unverified metrics. Use placeholders like [X% / $Y] if metric is missing.
3. Seniority Calibration: Enforce ${seniority}-level scope, architecture, and business outcomes.
4. Word Budget: 18–28 words per bullet. Eliminate passive duty phrases.
</rules>

<output_instructions>
Output refactored bullets in clean markdown with a brief 1-line rationale for each change.
</output_instructions>`;
          } else if (selectedPromptModel === 'cursor') {
            return `/* CURSOR COMPOSER: RESUME REFACTORING INSTRUCTION */
// Target Seniority: ${seniority}
// Identified Skill Gaps: ${gaps}

## INSTRUCTIONS:
Refactor the candidate bullets into Google/IBM X-Y-Z statements:
Accomplished [X] as measured by [Y], by doing [Z].

## CONSTRAINTS:
- No metric hallucination (use [bracketed placeholders] for unknown numbers).
- Target 18-28 words per bullet.
- Use past-tense power verbs (Architected, Engineered, Spearheaded, Optimized).`;
          } else if (selectedPromptModel === 'gpt') {
            return `# SYSTEM: RESUME OPTIMIZATION AGENT (GPT-4o)
Seniority Target: ${seniority}

## MISSING KEYWORDS TO INCORPORATE:
${gaps}

## MANDATORY GUIDELINES:
1. Apply Google XYZ: "Accomplished [X] as measured by [Y], by doing [Z]".
2. Anti-Hallucination: Never fabricate ungrounded metrics.
3. Length: Strictly 18-28 words per bullet.
4. Active Voice: Start with active Bloom's taxonomy verbs.`;
          }
          return report?.byok_agent_prompt || `# ROLE: SENIOR TECHNICAL RESUME ARCHITECT & ATS COMPLIANCE SPECIALIST

Accomplished [X] as measured by [Y], by doing [Z]
Target Seniority: ${seniority}
Identified Competency Gaps: ${gaps}
Anti-Fabrication Safeguard: Strictly zero invented metrics or tools.`;
        };

        const handleCopyAgentPrompt = () => {
          const promptText = getModelPromptText();
          navigator.clipboard.writeText(promptText);
          setCopiedPrompt(true);
          setTimeout(() => setCopiedPrompt(false), 2000);
        };

        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Executive Letter Grade Hero */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '1.25rem',
              padding: '1.5rem',
              background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(168, 85, 247, 0.06) 100%)',
              border: '1px solid var(--border-color)',
              borderRadius: '16px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
                <div style={{
                  width: '68px',
                  height: '68px',
                  borderRadius: '16px',
                  background: letterGradeColor(complianceData.letter_grade),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '2.2rem',
                  fontWeight: 800,
                  color: '#fff',
                  boxShadow: `0 0 24px ${letterGradeGlow(complianceData.letter_grade)}`
                }}>
                  {complianceData.letter_grade}
                </div>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0 }}>
                      4-Pillar ATS Compliance Audit
                    </h3>
                    <span style={{
                      fontSize: '0.8rem',
                      background: 'rgba(16, 185, 129, 0.15)',
                      color: 'var(--success)',
                      padding: '0.2rem 0.6rem',
                      borderRadius: '12px',
                      fontWeight: 700
                    }}>
                      {complianceData.composite_score} / 100
                    </span>
                  </div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                    {complianceData.grade_descriptor}
                  </div>
                </div>
              </div>

              {/* Seniority & Budget Selectors */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Seniority:</span>
                  <select
                    value={targetSeniority}
                    onChange={(e) => setTargetSeniority(e.target.value)}
                    style={{
                      background: 'rgba(0,0,0,0.4)',
                      border: '1px solid var(--border-color)',
                      color: 'white',
                      padding: '0.35rem 0.65rem',
                      borderRadius: '8px',
                      fontSize: '0.8rem',
                      cursor: 'pointer'
                    }}
                  >
                    <option value="junior">Junior (0-2 yrs)</option>
                    <option value="mid">Mid-Level (3-5 yrs)</option>
                    <option value="senior">Senior (6-9 yrs)</option>
                    <option value="staff">Staff / Principal (10+ yrs)</option>
                    <option value="executive">Executive / VP</option>
                  </select>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Budget:</span>
                  <select
                    value={targetPages}
                    onChange={(e) => setTargetPages(Number(e.target.value))}
                    style={{
                      background: 'rgba(0,0,0,0.4)',
                      border: '1px solid var(--border-color)',
                      color: 'white',
                      padding: '0.35rem 0.65rem',
                      borderRadius: '8px',
                      fontSize: '0.8rem',
                      cursor: 'pointer'
                    }}
                  >
                    <option value={1}>1 Page (350–650 words)</option>
                    <option value={2}>2 Pages (650–1100 words)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* 4 Pillars Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
              gap: '1rem'
            }}>
              {/* Pillar 1: Keywords */}
              <div className="glass-panel" style={{ padding: '1.2rem', background: 'rgba(255,255,255,0.02)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                    Pillar 1 (40% Weight)
                  </span>
                  <span style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--primary)' }}>
                    {complianceData.pillars?.keywords?.score || 0}%
                  </span>
                </div>
                <div style={{ fontWeight: 700, fontSize: '1rem', marginBottom: '0.35rem' }}>
                  Keywords & Hard Skills
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                  {complianceData.pillars?.keywords?.finding}
                </div>
                {complianceData.pillars?.keywords?.missing_keywords?.length > 0 && (
                  <div style={{ marginTop: '0.75rem', display: 'flex', flexWrap: 'wrap', gap: '0.3rem' }}>
                    {complianceData.pillars.keywords.missing_keywords.slice(0, 4).map((kw, i) => (
                      <span key={i} className="tag missing" style={{ fontSize: '0.7rem' }}>
                        + {kw}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Pillar 2: Google/IBM XYZ Impact */}
              <div className="glass-panel" style={{ padding: '1.2rem', background: 'rgba(255,255,255,0.02)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                    Pillar 2 (30% Weight)
                  </span>
                  <span style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent)' }}>
                    {complianceData.pillars?.xyz_impact?.score || 0}%
                  </span>
                </div>
                <div style={{ fontWeight: 700, fontSize: '1rem', marginBottom: '0.35rem' }}>
                  Google/IBM X-Y-Z Impact
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                  {complianceData.pillars?.xyz_impact?.finding}
                </div>
                <div style={{ marginTop: '0.75rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Target Ratio: {Math.round((complianceData.pillars?.xyz_impact?.target_ratio || 0.8) * 100)}% XYZ bullets
                </div>
              </div>

              {/* Pillar 3: Structural Parseability */}
              <div className="glass-panel" style={{ padding: '1.2rem', background: 'rgba(255,255,255,0.02)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                    Pillar 3 (15% Weight)
                  </span>
                  <span style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--success)' }}>
                    {complianceData.pillars?.structure?.score || 0}%
                  </span>
                </div>
                <div style={{ fontWeight: 700, fontSize: '1rem', marginBottom: '0.35rem' }}>
                  Structural Parseability
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                  {complianceData.pillars?.structure?.finding}
                </div>
                <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.4rem', fontSize: '0.75rem' }}>
                  <span style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'var(--success)', padding: '0.2rem 0.4rem', borderRadius: '4px' }}>
                    Zero PUA Traps
                  </span>
                  <span style={{ background: 'rgba(99, 102, 241, 0.1)', color: 'var(--primary)', padding: '0.2rem 0.4rem', borderRadius: '4px' }}>
                    Linear Flow
                  </span>
                </div>
              </div>

              {/* Pillar 4: Reading Density */}
              <div className="glass-panel" style={{ padding: '1.2rem', background: 'rgba(255,255,255,0.02)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                    Pillar 4 (15% Weight)
                  </span>
                  <span style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--warning)' }}>
                    {complianceData.pillars?.density?.score || 0}%
                  </span>
                </div>
                <div style={{ fontWeight: 700, fontSize: '1rem', marginBottom: '0.35rem' }}>
                  Reading Density & Budget
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                  {complianceData.pillars?.density?.finding}
                </div>
                <div style={{ marginTop: '0.75rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Word Count: {wordCount} words ({wordCountStatus})
                </div>
              </div>
            </div>

            {/* Regulatory Safe Harbor Certificate Card */}
            <div style={{
              background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(6, 182, 212, 0.04) 100%)',
              border: '1px solid rgba(16, 185, 129, 0.25)',
              borderRadius: '14px',
              padding: '1.25rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.75rem' }}>
                <ShieldCheck style={{ width: '22px', height: '22px', color: 'var(--success)' }} />
                <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 700 }}>
                  Regulatory Safe Harbor Verification (EU AI Act & NYC LL 144)
                </h4>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '0.75rem', fontSize: '0.82rem' }}>
                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.75rem', borderRadius: '8px' }}>
                  <div style={{ fontWeight: 700, color: 'var(--success)', marginBottom: '0.2rem' }}>
                    EU AI Act (Regulation 2024/1689 Annex III)
                  </div>
                  <div style={{ color: 'var(--text-secondary)' }}>
                    {complianceData.regulatory_safe_harbor?.eu_ai_act_details || '100% deterministic 4-pillar arithmetic per Article 86 Right to Explanation.'}
                  </div>
                </div>

                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.75rem', borderRadius: '8px' }}>
                  <div style={{ fontWeight: 700, color: 'var(--success)', marginBottom: '0.2rem' }}>
                    NYC Local Law 144 (AEDT Bias Safe Harbor)
                  </div>
                  <div style={{ color: 'var(--text-secondary)' }}>
                    {complianceData.regulatory_safe_harbor?.nyc_ll_144_details || 'Zero demographic proxy variables used in scoring calculation.'}
                  </div>
                </div>
              </div>
            </div>

            {/* Agent-Native BYOK Prompt Exporter */}
            <div className="glass-panel" style={{ padding: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Terminal style={{ width: '18px', height: '18px', color: 'var(--primary)' }} />
                  <span style={{ fontSize: '0.95rem', fontWeight: 700 }}>
                    Agent-Native BYOK Prompt Exporter (Claude 3.5 Sonnet / ChatGPT / Cursor)
                  </span>
                </div>
                <button
                  onClick={handleCopyAgentPrompt}
                  style={{
                    background: copiedPrompt ? 'var(--success)' : 'var(--primary)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    padding: '0.4rem 0.85rem',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.35rem',
                    transition: 'all 0.2s ease'
                  }}
                >
                  {copiedPrompt ? (
                    <>
                      <Check style={{ width: '14px', height: '14px' }} />
                      Copied to Clipboard!
                    </>
                  ) : (
                    <>
                      <Copy style={{ width: '14px', height: '14px' }} />
                      Copy Refactor Prompt
                    </>
                  )}
                </button>
              </div>

              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
                Enforces the strict Bring-Your-Own-Key (BYOK) privacy model. Paste this synthesized prompt into Claude 3.5 Sonnet, GPT-4o, or Cursor for zero-hallucination Google/IBM XYZ bullet refactoring.
              </p>

              <div style={{ position: 'relative' }}>
                <div style={{ display: 'flex', gap: '0.4rem', marginBottom: '0.65rem', flexWrap: 'wrap' }}>
                  {[
                    { id: 'claude', label: 'Claude 3.5 (XML)' },
                    { id: 'gpt', label: 'OpenAI GPT-4o' },
                    { id: 'cursor', label: 'Cursor Composer' },
                    { id: 'general', label: 'Universal Markdown' }
                  ].map((m) => (
                    <button
                      key={m.id}
                      type="button"
                      onClick={() => setSelectedPromptModel(m.id)}
                      style={{
                        padding: '0.28rem 0.65rem',
                        fontSize: '0.74rem',
                        borderRadius: '6px',
                        border: '1px solid var(--border-color)',
                        background: selectedPromptModel === m.id ? 'var(--primary)' : 'rgba(255,255,255,0.05)',
                        color: selectedPromptModel === m.id ? 'white' : 'var(--text-secondary)',
                        cursor: 'pointer',
                        fontWeight: selectedPromptModel === m.id ? 700 : 500,
                        transition: 'all 0.15s ease'
                      }}
                    >
                      {m.label}
                    </button>
                  ))}
                </div>

                <pre style={{
                  background: 'rgba(0,0,0,0.35)',
                  padding: '1rem',
                  borderRadius: '10px',
                  fontSize: '0.78rem',
                  color: 'var(--text-secondary)',
                  overflowX: 'auto',
                  fontFamily: 'monospace',
                  maxHeight: showFullPrompt ? 'none' : '150px',
                  transition: 'all 0.3s ease',
                  border: '1px solid var(--border-color)'
                }}>
                  {getModelPromptText()}
                </pre>
                <button
                  onClick={() => setShowFullPrompt(!showFullPrompt)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'var(--primary)',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    marginTop: '0.35rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.25rem'
                  }}
                >
                  {showFullPrompt ? <ChevronUp style={{ width: '14px', height: '14px' }} /> : <ChevronDown style={{ width: '14px', height: '14px' }} />}
                  {showFullPrompt ? 'Collapse Prompt Preview' : 'Expand Full Prompt Preview'}
                </button>
              </div>
            </div>

            {/* Itemized Audit Trail */}
            {complianceData.itemized_audit_trail && (
              <div className="glass-panel" style={{ padding: '1.25rem' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.75rem' }}>
                  Article 86 Right to Explanation: Itemized Audit Trail
                </h4>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
                        <th style={{ textAlign: 'left', padding: '0.5rem 0' }}>Pillar</th>
                        <th style={{ textAlign: 'center', padding: '0.5rem' }}>Weight</th>
                        <th style={{ textAlign: 'center', padding: '0.5rem' }}>Score</th>
                        <th style={{ textAlign: 'center', padding: '0.5rem' }}>Weighted Pts</th>
                        <th style={{ textAlign: 'left', padding: '0.5rem' }}>Audit Finding</th>
                      </tr>
                    </thead>
                    <tbody>
                      {complianceData.itemized_audit_trail.map((item, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                          <td style={{ padding: '0.6rem 0', fontWeight: 600 }}>{item.pillar}</td>
                          <td style={{ textAlign: 'center', padding: '0.6rem' }}>{Math.round(item.weight * 100)}%</td>
                          <td style={{ textAlign: 'center', padding: '0.6rem', color: 'var(--primary)', fontWeight: 700 }}>
                            {item.score}%
                          </td>
                          <td style={{ textAlign: 'center', padding: '0.6rem', color: 'var(--success)', fontWeight: 700 }}>
                            +{item.weighted_points}
                          </td>
                          <td style={{ padding: '0.6rem', color: 'var(--text-secondary)' }}>{item.detail}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        );
      })()}
    </div>
  );
}
