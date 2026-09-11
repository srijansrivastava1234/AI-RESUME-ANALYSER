import React, { useState, useEffect, useCallback } from 'react';
import { 
  Zap, 
  Sparkles, 
  AlertTriangle, 
  CheckCircle, 
  Copy, 
  Check, 
  ArrowRight, 
  TrendingUp, 
  ShieldCheck, 
  Flame, 
  Sliders, 
  RefreshCw 
} from 'lucide-react';

const PRESETS = [
  {
    label: "Passive Duty (Weak)",
    bullet: "Responsible for assisting the development team with regular bug fixes and software updates.",
    seniority: "mid"
  },
  {
    label: "Unquantified Task (Average)",
    bullet: "Engineered backend microservices using Python and PostgreSQL for web platform.",
    seniority: "mid"
  },
  {
    label: "Elite Google XYZ (High Impact)",
    bullet: "Spearheaded migration of legacy monolith to FastAPI microservices on AWS, reducing p99 latency by 45% and saving $120k annually.",
    seniority: "senior"
  },
  {
    label: "Staff Architecture (Scale)",
    bullet: "Architected distributed event streaming platform with Apache Kafka and Kubernetes across 5 regions, scaling throughput to 500k req/s at 99.99% uptime.",
    seniority: "staff"
  }
];

