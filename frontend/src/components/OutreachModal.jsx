import {
  Send,
  Mail,
  Briefcase,
  Clock,
  Sparkles,
  Copy,
  Check,
  Download,
  RefreshCw,
  X,
  Building,
  User,
  Zap,
  Flame,
  BrainCircuit,
  MessageSquare
} from 'lucide-react';

const MODES = [
  { id: 'cover_letter', label: 'Tailored Cover Letter', icon: Mail, desc: '200-word Google/IBM XYZ accomplishment letter' },
  { id: 'linkedin_inmail', label: 'LinkedIn InMail / DM', icon: Briefcase, desc: '80-word high-conversion recruiter message' },
  { id: 'cold_email', label: 'Hiring Manager Cold Email', icon: Send, desc: 'Punchy 3-paragraph value proposition' },
  { id: 'follow_up', label: 'Follow-Up Note', icon: Clock, desc: '50-word polite status & momentum check-in' }
];

const TONES = [
  { id: 'confident', label: 'Confident & Bold', icon: Flame, color: '#f59e0b' },
  { id: 'direct', label: 'Direct & Metric-First', icon: Zap, color: '#38bdf8' },
  { id: 'technical', label: 'Deep Technical', icon: BrainCircuit, color: '#34d399' },
  { id: 'executive', label: 'Executive Leadership', icon: Sparkles, color: '#a855f7' }
];

