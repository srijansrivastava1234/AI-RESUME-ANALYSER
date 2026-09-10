import React, { useState } from 'react';
import { 
  Users, 
  UploadCloud, 
  X, 
  Trophy, 
  CheckCircle2, 
  AlertCircle, 
  BarChart2, 
  ArrowRight,
  Sparkles,
  FileText
} from 'lucide-react';

export default function ComparePanel({ backendUrl, getScoreColor, getScoreBg }) {
  const [files, setFiles] = useState([]);
  const [jobDesc, setJobDesc] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [comparisonResult, setComparisonResult] = useState(null);
  const [expandedRank, setExpandedRank] = useState(1);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files || []);
    if (!selectedFiles.length) return;

    // Filter valid extensions
    const valid = selectedFiles.filter(f => {
      const ext = f.name.toLowerCase();
      return ext.endsWith('.pdf') || ext.endsWith('.docx') || ext.endsWith('.txt');
    });

    if (valid.length !== selectedFiles.length) {
      setError('Some files were skipped. Only PDF, DOCX, and TXT files are supported.');
    } else {
      setError('');
    }

    setFiles(prev => {
      const combined = [...prev, ...valid];
      if (combined.length > 5) {
        setError('Maximum 5 resumes can be compared at once.');
        return combined.slice(0, 5);
      }
      return combined;
    });
  };

  const removeFile = (indexToRemove) => {
    setFiles(prev => prev.filter((_, idx) => idx !== indexToRemove));
  };

  const runComparison = async () => {
    if (files.length < 2) {
      setError('Please upload at least 2 resumes to compare.');
      return;
    }
    setError('');
    setLoading(true);
    setComparisonResult(null);

    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });
      if (jobDesc.trim()) {
        formData.append('job_description', jobDesc.trim());
      }

      const response = await fetch(`${backendUrl}/api/compare`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to compare resumes.');
      }

      const data = await response.json();
      setComparisonResult(data);
      if (data.rankings && data.rankings.length > 0) {
        setExpandedRank(data.rankings[0].rank);
      }
    } catch (err) {
      setError(err.message || 'An error occurred during comparison.');
    } finally {
      setLoading(false);
    }
  };

  const resetComparison = () => {
    setComparisonResult(null);
    setFiles([]);
    setJobDesc('');
    setError('');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header Banner */}
      <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', fontSize: '1.4rem', margin: 0 }}>
            <Users style={{ color: 'var(--primary)', width: '26px', height: '26px' }} />
            <span>Candidate Comparison Leaderboard</span>
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: '0.35rem 0 0 0' }}>
            Upload 2 to 5 resumes to compare ATS scores, keyword densities, and qualifications side-by-side.
          </p>
        </div>
        {comparisonResult && (
          <button 
            onClick={resetComparison} 
            className="btn-print"
            style={{ padding: '0.45rem 1rem', fontSize: '0.85rem' }}
          >
            New Comparison
          </button>
        )}
      </div>

      {error && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.15)',
          border: '1px solid rgba(239, 68, 68, 0.4)',
          borderRadius: '8px',
          padding: '0.85rem 1.2rem',
          color: '#fca5a5',
          display: 'flex',
          alignItems: 'center',
          gap: '0.6rem',
          fontSize: '0.9rem'
        }}>
          <AlertCircle style={{ width: '18px', height: '18px', flexShrink: 0 }} />
          <span>{error}</span>
        </div>
      )}

      {/* Upload and Configuration Phase */}
      {!comparisonResult && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
          {/* File Upload Box */}
          <div className="glass-panel" style={{ padding: '1.5rem' }}>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <UploadCloud style={{ width: '18px', height: '18px', color: 'var(--primary)' }} />
              <span>1. Upload Resumes (2 - 5)</span>
            </h3>

            <label style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              border: '2px dashed var(--border-color)',
              borderRadius: '12px',
              padding: '2rem 1rem',
              cursor: 'pointer',
              background: 'rgba(255, 255, 255, 0.02)',
              transition: 'var(--transition-smooth)'
            }}>
              <UploadCloud style={{ width: '36px', height: '36px', color: 'var(--text-secondary)', marginBottom: '0.5rem' }} />
              <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>Click to select resumes</span>
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '0.25rem' }}>
                PDF, DOCX, or TXT (Max 5 files)
              </span>
              <input 
                type="file" 
                multiple 
                accept=".pdf,.docx,.txt" 
                onChange={handleFileChange} 
                style={{ display: 'none' }} 
              />
            </label>

            {/* Selected File List */}
            {files.length > 0 && (
              <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                  Selected Files ({files.length}/5):
                </span>
                {files.map((f, idx) => (
                  <div key={idx} style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.5rem 0.75rem',
                    background: 'rgba(255, 255, 255, 0.04)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '6px',
                    fontSize: '0.85rem'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', overflow: 'hidden' }}>
                      <FileText style={{ width: '16px', height: '16px', color: 'var(--primary)', flexShrink: 0 }} />
                      <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '200px' }}>
                        {f.name}
                      </span>
                      <span style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>
                        ({(f.size / 1024).toFixed(1)} KB)
                      </span>
                    </div>
                    <button 
                      onClick={() => removeFile(idx)}
                      style={{ background: 'none', border: 'none', color: '#f87171', cursor: 'pointer', padding: '2px' }}
                      title="Remove file"
                    >
                      <X style={{ width: '16px', height: '16px' }} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Job Description Input */}
          <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <BarChart2 style={{ width: '18px', height: '18px', color: 'var(--primary)' }} />
              <span>2. Shared Job Description (Optional)</span>
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.75rem' }}>
              Paste the target role description to evaluate job compatibility across all candidates.
            </p>
            <textarea
              value={jobDesc}
              onChange={(e) => setJobDesc(e.target.value)}
              placeholder="Paste job description here (e.g. Senior Python Engineer with FastAPI, Docker, AWS)..."
              style={{
                width: '100%',
                flex: 1,
                minHeight: '140px',
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                color: 'var(--text-primary)',
                padding: '0.75rem',
                fontSize: '0.85rem',
                fontFamily: 'var(--font-code)',
                resize: 'vertical'
              }}
            />
            <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end' }}>
              <button
                onClick={runComparison}
                disabled={files.length < 2 || loading}
                className="btn-analyze"
                style={{
                  padding: '0.7rem 1.5rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  fontSize: '0.95rem',
                  opacity: files.length < 2 || loading ? 0.6 : 1,
                  cursor: files.length < 2 || loading ? 'not-allowed' : 'pointer'
                }}
              >
                {loading ? (
                  <>
                    <div className="spinner" style={{ width: '16px', height: '16px', margin: 0 }}></div>
                    <span>Ranking Resumes...</span>
                  </>
                ) : (
                  <>
                    <Sparkles style={{ width: '18px', height: '18px' }} />
                    <span>Compare & Rank Resumes ({files.length})</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Results View */}
      {comparisonResult && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Summary Card */}
          <div className="glass-panel" style={{
            padding: '1.25rem 1.5rem',
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(168, 85, 247, 0.08))',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            display: 'flex',
            alignItems: 'center',
            gap: '1rem'
          }}>
            <Trophy style={{ width: '32px', height: '32px', color: '#eab308', flexShrink: 0 }} />
            <div>
              <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--primary)', fontWeight: 700 }}>
                Comparison Summary ({comparisonResult.total_compared} Resumes Ranked)
              </span>
              <p style={{ margin: '0.25rem 0 0 0', fontSize: '1rem', fontWeight: 600 }}>
                {comparisonResult.summary}
              </p>
            </div>
          </div>

          {/* Rankings Grid */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {comparisonResult.rankings.map((item) => {
              const isWinner = item.rank === 1;
              const isExpanded = expandedRank === item.rank;
              const rankColor = item.rank === 1 ? '#eab308' : item.rank === 2 ? '#94a3b8' : item.rank === 3 ? '#b45309' : 'var(--text-secondary)';

              return (
                <div 
                  key={item.rank}
                  className="glass-panel"
                  style={{
                    padding: '1.25rem',
                    border: isWinner ? '1px solid rgba(234, 179, 8, 0.4)' : '1px solid var(--border-color)',
                    background: isWinner ? 'rgba(234, 179, 8, 0.03)' : 'rgba(255, 255, 255, 0.02)',
                    transition: 'var(--transition-smooth)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
                    {/* Left: Rank badge & File info */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <div style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '50%',
                        background: isWinner ? 'rgba(234, 179, 8, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                        border: `2px solid ${rankColor}`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 800,
                        fontSize: '1.1rem',
                        color: rankColor
                      }}>
                        #{item.rank}
                      </div>
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span style={{ fontWeight: 700, fontSize: '1.05rem' }}>{item.filename}</span>
                          {isWinner && (
                            <span style={{
                              background: 'rgba(234, 179, 8, 0.2)',
                              color: '#fef08a',
                              fontSize: '0.7rem',
                              fontWeight: 700,
                              padding: '2px 8px',
                              borderRadius: '12px',
                              textTransform: 'uppercase'
                            }}>
                              Top Match
                            </span>
                          )}
                        </div>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                          Keywords: {item.detected_keywords_count} detected • {item.missing_keywords_count} missing
                        </span>
                      </div>
                    </div>

                    {/* Right: Scores & Actions */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                      <div style={{ textAlign: 'right' }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block' }}>ATS Score</span>
                        <span style={{
                          fontSize: '1.5rem',
                          fontWeight: 800,
                          color: getScoreColor ? getScoreColor(item.ats_score) : '#6366f1'
                        }}>
                          {item.ats_score}<span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>/100</span>
                        </span>
                      </div>

                      {item.job_compatibility_score !== null && (
                        <div style={{ textAlign: 'right' }}>
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block' }}>Job Match</span>
                          <span style={{
                            fontSize: '1.3rem',
                            fontWeight: 700,
                            color: getScoreColor ? getScoreColor(item.job_compatibility_score) : '#10b981'
                          }}>
                            {item.job_compatibility_score}%
                          </span>
                        </div>
                      )}

                      <button
                        onClick={() => setExpandedRank(isExpanded ? null : item.rank)}
                        style={{
                          background: 'rgba(255, 255, 255, 0.05)',
                          border: '1px solid var(--border-color)',
                          borderRadius: '6px',
                          color: 'var(--text-primary)',
                          padding: '0.4rem 0.8rem',
                          fontSize: '0.8rem',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.3rem'
                        }}
                      >
                        <span>{isExpanded ? 'Hide Details' : 'View Details'}</span>
                        <ArrowRight style={{ width: '14px', height: '14px', transform: isExpanded ? 'rotate(90deg)' : 'none', transition: 'transform 0.2s ease' }} />
                      </button>
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {isExpanded && item.report && (
                    <div style={{
                      marginTop: '1.25rem',
                      paddingTop: '1.25rem',
                      borderTop: '1px solid var(--border-color)',
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                      gap: '1rem'
                    }}>
                      <div>
                        <h4 style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
                          Key Strengths
                        </h4>
                        <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                          {item.key_strengths && item.key_strengths.map((str, sIdx) => (
                            <li key={sIdx}>{str}</li>
                          ))}
                        </ul>
                      </div>

                      {item.report.formatting_hygiene && (
                        <div>
                          <h4 style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
                            Formatting Hygiene
                          </h4>
                          <p style={{ margin: 0, fontSize: '0.85rem' }}>
                            Score: <strong>{item.report.formatting_hygiene.hygiene_score}/100</strong> ({item.report.formatting_hygiene.rating})
                          </p>
                          <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                            Word count: {item.report.formatting_hygiene.word_count} words • Bullets: {item.report.formatting_hygiene.bullet_count}
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
