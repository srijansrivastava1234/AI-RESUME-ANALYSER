import React, { useState, useEffect } from 'react';
import {
  Server,
  Building2,
  Cpu,
  Layers,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  ShieldCheck,
  Split,
  FileCode2,
  HelpCircle,
  Loader2,
  Sparkles,
  RefreshCw
} from 'lucide-react';

const ENGINES = [
  { id: 'workday', name: 'Workday', icon: Building2, color: '#38bdf8', desc: 'Enterprise ERP & strict vertical scanline parser' },
  { id: 'greenhouse', name: 'Greenhouse / Lever', icon: Cpu, color: '#34d399', desc: 'Modern tech ATS with semantic keyword clustering' },
  { id: 'taleo', name: 'Taleo / Oracle', icon: Server, color: '#f59e0b', desc: 'Legacy enterprise parser with strict exact substring indexing' },
  { id: 'matrix', name: 'Comparative Matrix', icon: Layers, color: '#a855f7', desc: 'Unified cross-platform risk analysis' }
];

export default function AtsSimulatorTab({ extractedText, backendUrl }) {
  const [selectedEngine, setSelectedEngine] = useState('workday');
  const [simData, setSimData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchSimulation = async () => {
    if (!extractedText || !extractedText.trim()) return;

    setLoading(true);
    setError('');

    try {
      const res = await fetch(`${backendUrl}/api/simulate-ats`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_text: extractedText })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server returned status ${res.status}`);
      }

      const data = await res.json();
      setSimData(data);
    } catch (err) {
      console.error('Multi-ATS Simulation Error:', err);
      setError(err.message || 'Failed to simulate multi-ATS parsing.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSimulation();
  }, [extractedText, backendUrl]);

  if (loading) {
    return (
      <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
        <Loader2 size={32} className="spin text-cyan-400" style={{ margin: '0 auto 1rem auto' }} />
        <h4 style={{ fontSize: '1.1rem', marginBottom: '0.35rem' }}>Emulating Enterprise ATS Parsers...</h4>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
          Simulating Workday vertical scanlines, Greenhouse semantic clustering, and Taleo legacy indexers.
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center' }}>
        <AlertCircle size={32} className="text-red-400" style={{ margin: '0 auto 0.75rem auto' }} />
        <h4 style={{ color: '#ef4444', marginBottom: '0.5rem' }}>Simulation Error</h4>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1rem' }}>{error}</p>
        <button className="btn-primary" onClick={fetchSimulation} style={{ margin: '0 auto' }}>
          <RefreshCw size={14} className="inline mr-1" />
          <span>Retry Simulation</span>
        </button>
      </div>
    );
  }

  const currentEngineData = simData?.engines?.[selectedEngine];
  const overallScore = simData?.overall_cross_ats_score || 0;

  return (
    <div className="ats-simulator-container">
      {/* Top Banner & Cross-ATS Composite Score */}
      <div className="glass-panel ats-composite-banner">
        <div className="composite-info">
          <div className="composite-badge">
            <Sparkles size={14} className="text-cyan-400" />
            <span>Multi-ATS Engine Emulation Sandbox</span>
          </div>
          <h3>Enterprise ATS Parsing Diagnostic</h3>
          <p className="composite-subtext">
            Different ATS platforms parse resumes using wildly different algorithms. This sandbox reveals exactly how your resume is extracted by Workday, Greenhouse, and Taleo.
          </p>
        </div>

        <div className="composite-score-card">
          <div className="score-ring-wrap">
            <span
              className="score-number"
              style={{
                color: overallScore >= 80 ? '#34d399' : (overallScore >= 70 ? '#f59e0b' : '#ef4444')
              }}
            >
              {overallScore}%
            </span>
            <span className="score-label">Universal ATS Score</span>
          </div>
          <span className="composite-tier-pill">{simData?.tier || 'Universal Compatible'}</span>
        </div>
      </div>

      {/* Engine Switcher Tabs */}
      <div className="ats-engine-nav">
        {ENGINES.map((eng) => {
          const IconComp = eng.icon;
          const isActive = selectedEngine === eng.id;
          const score = simData?.engines?.[eng.id]?.compatibility_score;

          return (
            <button
              key={eng.id}
              className={`ats-engine-btn ${isActive ? 'active' : ''}`}
              onClick={() => setSelectedEngine(eng.id)}
              style={{
                borderColor: isActive ? eng.color : 'transparent'
              }}
            >
              <div className="engine-btn-left">
                <IconComp size={16} style={{ color: eng.color }} />
                <span>{eng.name}</span>
              </div>
              {score !== undefined && (
                <span
                  className="engine-mini-score"
                  style={{
                    background: score >= 80 ? 'rgba(52, 211, 153, 0.15)' : (score >= 70 ? 'rgba(245, 158, 11, 0.15)' : 'rgba(239, 68, 68, 0.15)'),
                    color: score >= 80 ? '#34d399' : (score >= 70 ? '#f59e0b' : '#ef4444')
                  }}
                >
                  {score}%
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Main Engine Content */}
      {selectedEngine === 'matrix' ? (
        /* Matrix Comparative View */
        <div className="glass-panel ats-matrix-panel">
          <h4 className="matrix-title">Cross-Engine Feature Comparison</h4>
          <div className="matrix-table-wrap">
            <table className="ats-matrix-table">
              <thead>
                <tr>
                  <th>ATS Engine</th>
                  <th>Parsing Architecture</th>
                  <th>Compatibility Score</th>
                  <th>Status</th>
                  <th>Primary Vulnerability</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="font-semibold text-cyan-400">🏢 Workday</td>
                  <td>Strict Top-to-Bottom Vertical Scanline</td>
                  <td className="font-mono">{simData?.engines?.workday?.compatibility_score}%</td>
                  <td>
                    {simData?.engines?.workday?.is_safe ? (
                      <span className="matrix-status safe"><CheckCircle2 size={13} /> Safe</span>
                    ) : (
                      <span className="matrix-status warn"><AlertTriangle size={13} /> Risk</span>
                    )}
                  </td>
                  <td>Multi-column text interleaving & header/footer loss</td>
                </tr>
                <tr>
                  <td className="font-semibold text-emerald-400">🌿 Greenhouse / Lever</td>
                  <td>Semantic Bag-of-Words & Skill Clustering</td>
                  <td className="font-mono">{simData?.engines?.greenhouse?.compatibility_score}%</td>
                  <td>
                    {simData?.engines?.greenhouse?.is_safe ? (
                      <span className="matrix-status safe"><CheckCircle2 size={13} /> Safe</span>
                    ) : (
                      <span className="matrix-status warn"><AlertTriangle size={13} /> Risk</span>
                    )}
                  </td>
                  <td>Unrecognized Unicode glyphs & low skill density</td>
                </tr>
                <tr>
                  <td className="font-semibold text-amber-400">🏛️ Taleo / Oracle</td>
                  <td>Legacy Exact Substring & Header Keyword Matcher</td>
                  <td className="font-mono">{simData?.engines?.taleo?.compatibility_score}%</td>
                  <td>
                    {simData?.engines?.taleo?.is_safe ? (
                      <span className="matrix-status safe"><CheckCircle2 size={13} /> Safe</span>
                    ) : (
                      <span className="matrix-status warn"><AlertTriangle size={13} /> Risk</span>
                    )}
                  </td>
                  <td>Creative section header rejection & unexpanded acronyms</td>
                </tr>
              </tbody>
            </table>
          </div>

          {simData?.summary_alerts?.length > 0 && (
            <div className="matrix-alerts-block">
              <h5>Detected System Hazards ({simData.summary_alerts.length})</h5>
              <div className="alerts-list">
                {simData.summary_alerts.map((alt, i) => (
                  <div key={i} className="alert-row">
                    <AlertTriangle size={14} className="text-amber-400 flex-shrink-0" />
                    <span>{alt}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Single Engine Detailed Diagnostic */
        <div className="ats-engine-detail-grid">
          {/* Hazards & Extraction Card */}
          <div className="glass-panel engine-hazards-card">
            <div className="engine-card-header">
              <ShieldCheck size={18} style={{ color: ENGINES.find(e => e.id === selectedEngine)?.color }} />
              <h4>{currentEngineData?.engine} Parser Diagnostics</h4>
            </div>

            {currentEngineData?.hazards?.length > 0 ? (
              <div className="engine-hazard-list">
                {currentEngineData.hazards.map((hz, i) => (
                  <div key={i} className="hazard-item">
                    <AlertCircle size={14} className="text-red-400 flex-shrink-0 mt-0.5" />
                    <p>{hz}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="engine-perfect-pass">
                <CheckCircle2 size={24} className="text-emerald-400" />
                <p>No formatting traps or parser failures detected for {currentEngineData?.engine}.</p>
              </div>
            )}

            {/* Engine Extracted Entities */}
            {selectedEngine === 'workday' && (
              <div className="engine-entities-box">
                <h5>Workday Profile Field Detection</h5>
                <div className="entities-grid">
                  <div className="entity-item">
                    <span className="entity-lbl">Candidate Name:</span>
                    <span className="entity-val font-semibold">{currentEngineData?.extracted_entities?.candidate_name}</span>
                  </div>
                  <div className="entity-item">
                    <span className="entity-lbl">Email Address:</span>
                    <span className="entity-val">{currentEngineData?.extracted_entities?.email || '❌ Missing in Header'}</span>
                  </div>
                  <div className="entity-item">
                    <span className="entity-lbl">Experience Section:</span>
                    <span className="entity-val text-emerald-400">
                      {currentEngineData?.extracted_entities?.experience_detected ? '✓ Detected' : '❌ Missing'}
                    </span>
                  </div>
                  <div className="entity-item">
                    <span className="entity-lbl">Education Section:</span>
                    <span className="entity-val text-emerald-400">
                      {currentEngineData?.extracted_entities?.education_detected ? '✓ Detected' : '❌ Missing'}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {selectedEngine === 'greenhouse' && (
              <div className="engine-entities-box">
                <h5>Greenhouse Skill Taxonomy Clusters</h5>
                {Object.keys(currentEngineData?.extracted_entities?.skill_clusters || {}).length > 0 ? (
                  <div className="cluster-list">
                    {Object.entries(currentEngineData?.extracted_entities?.skill_clusters || {}).map(([cName, sList]) => (
                      <div key={cName} className="cluster-row">
                        <span className="cluster-name">{cName}:</span>
                        <div className="cluster-tags">
                          {sList.map((s, idx) => (
                            <span key={idx} className="cluster-tag">{s}</span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-400">No dense skill clusters identified.</p>
                )}
              </div>
            )}

            {selectedEngine === 'taleo' && (
              <div className="engine-entities-box">
                <h5>Taleo Legacy Matching Parameters</h5>
                <div className="entities-grid">
                  <div className="entity-item">
                    <span className="entity-lbl">Indexing Tier:</span>
                    <span className="entity-val font-semibold text-amber-400">
                      {currentEngineData?.extracted_entities?.legacy_indexing_tier}
                    </span>
                  </div>
                  <div className="entity-item">
                    <span className="entity-lbl">Unexpanded Acronyms:</span>
                    <span className="entity-val">
                      {currentEngineData?.extracted_entities?.unexpanded_acronyms?.length || 0} flagged
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Side-by-Side Raw vs Parsed Output Diff */}
          <div className="glass-panel engine-stream-card">
            <div className="engine-card-header">
              <FileCode2 size={18} className="text-cyan-400" />
              <h4>Extracted Text Stream ({currentEngineData?.engine})</h4>
            </div>
            <p className="stream-subtitle">
              This is the raw, unformatted plaintext stream {currentEngineData?.engine}'s parser produces after document linearization:
            </p>

            <pre className="ats-stream-pre">
              {currentEngineData?.parsed_text || extractedText}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
