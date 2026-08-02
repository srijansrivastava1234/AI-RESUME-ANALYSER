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
        error={error}
      />

      <div className="glass-panel job-desc-input">
        <label htmlFor="job-desc">Target Job Description (Optional)</label>
        <textarea 
          id="job-desc" 
          placeholder="Paste the target job description here to check your compatibility, skills alignment, and discover specific keywords gaps..." 
          value={jobDesc}
          onChange={(e) => setJobDesc(e.target.value)}
        />
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
