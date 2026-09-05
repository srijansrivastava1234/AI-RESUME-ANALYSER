import React from 'react';
import { ArrowRight } from 'lucide-react';
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
  getScoreBg
}) {
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
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
          <label htmlFor="job-desc" style={{ margin: 0, fontWeight: 600 }}>Target Job Description (Optional)</label>
          {jobDesc.length > 0 && (
            <button
              onClick={() => setJobDesc('')}
              type="button"
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-secondary)',
                fontSize: '0.72rem',
                cursor: 'pointer',
                padding: '0 0.2rem'
              }}
              title="Clear job description"
            >
              Clear
            </button>
          )}
        </div>
        <textarea 
          id="job-desc" 
          placeholder="Paste the target job description here to check your compatibility, skills alignment, and discover specific keywords gaps..." 
          value={jobDesc}
          onChange={(e) => setJobDesc(e.target.value.slice(0, 5000))}
        />
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