export default function BulletImpactLab({ backendUrl }) {
  const [bullet, setBullet] = useState(PRESETS[0].bullet);
  const [seniority, setSeniority] = useState("mid");
  const [targetRole, setTargetRole] = useState("Senior Software Engineer");
  const [scoreData, setScoreData] = useState(null);
  const [scoringLoading, setScoringLoading] = useState(false);
  const [optimizeLoading, setOptimizeLoading] = useState(false);
  const [optimizedResult, setOptimizedResult] = useState(null);
  const [copiedOptimized, setCopiedOptimized] = useState(false);
  const [copiedOriginal, setCopiedOriginal] = useState(false);

  // Evaluate bullet using deterministic backend scorer
  const evaluateBullet = useCallback(async (textToScore, senLevel) => {
    if (!textToScore || !textToScore.trim()) {
      setScoreData(null);
      return;
    }
    setScoringLoading(true);
    try {
      const res = await fetch(`${backendUrl}/api/score-bullet`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bullet: textToScore.trim(),
          seniority: senLevel
        })
      });
      if (res.ok) {
        const data = await res.json();
        setScoreData(data);
      }
    } catch (err) {
      console.error("Failed to score bullet:", err);
    } finally {
      setScoringLoading(false);
    }
  }, [backendUrl]);

  // Initial evaluation on mount or input change
  useEffect(() => {
    const timer = setTimeout(() => {
      evaluateBullet(bullet, seniority);
    }, 350);
    return () => clearTimeout(timer);
  }, [bullet, seniority, evaluateBullet]);

  // Handle preset selection
  const applyPreset = (preset) => {
    setBullet(preset.bullet);
    setSeniority(preset.seniority);
    setOptimizedResult(null);
  };

  // Trigger Gemini AI Rewriter
  const handleOptimize = async () => {
    if (!bullet.trim()) return;
    setOptimizeLoading(true);
    try {
      const res = await fetch(`${backendUrl}/api/optimize-bullet`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bullet: bullet.trim(),
          target_role: targetRole.trim() || undefined
        })
      });
      if (res.ok) {
        const data = await res.json();
        setOptimizedResult(data);
      }
    } catch (err) {
      console.error("Failed to optimize bullet:", err);
    } finally {
      setOptimizeLoading(false);
    }
  };

  const copyText = (text, type) => {
    navigator.clipboard.writeText(text);
    if (type === 'optimized') {
      setCopiedOptimized(true);
      setTimeout(() => setCopiedOptimized(false), 2000);
    } else {
      setCopiedOriginal(true);
      setTimeout(() => setCopiedOriginal(false), 2000);
    }
  };

  const score = scoreData ? scoreData.score : 0;
  const getScoreColor = (s) => {
    if (s >= 80) return "var(--success)";
    if (s >= 60) return "var(--accent)";
    if (s >= 40) return "var(--warning)";
    return "var(--danger)";
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', animation: 'fadeIn 0.3s ease' }}>
      {/* Hero Banner */}
      <div className="glass-panel" style={{ padding: '1.5rem 2rem', position: 'relative', overflow: 'hidden' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa', padding: '0.25rem 0.65rem', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              <Flame style={{ width: '14px', height: '14px' }} />
              Google / IBM X-Y-Z Mathematical Formulation Engine
            </div>
            <h2 style={{ fontSize: '1.5rem', margin: '0 0 0.4rem 0' }}>
              Resume Bullet <span className="text-gradient">Impact Lab</span>
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', margin: 0, maxWidth: '680px' }}>
              Calibrate your career accomplishments with algorithmic precision: <strong>"Accomplished [X] as measured by [Y], by doing [Z]"</strong>. Audit action verbs, metrics, and tooling before transforming with Gemini AI.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {PRESETS.map((p, idx) => (
              <button
                key={idx}
                onClick={() => applyPreset(p)}
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid var(--border-color)',
                  color: 'white',
                  borderRadius: '8px',
                  padding: '0.35rem 0.75rem',
                  fontSize: '0.75rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                className="hover-glow"
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Grid: Input Column & Live Audit Column */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.5rem' }}>
        {/* Left Column: Bullet Editor & Controls */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <label style={{ fontSize: '0.875rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Sliders style={{ width: '16px', height: '16px', color: 'var(--primary)' }} />
              Career Bullet Point
            </label>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              {bullet.trim() ? bullet.trim().split(/\s+/).length : 0} words
            </span>
          </div>

          <textarea
            value={bullet}
            onChange={(e) => setBullet(e.target.value)}
            placeholder="e.g., Spearheaded migration of legacy monolith to FastAPI microservices on AWS, reducing p99 latency by 45% and saving $120k annually..."
            rows={5}
            style={{
              width: '100%',
              background: 'rgba(0, 0, 0, 0.25)',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              padding: '0.85rem',
              color: 'white',
              fontSize: '0.9rem',
              lineHeight: 1.5,
              resize: 'vertical',
              fontFamily: 'inherit'
            }}
          />

          {/* Seniority Calibration Selector */}
          <div>
            <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.4rem' }}>
              Seniority Calibration Tier:
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.4rem' }}>
              {[
                { id: "junior", label: "Junior", exp: "0–2y" },
                { id: "mid", label: "Mid", exp: "3–5y" },
                { id: "senior", label: "Senior", exp: "6–9y" },
                { id: "staff", label: "Staff", exp: "10+y" }
              ].map((tier) => (
                <button
                  key={tier.id}
                  onClick={() => setSeniority(tier.id)}
                  style={{
                    background: seniority === tier.id ? 'var(--primary)' : 'rgba(255, 255, 255, 0.04)',
                    color: 'white',
                    border: '1px solid ' + (seniority === tier.id ? 'var(--primary)' : 'var(--border-color)'),
                    borderRadius: '8px',
                    padding: '0.4rem 0.2rem',
                    textAlign: 'center',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <div style={{ fontSize: '0.75rem', fontWeight: 600 }}>{tier.label}</div>
                  <div style={{ fontSize: '0.65rem', opacity: 0.7 }}>{tier.exp}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Target Role Context */}
          <div>
            <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '0.4rem' }}>
              Target Job Title / Role Context (Optional):
            </label>
            <input
              type="text"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              placeholder="e.g. Senior Backend Engineer"
              style={{
                width: '100%',
                background: 'rgba(0, 0, 0, 0.25)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '0.6rem 0.8rem',
                color: 'white',
                fontSize: '0.85rem'
              }}
            />
          </div>

          {/* Action Trigger Buttons */}
          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
            <button
              onClick={handleOptimize}
              disabled={optimizeLoading || !bullet.trim()}
              style={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                background: 'linear-gradient(135deg, var(--primary), #8b5cf6)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                padding: '0.75rem 1rem',
                fontWeight: 600,
                fontSize: '0.85rem',
                cursor: optimizeLoading ? 'not-allowed' : 'pointer',
                opacity: optimizeLoading || !bullet.trim() ? 0.6 : 1,
                boxShadow: '0 4px 15px rgba(59, 130, 246, 0.3)',
                transition: 'all 0.2s ease'
              }}
            >
              {optimizeLoading ? (
                <>
                  <RefreshCw className="spinner" style={{ width: '16px', height: '16px' }} />
                  Synthesizing XYZ Impact...
                </>
              ) : (
                <>
                  <Sparkles style={{ width: '16px', height: '16px' }} />
                  Optimize with Google XYZ
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Deterministic Mathematical Audit Panel */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: '1.1rem', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <TrendingUp style={{ width: '18px', height: '18px', color: 'var(--primary)' }} />
              Deterministic Audit
            </h3>
            {scoreData && (
              <span style={{
                fontSize: '0.75rem',
                fontWeight: 600,
                padding: '0.2rem 0.6rem',
                borderRadius: '12px',
                background: score >= 75 ? 'rgba(16, 185, 129, 0.15)' : score >= 50 ? 'rgba(245, 158, 11, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                color: getScoreColor(score)
              }}>
                {scoreData.tier}
              </span>
            )}
          </div>

          {/* Mathematical Gauge Bar */}
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', borderRadius: '12px', padding: '1rem', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Google XYZ Impact Score</span>
              <span style={{ fontSize: '1.75rem', fontWeight: 800, color: getScoreColor(score) }}>
                {score}<span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>/100</span>
              </span>
            </div>

            <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '4px', overflow: 'hidden' }}>
              <div
                style={{
                  width: `${score}%`,
                  height: '100%',
                  background: `linear-gradient(90deg, ${getScoreColor(score)}, #3b82f6)`,
                  transition: 'width 0.4s ease'
                }}
              />
            </div>
          </div>

          {/* Pillar Scores Breakdown */}
          {scoreData && scoreData.component_scores && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.6rem' }}>
              <div style={{ background: 'rgba(0, 0, 0, 0.2)', padding: '0.65rem', borderRadius: '8px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>Action Verb (w=0.25)</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: getScoreColor(scoreData.component_scores.action_score) }}>
                  {scoreData.component_scores.action_score}%
                </div>
              </div>
              <div style={{ background: 'rgba(0, 0, 0, 0.2)', padding: '0.65rem', borderRadius: '8px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>Metrics (w=0.45)</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: getScoreColor(scoreData.component_scores.metric_score) }}>
                  {scoreData.component_scores.metric_score}%
                </div>
              </div>
              <div style={{ background: 'rgba(0, 0, 0, 0.2)', padding: '0.65rem', borderRadius: '8px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>Tooling (w=0.30)</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: getScoreColor(scoreData.component_scores.tooling_score) }}>
                  {scoreData.component_scores.tooling_score}%
                </div>
              </div>
            </div>
          )}

          {/* Detected Elements Chips */}
          {scoreData && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.8rem' }}>
              {scoreData.detected_action_verbs?.length > 0 && (
                <div>
                  <span style={{ color: 'var(--text-secondary)', marginRight: '0.4rem' }}>Verbs:</span>
                  {scoreData.detected_action_verbs.map((v, i) => (
                    <span key={i} style={{ background: 'rgba(59, 130, 246, 0.2)', color: '#93c5fd', padding: '0.15rem 0.5rem', borderRadius: '6px', marginRight: '0.3rem', fontWeight: 600 }}>
                      {v}
                    </span>
                  ))}
                </div>
              )}

              {scoreData.detected_metrics?.length > 0 && (
                <div>
                  <span style={{ color: 'var(--text-secondary)', marginRight: '0.4rem' }}>Metrics:</span>
                  {scoreData.detected_metrics.map((m, i) => (
                    <span key={i} style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#6ee7b7', padding: '0.15rem 0.5rem', borderRadius: '6px', marginRight: '0.3rem', fontWeight: 600 }}>
                      {m}
                    </span>
                  ))}
                </div>
              )}

              {scoreData.detected_tools?.length > 0 && (
                <div>
                  <span style={{ color: 'var(--text-secondary)', marginRight: '0.4rem' }}>Stack:</span>
                  {scoreData.detected_tools.map((t, i) => (
                    <span key={i} style={{ background: 'rgba(168, 85, 247, 0.2)', color: '#d8b4fe', padding: '0.15rem 0.5rem', borderRadius: '6px', marginRight: '0.3rem', fontWeight: 600 }}>
                      {t}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Penalties & Deductions */}
          {scoreData && scoreData.penalties?.length > 0 && (
            <div style={{ background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.25)', borderRadius: '8px', padding: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: '#f87171', fontWeight: 600, fontSize: '0.75rem', marginBottom: '0.4rem' }}>
                <AlertTriangle style={{ width: '14px', height: '14px' }} />
                Detected Penalties & Deductions
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                {scoreData.penalties.map((p, i) => (
                  <div key={i} style={{ fontSize: '0.75rem', color: '#fca5a5' }}>
                    <strong>-{p.deduction} pts:</strong> {p.reason || p.name}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Improvement Tips */}
          {scoreData && scoreData.improvement_tips?.length > 0 && (
            <div style={{ background: 'rgba(59, 130, 246, 0.06)', border: '1px solid rgba(59, 130, 246, 0.2)', borderRadius: '8px', padding: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: '#60a5fa', fontWeight: 600, fontSize: '0.75rem', marginBottom: '0.4rem' }}>
                <ShieldCheck style={{ width: '14px', height: '14px' }} />
                Actionable Heuristic Advice
              </div>
              <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                {scoreData.improvement_tips.map((tip, i) => (
                  <li key={i} style={{ marginBottom: '0.2rem' }}>{tip}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Side-by-Side Before vs After Rewritten Output */}
      {optimizedResult && (
        <div className="glass-panel" style={{ padding: '1.5rem', animation: 'fadeIn 0.3s ease' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1.15rem', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Sparkles style={{ width: '18px', height: '18px', color: 'var(--accent)' }} />
              Google XYZ Synthesized Comparison
            </h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              Source: {optimizedResult.source === 'gemini' ? 'Google Gemini 1.5 Flash' : 'Heuristic XYZ Template'}
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem' }}>
            {/* Before */}
            <div style={{ background: 'rgba(239, 68, 68, 0.05)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '8px', padding: '1rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#f87171', marginBottom: '0.5rem', textTransform: 'uppercase' }}>
                  Original Bullet
                </div>
                <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {optimizedResult.original}
                </p>
              </div>
              <div style={{ marginTop: '0.75rem', display: 'flex', justifyContent: 'flex-end' }}>
                <button
                  onClick={() => copyText(optimizedResult.original, 'original')}
                  style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', fontSize: '0.75rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                >
                  {copiedOriginal ? <Check style={{ width: '13px', height: '13px', color: 'var(--success)' }} /> : <Copy style={{ width: '13px', height: '13px' }} />}
                  {copiedOriginal ? 'Copied' : 'Copy'}
                </button>
              </div>
            </div>

            {/* After */}
            <div style={{ background: 'rgba(16, 185, 129, 0.06)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', padding: '1rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#34d399', textTransform: 'uppercase' }}>
                    Google XYZ High-Impact Formula
                  </span>
                  <span style={{ fontSize: '0.7rem', background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', padding: '0.15rem 0.45rem', borderRadius: '6px', fontWeight: 600 }}>
                    ATS Optimized
                  </span>
                </div>
                <p style={{ margin: 0, fontSize: '0.9rem', color: 'white', fontWeight: 500, lineHeight: 1.5 }}>
                  {optimizedResult.optimized}
                </p>
                {optimizedResult.explanation && (
                  <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.75rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                    {optimizedResult.explanation}
                  </p>
                )}
              </div>
              <div style={{ marginTop: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <button
                  onClick={() => setBullet(optimizedResult.optimized)}
                  style={{ background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white', borderRadius: '6px', padding: '0.25rem 0.5rem', fontSize: '0.75rem', cursor: 'pointer' }}
                >
                  Load into Scorer
                </button>
                <button
                  onClick={() => copyText(optimizedResult.optimized, 'optimized')}
                  style={{ background: 'var(--primary)', border: 'none', color: 'white', borderRadius: '6px', padding: '0.35rem 0.75rem', fontSize: '0.75rem', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                >
                  {copiedOptimized ? <Check style={{ width: '13px', height: '13px' }} /> : <Copy style={{ width: '13px', height: '13px' }} />}
                  {copiedOptimized ? 'Copied to Clipboard!' : 'Copy XYZ Bullet'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