export default function OutreachModal({
  isOpen,
  onClose,
  extractedText,
  jobDesc,
  backendUrl
}) {
  const [mode, setMode] = useState('cover_letter');
  const [tone, setTone] = useState('confident');
  const [recipientName, setRecipientName] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [outreachData, setOutreachData] = useState(null);
  const [editableBody, setEditableBody] = useState('');
  const [editableSubject, setEditableSubject] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copiedSubject, setCopiedSubject] = useState(false);
  const [copiedBody, setCopiedBody] = useState(false);

  const fetchOutreach = async (overrideMode = mode, overrideTone = tone) => {
    if (!extractedText || !extractedText.trim()) return;

    setLoading(true);
    setError('');

    try {
      const res = await fetch(`${backendUrl}/api/generate-outreach`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: extractedText,
          job_description: jobDesc || '',
          mode: overrideMode,
          tone: overrideTone,
          recipient_name: recipientName.trim() || undefined,
          company_name: companyName.trim() || undefined
        })
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      const data = await res.json();
      setOutreachData(data);
      setEditableSubject(data.subject || '');
      setEditableBody(data.body || '');
    } catch (err) {
      console.error('Outreach generation error:', err);
      setError('Failed to generate tailored outreach copy.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen && extractedText) {
      fetchOutreach(mode, tone);
    }
  }, [isOpen, mode, tone]);

  // Handle Close on Escape
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const copySubjectToClipboard = () => {
    navigator.clipboard.writeText(editableSubject);
    setCopiedSubject(true);
    setTimeout(() => setCopiedSubject(false), 2000);
  };

  const copyBodyToClipboard = () => {
    const fullText = editableSubject
      ? `Subject: ${editableSubject}\n\n${editableBody}`
      : editableBody;
    navigator.clipboard.writeText(fullText);
    setCopiedBody(true);
    setTimeout(() => setCopiedBody(false), 2000);
  };

  const downloadAsMarkdown = () => {
    const fullText = editableSubject
      ? `# ${editableSubject}\n\n${editableBody}`
      : editableBody;
    const blob = new Blob([fullText], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${mode}_${tone}.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (!isOpen) return null;

  const currentWordCount = editableBody ? editableBody.trim().split(/\s+/).filter(Boolean).length : 0;
  const currentReadTime = Math.max(10, Math.round((currentWordCount / 220) * 60));

  return (
    <div className="outreach-modal-overlay" onClick={onClose}>
      <div className="outreach-modal-container" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="outreach-modal-header">
          <div className="outreach-header-title-row">
            <div className="outreach-icon-badge">
              <Send size={20} className="text-amber-400" />
            </div>
            <div>
              <h2 className="outreach-modal-title">🚀 Tailored Cover Letter & Cold Outreach Suite</h2>
              <p className="outreach-modal-subtitle">
                Synthesize high-converting application letters and recruiter InMails directly grounded in your verified accomplishments.
              </p>
            </div>
          </div>
          <button className="outreach-close-btn" onClick={onClose} title="Close (Esc)">
            <X size={20} />
          </button>
        </div>

        {/* Mode Selector Tabs */}
        <div className="outreach-modes-grid">
          {MODES.map((m) => {
            const Icon = m.icon;
            const isSelected = mode === m.id;
            return (
              <button
                key={m.id}
                className={`outreach-mode-card ${isSelected ? 'selected' : ''}`}
                onClick={() => setMode(m.id)}
              >
                <div className="mode-card-top">
                  <Icon size={16} className={isSelected ? 'text-primary' : 'text-muted'} />
                  <span className="mode-card-name">{m.label}</span>
                </div>
                <p className="mode-card-desc">{m.desc}</p>
              </button>
            );
          })}
        </div>

        {/* Customization Controls Row */}
        <div className="outreach-controls-bar">
          {/* Tone Selector */}
          <div className="outreach-tone-group">
            <span className="control-label">Voice & Tone:</span>
            <div className="tone-pills-row">
              {TONES.map((t) => {
                const Icon = t.icon;
                const isSelected = tone === t.id;
                return (
                  <button
                    key={t.id}
                    className={`tone-pill ${isSelected ? 'active' : ''}`}
                    onClick={() => setTone(t.id)}
                    style={{ '--tone-color': t.color }}
                  >
                    <Icon size={13} />
                    <span>{t.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Recipient & Company Overrides */}
          <div className="outreach-inputs-row">
            <div className="outreach-input-wrap">
              <User size={13} className="input-icon" />
              <input
                type="text"
                value={recipientName}
                onChange={(e) => setRecipientName(e.target.value)}
                placeholder="Recipient / Recruiter Name (Optional)"
              />
            </div>
            <div className="outreach-input-wrap">
              <Building size={13} className="input-icon" />
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="Target Company Name (Optional)"
              />
            </div>
            <button
              className="refresh-outreach-btn"
              onClick={() => fetchOutreach(mode, tone)}
              disabled={loading}
              title="Re-synthesize copy with current parameters"
            >
              <RefreshCw size={14} className={loading ? 'spin-icon' : ''} />
              <span>{loading ? 'Synthesizing...' : 'Regenerate'}</span>
            </button>
          </div>
        </div>

        {/* Main Content & Editor Body */}
        <div className="outreach-preview-body">
          {loading && !outreachData ? (
            <div className="loading-interview-box">
              <div className="pulse-loader" />
              <p className="loading-text">Synthesizing personalized outreach copy from resume accomplishments...</p>
            </div>
          ) : (
            <>
              {/* Subject Line Bar (if applicable) */}
              {mode !== 'cover_letter' && (
                <div className="subject-line-container">
                  <div className="subject-label-group">
                    <span className="subject-tag">Subject Line</span>
                    <button
                      className="copy-mini-btn"
                      onClick={copySubjectToClipboard}
                      title="Copy subject line only"
                    >
                      {copiedSubject ? <Check size={13} className="text-emerald-400" /> : <Copy size={13} />}
                      <span>{copiedSubject ? 'Copied' : 'Copy'}</span>
                    </button>
                  </div>
                  <input
                    type="text"
                    className="subject-input"
                    value={editableSubject}
                    onChange={(e) => setEditableSubject(e.target.value)}
                    placeholder="Enter subject line..."
                  />
                </div>
              )}

              {/* Message Body Editor */}
              <div className="message-body-wrapper">
                <div className="message-toolbar">
                  <div className="meta-stats-row">
                    <span className="meta-stat-pill">
                      <strong>{currentWordCount}</strong> words
                    </span>
                    <span className="meta-stat-pill">
                      ~<strong>{currentReadTime}s</strong> reading time
                    </span>
                    {outreachData && (
                      <span className={`ai-mode-pill ${outreachData.ai_powered ? 'mode-gemini' : 'mode-heuristic'}`}>
                        {outreachData.ai_powered ? (
                          <>
                            <Sparkles size={12} /> Gemini 2.5 AI Powered
                          </>
                        ) : (
                          <>
                            <Zap size={12} /> Heuristic XYZ Engine
                          </>
                        )}
                      </span>
                    )}
                  </div>
                  <span className="editor-hint">Editable Draft — feel free to tweak directly below</span>
                </div>

                <textarea
                  className="outreach-textarea"
                  rows={12}
                  value={editableBody}
                  onChange={(e) => setEditableBody(e.target.value)}
                  placeholder="Generated message will appear here..."
                />
              </div>
            </>
          )}
        </div>

        {/* Modal Footer Actions */}
        <div className="outreach-modal-footer">
          <div className="footer-left-info">
            <span className="target-pill">
              Target: <strong>{companyName || outreachData?.target_context?.company || 'Target Organization'}</strong>
            </span>
          </div>

          <div className="footer-right-actions">
            <button className="footer-btn-secondary" onClick={downloadAsMarkdown}>
              <Download size={14} /> Download .MD
            </button>
            <button className="footer-btn-primary" onClick={copyBodyToClipboard}>
              {copiedBody ? <Check size={14} /> : <Copy size={14} />}
              {copiedBody ? 'Copied to Clipboard!' : 'Copy Complete Message'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
