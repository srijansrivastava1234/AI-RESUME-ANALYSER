import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  HelpCircle,
  AlertTriangle,
  CheckCircle2,
  BrainCircuit,
  MessageSquareCode,
  ShieldAlert,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Copy,
  Check,
  Award,
  Layers,
  Edit3,
  Flame
} from 'lucide-react';

const CATEGORY_MAP = {
  all: { label: 'All Questions', color: '#6366f1' },
  behavioral_star: { label: 'Behavioral & STAR', color: '#38bdf8' },
  technical_deep_dive: { label: 'Technical Deep-Dive', color: '#34d399' },
  resume_gap_probe: { label: 'Resume Vulnerabilities & Gaps', color: '#f59e0b' },
  system_design_or_scenario: { label: 'System Design / Scenario', color: '#a855f7' }
};

export default function InterviewPrepPanel({ extractedText, jobDesc, backendUrl }) {
  const [prepData, setPrepData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');
  const [expandedCards, setExpandedCards] = useState({});
  const [practiceNotes, setPracticeNotes] = useState({});
  const [activePracticeBox, setActivePracticeBox] = useState(null);
  const [copiedId, setCopiedId] = useState(null);

  const fetchInterviewPrep = async () => {
    if (!extractedText || !extractedText.trim()) return;

    setLoading(true);
    setError('');

    try {
      const res = await fetch(`${backendUrl}/api/interview-prep`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: extractedText,
          job_desc: jobDesc || ''
        })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `HTTP ${res.status}: Failed to generate interview questions.`);
      }

      const data = await res.json();
      setPrepData(data);
      // Expand the first two cards by default
      if (data.questions && data.questions.length > 0) {
        setExpandedCards({ 0: true, 1: true });
      }
    } catch (err) {
      console.error('Interview Prep fetch error:', err);
      setError(err.message || 'Failed to generate interview preparation questions.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (extractedText && extractedText.trim().length > 20) {
      fetchInterviewPrep();
    }
  }, [extractedText, jobDesc]);

  const toggleCard = (idx) => {
    setExpandedCards(prev => ({
      ...prev,
      [idx]: !prev[idx]
    }));
  };

  const handleCopyQuestion = (idx, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(idx);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleNoteChange = (idx, text) => {
    setPracticeNotes(prev => ({
      ...prev,
      [idx]: text
    }));
  };

  if (!extractedText || !extractedText.trim()) {
    return (
      <div className="empty-panel-state">
        <HelpCircle size={48} className="empty-icon text-muted" />
        <p className="empty-state-title">No Resume Loaded</p>
        <p className="empty-state-subtitle">
          Please upload or paste your resume to generate targeted "Recruiter Grill-Me" interview questions.
        </p>
      </div>
    );
  }

  const questions = prepData?.questions || [];
  const filteredQuestions = activeCategory === 'all'
    ? questions
    : questions.filter(q => q.category === activeCategory);

  const getDifficultyColor = (diff) => {
    switch ((diff || '').toLowerCase()) {
      case 'hard':
      case 'advanced':
        return '#f43f5e';
      case 'intermediate':
      case 'medium':
        return '#f59e0b';
      case 'basic':
      case 'easy':
      default:
        return '#10b981';
    }
  };

  return (
    <div className="interview-prep-panel">
      {/* Header Banner */}
      <div className="interview-header-card">
        <div className="interview-header-content">
          <div className="interview-title-row">
            <div className="interview-icon-badge">
              <Flame size={22} className="text-amber-400" />
            </div>
            <div>
              <h2 className="interview-main-title">🎯 Recruiter "Grill-Me" Interview Simulation</h2>
              <p className="interview-sub-title">
                High-friction behavioral, technical, and resume-gap questions synthesized directly from your experience vs. targeted JD requirements.
              </p>
            </div>
          </div>

          <div className="interview-header-actions">
            {prepData && (
              <span className={`ai-mode-pill ${prepData.ai_powered ? 'mode-gemini' : 'mode-heuristic'}`}>
                {prepData.ai_powered ? (
                  <>
                    <Sparkles size={14} /> Gemini 2.5 AI Powered
                  </>
                ) : (
                  <>
                    <BrainCircuit size={14} /> Deterministic Heuristic Engine
                  </>
                )}
              </span>
            )}
            <button
              className="refresh-prep-btn"
              onClick={fetchInterviewPrep}
              disabled={loading}
              title="Re-generate Interview Questions"
            >
              <RefreshCw size={15} className={loading ? 'spin-icon' : ''} />
              {loading ? 'Synthesizing...' : 'Regenerate'}
            </button>
          </div>
        </div>

        {prepData?.summary && (
          <div className="interview-summary-banner">
            <MessageSquareCode size={18} className="text-indigo-400 shrink-0" />
            <p className="summary-text">{prepData.summary}</p>
          </div>
        )}
      </div>

      {error && (
        <div className="error-banner">
          <AlertTriangle size={18} />
          <span>{error}</span>
          <button className="error-retry-btn" onClick={fetchInterviewPrep}>Retry</button>
        </div>
      )}

      {loading && !prepData ? (
        <div className="loading-interview-box">
          <div className="pulse-loader" />
          <p className="loading-text">Analyzing resume vulnerability vectors & generating recruiter questions...</p>
        </div>
      ) : (
        <>
          {/* Category Filter Pills */}
          <div className="interview-category-filter">
            {Object.entries(CATEGORY_MAP).map(([catKey, catMeta]) => {
              const count = catKey === 'all'
                ? questions.length
                : questions.filter(q => q.category === catKey).length;

              return (
                <button
                  key={catKey}
                  className={`category-pill ${activeCategory === catKey ? 'active' : ''}`}
                  onClick={() => setActiveCategory(catKey)}
                  style={{
                    '--cat-accent': catMeta.color
                  }}
                >
                  <span>{catMeta.label}</span>
                  <span className="cat-count-badge">{count}</span>
                </button>
              );
            })}
          </div>

          {/* Question Cards List */}
          <div className="questions-feed">
            {filteredQuestions.length === 0 ? (
              <div className="no-questions-placeholder">
                <p>No questions found for this specific category.</p>
              </div>
            ) : (
              filteredQuestions.map((q, idx) => {
                const isExpanded = !!expandedCards[idx];
                const diffColor = getDifficultyColor(q.difficulty);
                const isPracticing = activePracticeBox === idx;
                const userNotes = practiceNotes[idx] || '';
                const wordCount = userNotes.trim() ? userNotes.trim().split(/\s+/).length : 0;

                return (
                  <div key={idx} className={`interview-question-card ${isExpanded ? 'expanded' : ''}`}>
                    {/* Card Header Top */}
                    <div className="q-card-top" onClick={() => toggleCard(idx)}>
                      <div className="q-meta-badges">
                        <span
                          className="q-category-tag"
                          style={{
                            backgroundColor: `${CATEGORY_MAP[q.category]?.color || '#6366f1'}20`,
                            color: CATEGORY_MAP[q.category]?.color || '#818cf8',
                            borderColor: `${CATEGORY_MAP[q.category]?.color || '#6366f1'}40`
                          }}
                        >
                          {CATEGORY_MAP[q.category]?.label || q.category}
                        </span>

                        <span
                          className="q-diff-tag"
                          style={{
                            color: diffColor,
                            backgroundColor: `${diffColor}18`,
                            borderColor: `${diffColor}40`
                          }}
                        >
                          {q.difficulty || 'Medium'}
                        </span>
                      </div>

                      <div className="q-card-controls" onClick={(e) => e.stopPropagation()}>
                        <button
                          className="q-copy-btn"
                          title="Copy Question to Clipboard"
                          onClick={() => handleCopyQuestion(idx, q.question)}
                        >
                          {copiedId === idx ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
                        </button>
                        <button
                          className="q-expand-toggle"
                          onClick={() => toggleCard(idx)}
                          title={isExpanded ? 'Collapse Answer Strategy' : 'Expand Strategy'}
                        >
                          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                        </button>
                      </div>
                    </div>

                    {/* Question Statement */}
                    <div className="q-statement-box" onClick={() => toggleCard(idx)}>
                      <h3 className="q-text">
                        <span className="q-number">Q{idx + 1}.</span> {q.question}
                      </h3>
                    </div>

                    {/* Collapsible Strategy & Breakdown */}
                    {isExpanded && (
                      <div className="q-breakdown-body">
                        {/* Recruiter Intent */}
                        {q.recruiter_intent && (
                          <div className="intent-box">
                            <div className="intent-header">
                              <BrainCircuit size={15} className="text-sky-400" />
                              <span>Why the Recruiter Asks This:</span>
                            </div>
                            <p className="intent-desc">{q.recruiter_intent}</p>
                          </div>
                        )}

                        {/* Suggested STAR Strategy */}
                        {q.star_strategy && (
                          <div className="star-strategy-box">
                            <div className="star-header">
                              <Award size={15} className="text-emerald-400" />
                              <span>Recommended STAR Framework Strategy:</span>
                            </div>

                            <div className="star-grid">
                              {q.star_strategy.situation && (
                                <div className="star-step star-s">
                                  <div className="star-badge">S</div>
                                  <div className="star-content">
                                    <strong>Situation:</strong> {q.star_strategy.situation}
                                  </div>
                                </div>
                              )}
                              {q.star_strategy.task && (
                                <div className="star-step star-t">
                                  <div className="star-badge">T</div>
                                  <div className="star-content">
                                    <strong>Task:</strong> {q.star_strategy.task}
                                  </div>
                                </div>
                              )}
                              {q.star_strategy.action && (
                                <div className="star-step star-a">
                                  <div className="star-badge">A</div>
                                  <div className="star-content">
                                    <strong>Action:</strong> {q.star_strategy.action}
                                  </div>
                                </div>
                              )}
                              {q.star_strategy.result && (
                                <div className="star-step star-r">
                                  <div className="star-badge">R</div>
                                  <div className="star-content">
                                    <strong>Result:</strong> {q.star_strategy.result}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Pitfalls to Avoid */}
                        {q.pitfalls_to_avoid && (
                          <div className="pitfalls-box">
                            <div className="pitfalls-header">
                              <ShieldAlert size={15} className="text-rose-400" />
                              <span>Critical Traps & Pitfalls:</span>
                            </div>
                            <p className="pitfalls-desc">{q.pitfalls_to_avoid}</p>
                          </div>
                        )}

                        {/* Interactive Practice Sandbox */}
                        <div className="practice-sandbox-wrapper">
                          <button
                            className={`toggle-practice-btn ${isPracticing ? 'active' : ''}`}
                            onClick={() => setActivePracticeBox(isPracticing ? null : idx)}
                          >
                            <Edit3 size={14} />
                            {isPracticing ? 'Hide Answer Sandbox' : 'Practice Your Response (Draft Sandbox)'}
                          </button>

                          {isPracticing && (
                            <div className="practice-editor-card">
                              <div className="practice-editor-header">
                                <span className="practice-title">Your Live Response Draft</span>
                                <span className={`word-count-badge ${wordCount > 150 ? 'good-length' : ''}`}>
                                  {wordCount} words (Ideal: 120-250)
                                </span>
                              </div>
                              <textarea
                                className="practice-textarea"
                                rows={4}
                                placeholder="Structure your answer here using STAR (Context -> Challenge -> Action -> Quantified Outcome)..."
                                value={userNotes}
                                onChange={(e) => handleNoteChange(idx, e.target.value)}
                              />
                              <p className="practice-hint">
                                💡 Tip: Keep behavioral answers under 2 minutes verbally (~180-220 words). Emphasize quantifiable metrics and specific decisions.
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </>
      )}
    </div>
  );
}
