import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Target, 
  Printer,
  Copy,
  Check,
  Download,
  Eye,
  Send,
  CheckCircle2,
  Zap
} from 'lucide-react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ScoreCard from './components/ScoreCard';
import CoreParameters from './components/CoreParameters';
import TabsPanel from './components/TabsPanel';

// Lazy-loaded secondary panels & modals for optimized bundle splitting
const HelpModal = React.lazy(() => import('./components/HelpModal'));
const ComparePanel = React.lazy(() => import('./components/ComparePanel'));
const BulletImpactLab = React.lazy(() => import('./components/BulletImpactLab'));
const PdfVisualStudio = React.lazy(() => import('./components/PdfVisualStudio'));
const OutreachModal = React.lazy(() => import('./components/OutreachModal'));


// Dynamically resolve backend URL. If VITE_API_URL env variable is provided, use it.
// Otherwise, fall back to using the current page hostname with port 8000.
// This allows other devices on the network to connect without code changes.
const BACKEND_URL = import.meta.env.VITE_API_URL || `${window.location.protocol}//${window.location.hostname}:8000`;


function App() {
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [jobDesc, setJobDesc] = useState('');
  const [loading, setLoading] = useState(false);
  const [apiOnline, setApiOnline] = useState(false);
  const [report, setReport] = useState(null);
  const [extractedText, setExtractedText] = useState('');
  const [editedText, setEditedText] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [error, setError] = useState('');
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'dark';
  });
  const [showHelpModal, setShowHelpModal] = useState(false);
  const [showPdfStudio, setShowPdfStudio] = useState(false);
  const [showOutreachModal, setShowOutreachModal] = useState(false);
  const [copiedReport, setCopiedReport] = useState(false);
  const [appMode, setAppMode] = useState('audit');

  // Apply theme class to body and sync with localStorage
  useEffect(() => {
    document.body.className = theme === 'dark' ? '' : `${theme}-theme`;
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Keyboard shortcut listener: Ctrl+Enter or Cmd+Enter to run analysis
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (file && !loading) {
          e.preventDefault();
          analyzeResume();
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [file, loading, jobDesc]);

  const copyMarkdownReport = () => {
    if (!report) return;
    const detectedKws = report.keywords?.detected?.join(', ') || 'None';
    const missingKws = report.keywords?.missing?.join(', ') || 'None';
    
    let md = `# ATS Resume Analysis Report - ${file?.name || 'Resume'}\n\n`;
    md += `**ATS Score:** ${report.ats_score}/100\n\n`;
    if (report.job_compatibility) {
      md += `## Job Description Compatibility\n`;
      md += `* **Match Score:** ${report.job_compatibility.score}%\n`;
      md += `* **Analysis:** ${report.job_compatibility.match_analysis}\n`;
      if (report.job_compatibility.skill_gaps?.length) {
        md += `* **Skill Gaps:** ${report.job_compatibility.skill_gaps.join(', ')}\n`;
      }
      md += `\n`;
    }
    
    md += `## Core Metrics\n`;
    report.metrics?.forEach(m => {
      md += `* **${m.name}:** ${m.score}/100 - ${m.feedback}\n`;
    });
    md += `\n`;
    
    md += `## Key Strengths\n`;
    report.key_strengths?.forEach(str => {
      md += `* ✓ ${str}\n`;
    });
    md += `\n`;
    
    md += `## Actionable Recommendations\n`;
    report.actionable_recommendations?.forEach((rec, idx) => {
      md += `### Recommendation ${idx + 1}: ${rec.issue} (${rec.priority} Priority)\n`;
      md += `* **Advice:** ${rec.recommendation}\n`;
      md += `* **Before:** \`${rec.before_after?.before}\`\n`;
      md += `* **After:** \`${rec.before_after?.after}\`\n\n`;
    });
    
    md += `## Keywords Analysis\n`;
    md += `* **Detected Keywords:** ${detectedKws}\n`;
    md += `* **Missing Keywords:** ${missingKws}\n`;
    
    navigator.clipboard.writeText(md);
    setCopiedReport(true);
    setTimeout(() => setCopiedReport(false), 2000);
  };

  const downloadJSONReport = () => {
    if (!report) return;
    const exportData = {
      filename: file?.name || 'resume_analysis',
      generated_at: new Date().toISOString(),
      ats_score: report.ats_score,
      report,
      extracted_text: extractedText
    };
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${(file?.name || 'resume').replace(/\.[^/.]+$/, "")}_ats_report.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadTxtReport = () => {
    if (!report) return;
    let txt = `====================================================\n`;
    txt += `          ATS RESUME ANALYSIS REPORT                \n`;
    txt += `====================================================\n\n`;
    txt += `File Name: ${file?.name || 'Resume'}\n`;
    txt += `ATS Score: ${report.ats_score}/100\n\n`;
    if (report.job_compatibility) {
      txt += `[JOB COMPATIBILITY]\n`;
      txt += `Match Score: ${report.job_compatibility.score}%\n`;
      txt += `Analysis: ${report.job_compatibility.match_analysis}\n\n`;
    }
    txt += `[CORE METRICS]\n`;
    report.metrics?.forEach(m => {
      txt += `• ${m.name}: ${m.score}/100 - ${m.feedback}\n`;
    });
    txt += `\n[KEY STRENGTHS]\n`;
    report.key_strengths?.forEach(s => {
      txt += `• ${s}\n`;
    });
    txt += `\n[KEYWORDS]\n`;
    txt += `Detected: ${report.keywords?.detected?.join(', ') || 'None'}\n`;
    txt += `Missing:  ${report.keywords?.missing?.join(', ') || 'None'}\n`;
    
    const blob = new Blob([txt], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${(file?.name || 'resume').replace(/\.[^/.]+$/, "")}_ats_summary.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

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

  const saveToHistory = (filename, score, reportData, extractedTextData) => {
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
        report: reportData,
        extractedText: extractedTextData
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
    setExtractedText(item.extractedText || '');
    setEditedText(item.extractedText || '');
    setActiveTab('overview');
  };

  const clearHistory = () => {
    localStorage.removeItem('resume_history');
    setHistory([]);
  };

  const deleteHistoryItem = (id, e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    try {
      const currentHistory = JSON.parse(localStorage.getItem('resume_history') || '[]');
      const updatedHistory = currentHistory.filter(item => item.id !== id);
      localStorage.setItem('resume_history', JSON.stringify(updatedHistory));
      setHistory(updatedHistory);
    } catch (err) {
      console.error("Error deleting history item:", err);
    }
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
      const name = droppedFile.name.toLowerCase();
      if (name.endsWith(".pdf") || name.endsWith(".docx") || name.endsWith(".txt")) {
        setFile(droppedFile);
        setError('');
      } else {
        setError('Only PDF, DOCX, and TXT files are supported.');
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      const name = selectedFile.name.toLowerCase();
      if (name.endsWith(".pdf") || name.endsWith(".docx") || name.endsWith(".txt")) {
        setFile(selectedFile);
        setError('');
      } else {
        setError('Only PDF, DOCX, and TXT files are supported.');
      }
    }
  };

  const loadSampleResume = () => {
    const sampleText = `Alex Mercer
Senior Full Stack Engineer | San Francisco, CA | alex.mercer@email.com | (555) 019-2834

PROFESSIONAL SUMMARY
Results-driven Senior Full Stack Software Engineer with 6+ years of experience designing, scaling, and deploying mission-critical distributed systems. Proven track record in microservice architectures, API latency reduction, and cloud infrastructure optimization.

TECHNICAL SKILLS
- Languages: Python, TypeScript, JavaScript, SQL, HTML5, CSS3, Go
- Frameworks & Libraries: React, FastAPI, Node.js, Next.js, Express, Redux, TailwindCSS
- Cloud & DevOps: AWS (EC2, S3, RDS, Lambda), Docker, Kubernetes, CI/CD (GitHub Actions), Terraform, Linux
- Databases: PostgreSQL, Redis, MongoDB, MySQL
- Methodologies: Agile / Scrum, TDD, RESTful APIs, Microservices, System Design

WORK EXPERIENCE
Senior Software Engineer | CloudScale Tech | 2022 – Present
• Architected and deployed high-throughput microservices using FastAPI and PostgreSQL, reducing endpoint p99 latency by 42% for 2.5M daily active users.
• Spearheaded containerization initiative with Docker and Kubernetes on AWS EKS, cutting deployment overhead by 65% and achieving 99.99% system availability.
• Engineered real-time event-driven data streaming pipeline with Redis and WebSockets, processing 50k events/second with zero packet drop.
• Mentored 5 junior and mid-level software engineers on code review standards, modern testing methodologies, and architectural design patterns.

Full Stack Developer | Nexa Innovations | 2019 – 2022
• Developed responsive web applications using React and TypeScript, boosting candidate conversion rates by 28%.
• Implemented automated CI/CD deployment pipelines with GitHub Actions, reducing release cycle time from 2 weeks to daily automated deployments.
• Optimized relational database queries and indexed slow schemas in PostgreSQL, resulting in a 35% query performance improvement.

EDUCATION
Bachelor of Science in Computer Science | University of California, Berkeley | 2015 – 2019
`;
    const sampleFile = new File([sampleText], "sample_software_engineer_resume.txt", { type: "text/plain" });
    setFile(sampleFile);
    setError("");
    if (!jobDesc) {
      setJobDesc("We are seeking a Senior Full Stack Engineer proficient in Python, FastAPI, React, Docker, and AWS to architect high-performance distributed systems.");
    }
  };

  const removeFile = () => {
    setFile(null);
    setReport(null);
    setExtractedText('');
    setEditedText('');
    setError('');
  };// Submit to API
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
      setExtractedText(data.extracted_text || '');
      setEditedText(data.extracted_text || '');
      setActiveTab('overview');
      saveToHistory(file.name, data.report.ats_score, data.report, data.extracted_text || '');
    } catch (err) {
      setError(err.message || 'An error occurred during analysis.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Submit edited sandbox text to API
  const analyzeSandboxText = async () => {
    if (!editedText.trim()) {
      setError('Sandbox draft is empty.');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const textBlob = new Blob([editedText], { type: 'text/plain' });
      const textFile = new File([textBlob], file?.name || 'resume.txt', { type: 'text/plain' });
      
      const formData = new FormData();
      formData.append('file', textFile);
      if (jobDesc.trim()) {
        formData.append('job_description', jobDesc);
      }

      const response = await fetch(`${BACKEND_URL}/api/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to analyze sandbox draft.');
      }

      const data = await response.json();
      setReport(data.report);
      setExtractedText(data.extracted_text || '');
      setEditedText(data.extracted_text || '');
      setActiveTab('overview');
      saveToHistory(`[Draft] ${file?.name || 'resume.txt'}`, data.report.ats_score, data.report, data.extracted_text || '');
    } catch (err) {
      setError(err.message || 'An error occurred during sandbox analysis.');
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
        setShowHelpModal={setShowHelpModal}
        appMode={appMode}
        setAppMode={setAppMode}
      />

      {appMode === 'compare' ? (
        <div style={{ maxWidth: '1200px', margin: '0 auto', width: '100%', padding: '0 1rem 2rem 1rem' }}>
          <React.Suspense fallback={<div className="glass-panel" style={{ padding: '2rem', textAlign: 'center' }}>Loading Comparison Studio...</div>}>
            <ComparePanel
              backendUrl={BACKEND_URL}
              getScoreColor={getScoreColor}
              getScoreBg={getScoreBg}
            />
          </React.Suspense>
        </div>
      ) : appMode === 'xyz' ? (
        <div style={{ maxWidth: '1200px', margin: '0 auto', width: '100%', padding: '0 1rem 2rem 1rem' }}>
          <React.Suspense fallback={<div className="glass-panel" style={{ padding: '2rem', textAlign: 'center' }}>Loading Bullet Impact Lab...</div>}>
            <BulletImpactLab
              backendUrl={BACKEND_URL}
            />
          </React.Suspense>
        </div>
      ) : (
      /* Grid */
      <div className="grid-container">
        <Sidebar
          file={file}
          dragActive={dragActive}
          handleDrag={handleDrag}
          handleDrop={handleDrop}
          handleFileChange={handleFileChange}
          removeFile={removeFile}
          loadSampleResume={loadSampleResume}
          error={error}
          jobDesc={jobDesc}
          setJobDesc={setJobDesc}
          analyzeResume={analyzeResume}
          loading={loading}
          history={history}
          loadHistoryItem={loadHistoryItem}
          clearHistory={clearHistory}
          deleteHistoryItem={deleteHistoryItem}
          getScoreColor={getScoreColor}
          getScoreBg={getScoreBg}
          backendUrl={BACKEND_URL}
        />

        {/* Dashboard Main */}
        <div className="dashboard-main">
          {loading && (
            <div className="glass-panel loading-container">
              <div className="loading-radar-ring">
                <div className="spinner"></div>
              </div>
              <div style={{ textAlign: 'center', maxWidth: '440px' }}>
                <h4 style={{ fontSize: '1.25rem', marginBottom: '0.35rem', fontWeight: 700 }}>Evaluating Resume Structure</h4>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: 1.5, marginBottom: '1.25rem' }}>
                  Extracting text, evaluating formatting, and matching requirements using Gemini AI...
                </p>
                
                <div className="loading-steps-list">
                  <div className="loading-step-item active">
                    <span className="step-dot"></span>
                    <span>Extracting PDF text tokens & layout hierarchy</span>
                  </div>
                  <div className="loading-step-item">
                    <span className="step-dot"></span>
                    <span>Benchmarking ATS parsing compliance (Workday/Taleo)</span>
                  </div>
                  <div className="loading-step-item">
                    <span className="step-dot"></span>
                    <span>Computing semantic keyword & skill gap vectors</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {!loading && !report && (
            <div className="glass-panel welcome-placeholder">
              <div className="welcome-hero-badge">
                <span className="welcome-badge-dot"></span>
                <span>Next-Gen Enterprise ATS Auditor</span>
              </div>

              <div className="placeholder-text">
                <h3>Ready to Audit Your Resume?</h3>
                <p>
                  Upload your resume in PDF, DOCX, or TXT format, enter an optional target job description, and hit 'Analyze' to run a deep scanner on your resume's ATS compliance score.
                </p>
              </div>

              {/* Feature Preview Grid */}
              <div className="welcome-feature-grid">
                <div className="welcome-feature-card">
                  <div className="welcome-feature-icon" style={{ background: 'rgba(37, 99, 235, 0.12)', color: '#38bdf8' }}>
                    <CheckCircle2 size={20} />
                  </div>
                  <h4>Multi-Engine Simulation</h4>
                  <p>Benchmark parsing compatibility across Workday, Taleo, and Greenhouse ATS algorithms.</p>
                  <span className="feature-pill">3 Engines</span>
                </div>

                <div className="welcome-feature-card">
                  <div className="welcome-feature-icon" style={{ background: 'rgba(16, 185, 129, 0.12)', color: '#34d399' }}>
                    <Target size={20} />
                  </div>
                  <h4>Keyword Gap Matrix</h4>
                  <p>Instantly uncover missing hard skills, certifications, and high-frequency role keywords.</p>
                  <span className="feature-pill" style={{ color: '#34d399', borderColor: 'rgba(16, 185, 129, 0.25)' }}>Skill Matrix</span>
                </div>

                <div className="welcome-feature-card">
                  <div className="welcome-feature-icon" style={{ background: 'rgba(245, 158, 11, 0.12)', color: '#fbbf24' }}>
                    <Zap size={20} />
                  </div>
                  <h4>XYZ Impact Lab</h4>
                  <p>Turn passive job duties into quantifiable achievements using the Google XYZ formula.</p>
                  <span className="feature-pill" style={{ color: '#fbbf24', borderColor: 'rgba(245, 158, 11, 0.25)' }}>Metric Diffs</span>
                </div>
              </div>

              {/* Workflow Timeline */}
              <div className="welcome-workflow-strip">
                <div className="workflow-step">
                  <span className="workflow-num">01</span>
                  <div>
                    <p className="workflow-title">Drop Resume</p>
                    <span className="workflow-desc">PDF, DOCX, TXT</span>
                  </div>
                </div>
                <div className="workflow-arrow">→</div>
                <div className="workflow-step">
                  <span className="workflow-num">02</span>
                  <div>
                    <p className="workflow-title">Target Job Spec</p>
                    <span className="workflow-desc">Paste or 1-click URL</span>
                  </div>
                </div>
                <div className="workflow-arrow">→</div>
                <div className="workflow-step">
                  <span className="workflow-num">03</span>
                  <div>
                    <p className="workflow-title">Instant ATS Audit</p>
                    <span className="workflow-desc">Deep Diagnostics</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {!loading && report && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', flexWrap: 'wrap' }} className="no-print">
                <button 
                  onClick={copyMarkdownReport} 
                  className="btn-print"
                  style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '0.4rem', 
                    padding: '0.45rem 0.85rem', 
                    background: 'rgba(255, 255, 255, 0.05)', 
                    border: '1px solid var(--border-color)', 
                    borderRadius: '8px', 
                    color: 'white', 
                    cursor: 'pointer', 
                    fontFamily: 'var(--font-header)', 
                    fontWeight: 600, 
                    fontSize: '0.8rem',
                    transition: 'var(--transition-smooth)'
                  }}
                  title="Copy the entire report as formatted Markdown"
                >
                  {copiedReport ? <Check style={{ width: '15px', height: '15px', color: 'var(--success)' }} /> : <Copy style={{ width: '15px', height: '15px' }} />}
                  <span>{copiedReport ? 'Report Copied!' : 'Copy Markdown'}</span>
                </button>
                <button 
                  onClick={downloadJSONReport} 
                  className="btn-print"
                  style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '0.4rem', 
                    padding: '0.45rem 0.85rem', 
                    background: 'rgba(255, 255, 255, 0.05)', 
                    border: '1px solid var(--border-color)', 
                    borderRadius: '8px', 
                    color: 'white', 
                    cursor: 'pointer', 
                    fontFamily: 'var(--font-header)', 
                    fontWeight: 600, 
                    fontSize: '0.8rem',
                    transition: 'var(--transition-smooth)'
                  }}
                  title="Download full analysis payload as structured JSON"
                >
                  <Download style={{ width: '15px', height: '15px' }} />
                  <span>Download JSON</span>
                </button>
                <button 
                  onClick={downloadTxtReport} 
                  className="btn-print"
                  style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '0.4rem', 
                    padding: '0.45rem 0.85rem', 
                    background: 'rgba(255, 255, 255, 0.05)', 
                    border: '1px solid var(--border-color)', 
                    borderRadius: '8px', 
                    color: 'white', 
                    cursor: 'pointer', 
                    fontFamily: 'var(--font-header)', 
                    fontWeight: 600, 
                    fontSize: '0.8rem',
                    transition: 'var(--transition-smooth)'
                  }}
                  title="Download clean plain-text summary"
                >
                  <FileText style={{ width: '15px', height: '15px' }} />
                  <span>Summary TXT</span>
                </button>
                <button 
                  onClick={() => setShowPdfStudio(true)} 
                  className="btn-print"
                  style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '0.4rem', 
                    padding: '0.45rem 0.85rem', 
                    background: 'rgba(56, 189, 248, 0.08)', 
                    border: '1px solid rgba(56, 189, 248, 0.25)', 
                    borderRadius: '8px', 
                    color: '#38bdf8', 
                    cursor: 'pointer', 
                    fontFamily: 'var(--font-header)', 
                    fontWeight: 600, 
                    fontSize: '0.8rem',
                    transition: 'var(--transition-smooth)'
                  }}
                  title="Open Visual Eye-Tracking & ATS Bounding-Box Studio"
                >
                  <Eye style={{ width: '15px', height: '15px' }} />
                  <span>Visual Gaze & Heatmap</span>
                </button>
                <button 
                  onClick={() => setShowOutreachModal(true)} 
                  className="btn-print"
                  style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '0.4rem', 
                    padding: '0.45rem 0.85rem', 
                    background: 'rgba(245, 158, 11, 0.08)', 
                    border: '1px solid rgba(245, 158, 11, 0.25)', 
                    borderRadius: '8px', 
                    color: '#fbbf24', 
                    cursor: 'pointer', 
                    fontFamily: 'var(--font-header)', 
                    fontWeight: 600, 
                    fontSize: '0.8rem',
                    transition: 'var(--transition-smooth)'
                  }}
                  title="Generate Tailored Cover Letter, InMail & Cold Outreach"
                >
                  <Send style={{ width: '15px', height: '15px' }} />
                  <span>Outreach & Cover Letter</span>
                </button>
                <button 
                  onClick={() => window.print()} 
                  className="btn-print"
                  style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '0.4rem', 
                    padding: '0.45rem 0.85rem', 
                    background: 'rgba(255, 255, 255, 0.05)', 
                    border: '1px solid var(--border-color)', 
                    borderRadius: '8px', 
                    color: 'white', 
                    cursor: 'pointer', 
                    fontFamily: 'var(--font-header)', 
                    fontWeight: 600, 
                    fontSize: '0.8rem',
                    transition: 'var(--transition-smooth)'
                  }}
                >
                  <Printer style={{ width: '15px', height: '15px' }} />
                  <span>Print PDF</span>
                </button>
              </div>
              
              {/* Executive Metric Scores Hero Grid (Symmetrical 3-Card Header) */}
              <div className="dashboard-metrics-grid">
                <ScoreCard
                  atsScore={report.ats_score}
                  getScoreColor={getScoreColor}
                  getScoreBg={getScoreBg}
                  setShowHelpModal={setShowHelpModal}
                />

                {report.job_compatibility ? (
                  <div className="glass-panel compatibility-card">
                    <div className="compatibility-header">
                      <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.05rem', fontWeight: 600, margin: 0 }}>
                        <Target style={{ color: 'var(--accent)', width: '18px', height: '18px' }} />
                        <span>Role Compatibility</span>
                      </h4>
                      <div className="compat-score-pill" style={{ background: getScoreBg(report.job_compatibility.score) }}>
                        <span className="compat-score-num" style={{ color: getScoreColor(report.job_compatibility.score) }}>
                          {report.job_compatibility.score}%
                        </span>
                        <span className="compat-score-tag">Match</span>
                      </div>
                    </div>
                    <p className="compat-desc">{report.job_compatibility.match_analysis}</p>
                    
                    {report.job_compatibility.skill_gaps && report.job_compatibility.skill_gaps.length > 0 ? (
                      <div className="compat-gaps-section">
                        <span className="compat-gaps-title">
                          Missing Role Keywords ({report.job_compatibility.skill_gaps.length}):
                        </span>
                        <div className="compat-gaps-list">
                          {report.job_compatibility.skill_gaps.map((gap, index) => (
                            <span key={index} className="tag missing" style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}>{gap}</span>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="compat-gaps-section">
                        <span className="compat-gaps-title" style={{ color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <CheckCircle2 style={{ width: '14px', height: '14px' }} />
                          All Core Skills Present
                        </span>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="glass-panel compatibility-card compatibility-placeholder">
                    <div className="compatibility-header">
                      <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.05rem', fontWeight: 600, margin: 0 }}>
                        <Target style={{ color: 'var(--text-muted)', width: '18px', height: '18px' }} />
                        <span>Role Compatibility</span>
                      </h4>
                      <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', background: 'rgba(255, 255, 255, 0.05)', padding: '2px 8px', borderRadius: '10px' }}>
                        Optional
                      </span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', flex: 1, padding: '1rem 0', gap: '0.5rem' }}>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>
                        No job description attached.
                      </p>
                      <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4, maxWidth: '280px' }}>
                        Paste a target job description in the left sidebar to unlock role matching and keyword gap analysis.
                      </p>
                    </div>
                  </div>
                )}

                <CoreParameters
                  metrics={report.metrics}
                  getScoreColor={getScoreColor}
                />
              </div>

              {/* Tab Navigation & Content */}
              <TabsPanel
                report={report}
                extractedText={extractedText}
                jobDesc={jobDesc}
                editedText={editedText}
                setEditedText={setEditedText}
                analyzeSandboxText={analyzeSandboxText}
                activeTab={activeTab}
                setActiveTab={setActiveTab}
                loading={loading}
                backendUrl={BACKEND_URL}
              />
            </div>
          )}
        </div>
      </div>
      )}

      <React.Suspense fallback={null}>
        {showHelpModal && (
          <HelpModal
            showHelpModal={showHelpModal}
            setShowHelpModal={setShowHelpModal}
          />
        )}

        {file && showPdfStudio && (
          <PdfVisualStudio
            file={file}
            backendUrl={BACKEND_URL}
            isOpen={showPdfStudio}
            onClose={() => setShowPdfStudio(false)}
          />
        )}

        {showOutreachModal && (
          <OutreachModal
            isOpen={showOutreachModal}
            onClose={() => setShowOutreachModal(false)}
            extractedText={extractedText}
            jobDesc={jobDesc}
            backendUrl={BACKEND_URL}
          />
        )}
      </React.Suspense>
    </div>
  );
}

export default App;

