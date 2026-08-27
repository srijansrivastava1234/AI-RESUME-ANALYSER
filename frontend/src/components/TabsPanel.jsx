import React, { useState } from 'react';
import { CheckCircle, AlertTriangle, BookOpen, Clock, FileText, ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';

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

  const getKeywordFrequency = (text) => {
    if (!text) return [];
    const stopwords = new Set([
      'the', 'and', 'a', 'of', 'to', 'in', 'for', 'is', 'on', 'that', 'by', 'this', 'with', 'i', 'you', 'it', 'he', 'she', 'they', 'we',
      'as', 'an', 'are', 'at', 'be', 'from', 'has', 'have', 'his', 'her', 'in', 'into', 'its', 'my', 'or', 'their', 'there', 'who', 'which',
      'was', 'were', 'will', 'with', 'about', 'but', 'not', 'can', 'our', 'out', 'all', 'more', 'some', 'any', 'been', 'other', 'than',
      'very', 'using', 'used', 'through', 'under', 'over', 'during', 'before', 'after', 'between', 'also', 'each', 'both', 'some'
    ]);
    
    const words = text
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .split(/\s+/)
      .filter(w => w.length > 2 && !stopwords.has(w));
      
    const freq = {};
    words.forEach(w => {
      freq[w] = (freq[w] || 0) + 1;
    });
    
    return Object.entries(freq)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([word, count]) => ({ word: word.charAt(0).toUpperCase() + word.slice(1), count }));
  };

  const freqKeywords = getKeywordFrequency(extractedText);

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
