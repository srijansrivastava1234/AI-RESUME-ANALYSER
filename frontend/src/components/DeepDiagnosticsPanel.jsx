import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  GraduationCap,
  Scale,
  Brain,
  Award,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  Loader2,
  RefreshCw,
  TrendingUp,
  Target,
  Sparkles
} from 'lucide-react';

export default function DeepDiagnosticsPanel({ extractedText, backendUrl = 'http://localhost:8000' }) {
  const [activeSubTab, setActiveSubTab] = useState('metric_consistency');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [metricData, setMetricData] = useState(null);
  const [eduData, setEduData] = useState(null);
  const [cogData, setCogData] = useState(null);
  const [secData, setSecData] = useState(null);
  const [leadData, setLeadData] = useState(null);

  const runAllDiagnostics = async () => {
    if (!extractedText || !extractedText.trim()) return;
    setLoading(true);
    setError('');

    try {
      const [mRes, eRes, cRes, sRes, lRes] = await Promise.all([
        fetch(`${backendUrl}/api/audit/metric-consistency`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ resume_text: extractedText })
        }).then(r => r.ok ? r.json() : null),
        fetch(`${backendUrl}/api/audit/education-hierarchy`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ resume_text: extractedText })
        }).then(r => r.ok ? r.json() : null),
        fetch(`${backendUrl}/api/audit/cognitive-load`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ resume_text: extractedText })
        }).then(r => r.ok ? r.json() : null),
        fetch(`${backendUrl}/api/audit/prompt-injection`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ resume_text: extractedText })
        }).then(r => r.ok ? r.json() : null),
        fetch(`${backendUrl}/api/audit/leadership-profile`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ resume_text: extractedText })
        }).then(r => r.ok ? r.json() : null),
      ]);

      setMetricData(mRes);
      setEduData(eRes);
      setCogData(cRes);
      setSecData(sRes);
      setLeadData(lRes);
    } catch (err) {
      console.error('Deep Diagnostics Audit Error:', err);
      setError('Failed to complete comprehensive diagnostic evaluation.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runAllDiagnostics();
  }, [extractedText]);

  const SUB_TABS = [
    { id: 'metric_consistency', label: 'Metric Verifiability', icon: Scale, score: metricData?.verifiability_score },
    { id: 'cognitive_load', label: 'Cognitive Readability', icon: Brain, score: cogData?.cognitive_load_score },
    { id: 'security_audit', label: 'Security & Steganography', icon: ShieldAlert, score: secData?.security_score },
    { id: 'leadership_profile', label: 'Leadership Scope', icon: TrendingUp, score: leadData?.overall_leadership_score },
    { id: 'education_hierarchy', label: 'Education Hierarchy', icon: GraduationCap, score: eduData?.ats_education_score },
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl text-slate-100">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5 mb-6">
        <div>
          <h3 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-400" />
            Deep Diagnostic & Security Analytics Hub
          </h3>
          <p className="text-sm text-slate-400 mt-1">
            Auditable mathematical scoring across verifiability, cognitive strain, LLM injection defense, and leadership scope.
          </p>
        </div>
        <button
          onClick={runAllDiagnostics}
          disabled={loading || !extractedText}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors shadow-lg"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
          Re-evaluate Diagnostics
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-950/40 border border-red-800/60 rounded-lg text-red-200 text-sm flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Sub-tab Navigation */}
      <div className="flex flex-wrap gap-2 mb-6 border-b border-slate-800 pb-3">
        {SUB_TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeSubTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveSubTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-indigo-600/20 border border-indigo-500 text-indigo-200 shadow-md'
                  : 'bg-slate-800/60 hover:bg-slate-800 text-slate-400 border border-transparent'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
              {typeof tab.score === 'number' && (
                <span className="ml-1.5 px-2 py-0.5 text-xs rounded-full bg-slate-950 font-mono font-semibold text-slate-300">
                  {Math.round(tab.score)}%
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Diagnostic Tab Views */}
      {loading ? (
        <div className="py-16 text-center text-slate-400 flex flex-col items-center justify-center gap-3">
          <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
          <p className="text-sm font-medium">Executing deep multi-engine diagnostic calculations...</p>
        </div>
      ) : (
        <div>
          {/* 1. Metric Verifiability */}
          {activeSubTab === 'metric_consistency' && metricData && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-slate-800/70 p-4 rounded-lg border border-slate-700/60">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Verifiability Score</span>
                  <div className="text-2xl font-bold text-emerald-400 mt-1">{metricData.verifiability_score}%</div>
                </div>
                <div className="bg-slate-800/70 p-4 rounded-lg border border-slate-700/60">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Total Metrics Claimed</span>
                  <div className="text-2xl font-bold text-sky-400 mt-1">{metricData.total_metrics_found}</div>
                </div>
                <div className="bg-slate-800/70 p-4 rounded-lg border border-slate-700/60">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Baseline Attached Rate</span>
                  <div className="text-2xl font-bold text-purple-400 mt-1">{Math.round(metricData.baseline_attachment_rate * 100)}%</div>
                </div>
              </div>

              <div className="bg-slate-800/40 p-4 rounded-lg border border-slate-800">
                <h4 className="text-sm font-semibold text-slate-200 mb-3">Metric Category Breakdown</h4>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-center text-xs">
                  <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800">
                    <div className="text-slate-400">Percentages</div>
                    <div className="font-bold text-slate-100 text-sm mt-1">{metricData.metric_breakdown.percentages}</div>
                  </div>
                  <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800">
                    <div className="text-slate-400">Multipliers</div>
                    <div className="font-bold text-slate-100 text-sm mt-1">{metricData.metric_breakdown.multipliers}</div>
                  </div>
                  <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800">
                    <div className="text-slate-400">Financial ($)</div>
                    <div className="font-bold text-slate-100 text-sm mt-1">{metricData.metric_breakdown.currency}</div>
                  </div>
                  <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800">
                    <div className="text-slate-400">Latency / QPS</div>
                    <div className="font-bold text-slate-100 text-sm mt-1">{metricData.metric_breakdown.latency_throughput}</div>
                  </div>
                  <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800">
                    <div className="text-slate-400">Entity Counts</div>
                    <div className="font-bold text-slate-100 text-sm mt-1">{metricData.metric_breakdown.raw_counts}</div>
                  </div>
                </div>
              </div>

              {metricData.recommendations?.length > 0 && (
                <div className="bg-slate-950/60 p-4 rounded-lg border border-slate-800">
                  <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-2">
                    <Target className="w-4 h-4 text-sky-400" />
                    Calibration Recommendations
                  </h4>
                  <ul className="space-y-1.5 text-xs text-slate-400">
                    {metricData.recommendations.map((rec, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-sky-400">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* 2. Cognitive Readability */}
          {activeSubTab === 'cognitive_load' && cogData && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                <div className="bg-slate-800/70 p-4 rounded-lg border border-slate-700/60">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Cognitive Score</span>
                  <div className="text-2xl font-bold text-emerald-400 mt-1">{cogData.cognitive_load_score}%</div>
                </div>
                <div className="bg-slate-800/70 p-4 rounded-lg border border-slate-700/60">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Gunning Fog Index</span>
                  <div className="text-2xl font-bold text-sky-400 mt-1">{cogData.gunning_fog_index}</div>
                </div>
                <div className="bg-slate-800/70 p-4 rounded-lg border border-slate-700/60">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Coleman-Liau</span>
                  <div className="text-2xl font-bold text-purple-400 mt-1">{cogData.coleman_liau_index}</div>
                </div>
                <div className="bg-slate-800/70 p-4 rounded-lg border border-slate-700/60">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Skimmability</span>
                  <div className="text-sm font-bold text-amber-400 mt-2">{cogData.skimmability_rating}</div>
                </div>
              </div>

              {cogData.recommendations?.length > 0 && (
                <div className="bg-slate-950/60 p-4 rounded-lg border border-slate-800">
                  <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Readability Insights</h4>
                  <ul className="space-y-1.5 text-xs text-slate-400">
                    {cogData.recommendations.map((rec, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-indigo-400">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* 3. Security & Steganography */}
          {activeSubTab === 'security_audit' && secData && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-slate-800/70 p-4 rounded-lg border border-slate-700/60">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Security Score</span>
                  <div className="text-2xl font-bold text-emerald-400 mt-1">{secData.security_score}%</div>
                </div>
                <div className="bg-slate-800/70 p-4 rounded-lg border border-slate-700/60">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Threat Level</span>
                  <div className={`text-xl font-bold mt-1 ${secData.threat_level === 'CLEAN' ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {secData.threat_level}
                  </div>
                </div>
                <div className="bg-slate-800/70 p-4 rounded-lg border border-slate-700/60">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Zero-Width Bytes</span>
                  <div className="text-2xl font-bold text-amber-400 mt-1">{secData.zero_width_chars_count}</div>
                </div>
              </div>

              {secData.recommendations?.length > 0 && (
                <div className="bg-slate-950/60 p-4 rounded-lg border border-slate-800">
                  <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Safety Audit Notes</h4>
                  <ul className="space-y-1.5 text-xs text-slate-400">
                    {secData.recommendations.map((rec, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-rose-400">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* 4. Leadership Scope */}
          {activeSubTab === 'leadership_profile' && leadData && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="bg-slate-800/70 p-4 rounded-lg border border-slate-700/60">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Overall Leadership Score</span>
                  <div className="text-2xl font-bold text-indigo-400 mt-1">{leadData.overall_leadership_score}%</div>
                </div>
                <div className="bg-slate-800/70 p-4 rounded-lg border border-slate-700/60">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Inferred Seniority Tier</span>
                  <div className="text-lg font-bold text-amber-400 mt-2">{leadData.inferred_leadership_tier}</div>
                </div>
              </div>

              {leadData.recommendations?.length > 0 && (
                <div className="bg-slate-950/60 p-4 rounded-lg border border-slate-800">
                  <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Leadership Roadmap</h4>
                  <ul className="space-y-1.5 text-xs text-slate-400">
                    {leadData.recommendations.map((rec, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-amber-400">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* 5. Education Hierarchy */}
          {activeSubTab === 'education_hierarchy' && eduData && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-slate-800/70 p-4 rounded-lg border border-slate-700/60">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Highest Degree</span>
                  <div className="text-lg font-bold text-indigo-400 mt-1">{eduData.highest_degree_name}</div>
                </div>
                <div className="bg-slate-800/70 p-4 rounded-lg border border-slate-700/60">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Normalized GPA</span>
                  <div className="text-2xl font-bold text-emerald-400 mt-1">
                    {eduData.normalized_gpa_4_scale ? `${eduData.normalized_gpa_4_scale}/4.0` : 'N/A'}
                  </div>
                </div>
                <div className="bg-slate-800/70 p-4 rounded-lg border border-slate-700/60">
                  <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">ATS Education Score</span>
                  <div className="text-2xl font-bold text-sky-400 mt-1">{eduData.ats_education_score}%</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
