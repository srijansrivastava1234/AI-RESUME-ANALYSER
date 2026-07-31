import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Target, 
  Printer
} from 'lucide-react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ScoreCard from './components/ScoreCard';
import CoreParameters from './components/CoreParameters';
import TabsPanel from './components/TabsPanel';
import HelpModal from './components/HelpModal';

const BACKEND_URL = 'http://127.0.0.1:8000';

function App() {
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [jobDesc, setJobDesc] = useState('');
  const [loading, setLoading] = useState(false);
  const [apiOnline, setApiOnline] = useState(false);
  const [report, setReport] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [error, setError] = useState('');
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'dark';
  });
  const [showHelpModal, setShowHelpModal] = useState(false);

  // Apply theme class to body and sync with localStorage
  useEffect(() => {
    document.body.className = theme === 'light' ? 'light-theme' : '';
    localStorage.setItem('theme', theme);
  }, [theme]);

  const [history, setHistory] = useState([]);

  // Load history on mount
  useEffect(() => {
    try {
      const savedHistory = JSON.parse(localStorage.getItem('resume_history') || '[]');
      setHistory(savedHistory);
    } catch (e) {
      console.error(e);
    }
  }, []);

  const saveToHistory = (filename, score, reportData) => {
    try {
      const historyItem = {
        id: Date.now().toString(),
        filename,
        score,
        date: new Date().toLocaleDateString(undefined, { 
          month: 'short', 
          day: 'numeric', 
          hour: '2-digit', 
          minute: '2-digit' 
        }),
        report: reportData
      };
      
      const currentHistory = JSON.parse(localStorage.getItem('resume_history') || '[]');
      const updatedHistory = [historyItem, ...currentHistory].slice(0, 5);
      localStorage.setItem('resume_history', JSON.stringify(updatedHistory));
      setHistory(updatedHistory);
    } catch (e) {
      console.error("Error saving history:", e);
    }
  };

  const loadHistoryItem = (item) => {
    setReport(item.report);
    setActiveTab('overview');
  };

  const clearHistory = () => {
    localStorage.removeItem('resume_history');
    setHistory([]);
  };

  // Check API health status on mount
  useEffect(() => {
    fetch(`${BACKEND_URL}/`)
      .then(res => {
        if (res.ok) setApiOnline(true);
      })
      .catch(() => {
        setApiOnline(false);
      });
  }, []);

  // Handle Drag & Drop
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === "application/pdf") {
        setFile(droppedFile);
        setError('');
      } else {
        setError('Only PDF files are supported.');
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === "application/pdf") {
        setFile(selectedFile);
        setError('');
      } else {
        setError('Only PDF files are supported.');
      }
    }
  };

  const removeFile = () => {
    setFile(null);
    setReport(null);
  };

  // Submit to API
  const analyzeResume = async () => {
    if (!file) {
      setError('Please upload a resume first.');
      return;
    }

    setLoading(true);
    setError('');
    
    const formData = new FormData();
    formData.append('file', file);
    if (jobDesc.trim()) {
      formData.append('job_description', jobDesc);
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to analyze resume.');
      }

      const data = await response.json();
      setReport(data.report);
      setActiveTab('overview');
      saveToHistory(file.name, data.report.ats_score, data.report);
    } catch (err) {
      setError(err.message || 'An error occurred during analysis.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Score styling helpers
  const getScoreColor = (score) => {
    if (score >= 85) return 'var(--success)';
    if (score >= 70) return 'var(--warning)';
    return 'var(--danger)';
  };

  const getScoreBg = (score) => {
    if (score >= 85) return 'var(--success-bg)';
    if (score >= 70) return 'var(--warning-bg)';
    return 'var(--danger-bg)';
  };

  return (
    <div className="app-container">
      <Header
        theme={theme}
        setTheme={setTheme}
        apiOnline={apiOnline}
      />

      {/* Grid */}
      <div className="grid-container">
        <Sidebar
          file={file}
          dragActive={dragActive}
          handleDrag={handleDrag}
          handleDrop={handleDrop}
          handleFileChange={handleFileChange}
          removeFile={removeFile}
          error={error}
          jobDesc={jobDesc}
          setJobDesc={setJobDesc}
          analyzeResume={analyzeResume}
          loading={loading}
          history={history}
          loadHistoryItem={loadHistoryItem}
          clearHistory={clearHistory}
          getScoreColor={getScoreColor}
          getScoreBg={getScoreBg}
        />

        {/* Dashboard Main */}
        <div className="dashboard-main">
          {loading && (
            <div className="glass-panel loading-container">
              <div className="spinner"></div>
              <div style={{ textAlign: 'center' }}>
                <h4 style={{ fontSize: '1.2rem', marginBottom: '0.25rem' }}>Evaluating Resume Structure</h4>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Extracting text, evaluating formatting, and matching requirements using Gemini AI...</p>
              </div>
            </div>
          )}

          {!loading && !report && (
            <div className="glass-panel welcome-placeholder">
              <FileText className="placeholder-icon" style={{ width: '64px', height: '64px' }} />
              <div className="placeholder-text">
                <h3>Ready to Audit Your Resume?</h3>
                <p>Upload your resume in PDF format, enter an optional target job description, and hit 'Analyze' to run a deep scanner on your resume's ATS compliance score.</p>
              </div>
            </div>
          )}

          {!loading && report && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }} className="no-print">
                <button 
                  onClick={() => window.print()} 
                  className="btn-print"
                  style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '0.5rem', 
                    padding: '0.5rem 1rem', 
                    background: 'rgba(255, 255, 255, 0.05)', 
                    border: '1px solid var(--border-color)', 
                    borderRadius: '8px', 
                    color: 'white', 
                    cursor: 'pointer', 
                    fontFamily: 'var(--font-header)', 
                    fontWeight: 600, 
                    fontSize: '0.85rem',
                    transition: 'var(--transition-smooth)'
                  }}
                >
                  <Printer style={{ width: '16px', height: '16px' }} />
                  <span>Export Report / Print PDF</span>
                </button>
              </div>
              
              {/* Job description score header */}
              {report.job_compatibility && (
                <div className="compatibility-box">
                  <div className="compatibility-header">
                    <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.15rem' }}>
                      <Target style={{ color: 'var(--accent)' }} />
                      <span>Job Description Compatibility</span>
                    </h3>
                    <div className="compat-score-wrap">
                      <span className="compat-score-num">{report.job_compatibility.score}%</span>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Match</span>
                    </div>
                  </div>
                  <p className="compat-desc">{report.job_compatibility.match_analysis}</p>
                  
                  {report.job_compatibility.skill_gaps && report.job_compatibility.skill_gaps.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.5rem', marginTop: '0.25rem' }}>
                      <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Key Skill Gaps:</span>
                      {report.job_compatibility.skill_gaps.map((gap, index) => (
                        <span key={index} className="tag missing" style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}>{gap}</span>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Main Scores Row */}
              <div className="dashboard-grid">
                <ScoreCard
                  atsScore={report.ats_score}
                  getScoreColor={getScoreColor}
                  getScoreBg={getScoreBg}
                  setShowHelpModal={setShowHelpModal}
                />

                <CoreParameters
                  metrics={report.metrics}
                  getScoreColor={getScoreColor}
                />
              </div>

              {/* Tab Navigation & Content */}
              <TabsPanel
                report={report}
                activeTab={activeTab}
                setActiveTab={setActiveTab}
              />
            </div>
          )}
        </div>
      </div>

      <HelpModal
        showHelpModal={showHelpModal}
        setShowHelpModal={setShowHelpModal}
      />
    </div>
  );
}

export default App;

