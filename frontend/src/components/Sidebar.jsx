import React, { useState } from 'react';
import { 
  ArrowRight, 
  Link as LinkIcon, 
  FileText, 
  Globe, 
  Sparkles, 
  AlertCircle, 
  CheckCircle2, 
  Loader2,
  Building2,
  Briefcase
} from 'lucide-react';
import Dropzone from './Dropzone';
import HistoryPanel from './HistoryPanel';

export default function Sidebar({
  file,
  dragActive,
  handleDrag,
  handleDrop,
  handleFileChange,
  removeFile,
  loadSampleResume,
  error,
  jobDesc,
  setJobDesc,
  analyzeResume,
  loading,
  history,
  loadHistoryItem,
  clearHistory,
  deleteHistoryItem,
  getScoreColor,
  getScoreBg,
  backendUrl
}) {
  const [jdMode, setJdMode] = useState('paste'); // 'paste' | 'url'
  const [jobUrl, setJobUrl] = useState('');
  const [scraping, setScraping] = useState(false);
  const [scrapeError, setScrapeError] = useState('');
  const [scrapedMeta, setScrapedMeta] = useState(null);

  const handleScrapeUrl = async (e) => {
    if (e) e.preventDefault();
    if (!jobUrl || !jobUrl.trim()) return;

    setScraping(true);
    setScrapeError('');
    setScrapedMeta(null);

    try {
      const res = await fetch(`${backendUrl}/api/scrape-jd`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: jobUrl.trim() })
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to import job description from URL.');
      }

      if (data.cleaned_description) {
        setJobDesc(data.cleaned_description);
        setScrapedMeta({
          job_title: data.job_title,
          company: data.company,
          skills: data.extracted_skills || [],
          domain: data.domain
        });
      } else {
        throw new Error('No readable job text could be extracted from this page.');
      }
    } catch (err) {
      setScrapeError(err.message || 'Error connecting to job URL.');
    } finally {
      setScraping(false);
    }
  };

  const clearJobDesc = () => {
    setJobDesc('');
    setScrapedMeta(null);
    setJobUrl('');
    setScrapeError('');
  };

  return (
    <div className="input-sidebar">
      <Dropzone
        file={file}
        dragActive={dragActive}
        handleDrag={handleDrag}
        handleDrop={handleDrop}
        handleFileChange={handleFileChange}
        removeFile={removeFile}
        loadSampleResume={loadSampleResume}
        error={error}
      />

      <div className="glass-panel job-desc-input">
        {/* Header & Mode Switcher */}
        <div className="jd-header-block">
          <label htmlFor="job-desc" style={{ margin: 0, fontWeight: 600 }}>
            Target Job Description (Optional)
          </label>

          <div className="jd-mode-tabs">
            <button
              type="button"
              className={`jd-mode-tab ${jdMode === 'paste' ? 'active' : ''}`}
              onClick={() => setJdMode('paste')}
              title="Paste job description text directly"
            >
              <FileText size={12} />
              <span>Paste</span>
            </button>
            <button
              type="button"
              className={`jd-mode-tab ${jdMode === 'url' ? 'active' : ''}`}
              onClick={() => setJdMode('url')}
              title="Import directly from Greenhouse, Lever, LinkedIn, Ashby, or Indeed URL"
            >
              <LinkIcon size={12} />
              <span>URL</span>
            </button>
          </div>
        </div>

        {/* URL Import Input Bar */}
        {jdMode === 'url' && (
          <div className="jd-url-importer">
            <div className="jd-url-input-wrap">
              <Globe size={14} className="jd-url-icon" />
              <input
                type="url"
                placeholder="https://boards.greenhouse.io/company/jobs/..."
                value={jobUrl}
                onChange={(e) => setJobUrl(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleScrapeUrl();
                  }
                }}
                className="jd-url-input"
                disabled={scraping}
              />
              <button
                type="button"
                className="jd-fetch-btn"
                onClick={handleScrapeUrl}
                disabled={scraping || !jobUrl.trim()}
              >
                {scraping ? (
                  <>
                    <Loader2 size={13} className="spin" />
                    <span>Scraping...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={13} />
                    <span>Import</span>
                  </>
                )}
              </button>
            </div>

            {scrapeError && (
              <div className="jd-scrape-error">
                <AlertCircle size={13} />
                <span>{scrapeError}</span>
              </div>
            )}

            <div className="jd-url-portals-hint">
              Supported: Greenhouse, Lever, LinkedIn, Ashby, Indeed, & generic careers pages
            </div>
          </div>
        )}

        {/* Extracted Metadata Badge */}
        {scrapedMeta && (
          <div className="jd-scraped-meta-card">
            <div className="meta-card-header">
              <div className="meta-card-title">
                <Briefcase size={13} className="text-cyan-400" />
                <span className="font-semibold">{scrapedMeta.job_title || 'Target Role'}</span>
              </div>
              {scrapedMeta.company && (
                <div className="meta-card-company">
                  <Building2 size={12} />
                  <span>{scrapedMeta.company}</span>
                </div>
              )}
            </div>

            {scrapedMeta.skills && scrapedMeta.skills.length > 0 && (
              <div className="meta-skills-list">
                {scrapedMeta.skills.slice(0, 6).map((skill, i) => (
                  <span key={i} className="meta-skill-tag">{skill}</span>
                ))}
                {scrapedMeta.skills.length > 6 && (
                  <span className="meta-skill-more">+{scrapedMeta.skills.length - 6} more</span>
                )}
              </div>
            )}
          </div>
        )}

        {/* Main Textarea */}
        <div style={{ position: 'relative' }}>
          <textarea 
            id="job-desc" 
            placeholder="Paste the target job description here or import via URL to check compatibility, skills alignment, and discover specific keywords gaps..." 
            value={jobDesc}
            onChange={(e) => setJobDesc(e.target.value.slice(0, 5000))}
          />
          {jobDesc.length > 0 && (
            <button
              onClick={clearJobDesc}
              type="button"
              className="jd-clear-float-btn"
              title="Clear job description"
            >
              Clear
            </button>
          )}
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '-0.25rem', marginBottom: '0.75rem' }}>
          <span>{jobDesc.trim() ? jobDesc.trim().split(/\s+/).length : 0} words</span>
          <span>{jobDesc.length} / 5000 chars</span>
        </div>

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
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: '0.5rem' }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', opacity: 0.8 }}>
            💡 Tip: Press <kbd style={{ background: 'rgba(255,255,255,0.08)', padding: '1px 5px', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.15)' }}>Ctrl</kbd> + <kbd style={{ background: 'rgba(255,255,255,0.08)', padding: '1px 5px', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.15)' }}>Enter</kbd> to analyze
          </span>
        </div>
      </div>

      <HistoryPanel
        history={history}
        loadHistoryItem={loadHistoryItem}
        clearHistory={clearHistory}
        deleteHistoryItem={deleteHistoryItem}
        getScoreColor={getScoreColor}
        getScoreBg={getScoreBg}
      />
    </div>
  );
}
