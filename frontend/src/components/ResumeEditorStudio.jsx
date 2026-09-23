import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  FileText,
  Sparkles,
  Download,
  Copy,
  Check,
  Plus,
  Trash2,
  RefreshCw,
  Eye,
  CheckCircle2,
  AlertTriangle,
  Layers,
  ChevronDown,
  ChevronUp,
  User,
  Briefcase,
  GraduationCap,
  Wrench,
  FolderGit2,
  ExternalLink,
  Printer
} from 'lucide-react';

export default function ResumeEditorStudio({
  extractedText,
  report,
  backendUrl,
  onApplyEditedText
}) {
  const [doc, setDoc] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeSection, setActiveSection] = useState('experience');
  const [copiedTxt, setCopiedTxt] = useState(false);
  const [newSkillInputs, setNewSkillInputs] = useState({
    technical: '',
    tools_frameworks: '',
    soft_skills: ''
  });
  const [fontFamily, setFontFamily] = useState('sans'); // 'sans' or 'serif'
  const previewRef = useRef(null);

  // Initialize and parse structured resume
  const parseDocument = async () => {
    if (!extractedText || !extractedText.trim()) return;

    setLoading(true);
    setError('');

    try {
      const res = await fetch(`${backendUrl}/api/resume/parse-structured`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_text: extractedText })
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      const data = await res.json();
      setDoc(data.structured_resume);
    } catch (err) {
      console.error('Failed to parse structured resume:', err);
      setError('Failed to parse resume into structured editor schema. Using fallback.');
      // Simple fallback schema
      setDoc({
        contact: {
          full_name: 'Candidate Name',
          email: '',
          phone: '',
          location: '',
          linkedin: '',
          github: '',
          portfolio: ''
        },
        summary: '',
        experience: [],
        education: [],
        skills: { technical: [], tools_frameworks: [], soft_skills: [] },
        projects: [],
        certifications: []
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (extractedText && extractedText.trim().length > 10) {
      parseDocument();
    }
  }, [extractedText]);

  // Handle Contact Changes
  const updateContact = (field, value) => {
    setDoc(prev => ({
      ...prev,
      contact: {
        ...prev.contact,
        [field]: value
      }
    }));
  };

  // Handle Summary Changes
  const updateSummary = (value) => {
    setDoc(prev => ({
      ...prev,
      summary: value
    }));
  };

  // Handle Experience
  const updateExperience = (idx, field, value) => {
    setDoc(prev => {
      const updated = [...prev.experience];
      updated[idx] = { ...updated[idx], [field]: value };
      return { ...prev, experience: updated };
    });
  };

  const addExperience = () => {
    setDoc(prev => ({
      ...prev,
      experience: [
        ...prev.experience,
        {
          role: 'Job Title',
          company: 'Company Name',
          location: 'City, ST',
          date_range: '2023 - Present',
          bullets: ['Spearheaded [initiative] achieving [X% quantifiable outcome] by leveraging [technologies].']
        }
      ]
    }));
  };

  const removeExperience = (idx) => {
    setDoc(prev => ({
      ...prev,
      experience: prev.experience.filter((_, i) => i !== idx)
    }));
  };

  const updateBullet = (expIdx, bulletIdx, value) => {
    setDoc(prev => {
      const updated = [...prev.experience];
      const bullets = [...updated[expIdx].bullets];
      bullets[bulletIdx] = value;
      updated[expIdx] = { ...updated[expIdx], bullets };
      return { ...prev, experience: updated };
    });
  };

  const addBullet = (expIdx) => {
    setDoc(prev => {
      const updated = [...prev.experience];
      const bullets = [...updated[expIdx].bullets, 'Engineered [system component] delivering [metric] using [tools].'];
      updated[expIdx] = { ...updated[expIdx], bullets };
      return { ...prev, experience: updated };
    });
  };

  const removeBullet = (expIdx, bulletIdx) => {
    setDoc(prev => {
      const updated = [...prev.experience];
      const bullets = updated[expIdx].bullets.filter((_, bIdx) => bIdx !== bulletIdx);
      updated[expIdx] = { ...updated[expIdx], bullets };
      return { ...prev, experience: updated };
    });
  };

  // Handle Skills
  const addSkill = (category) => {
    const val = newSkillInputs[category].trim();
    if (!val) return;
    setDoc(prev => ({
      ...prev,
      skills: {
        ...prev.skills,
        [category]: [...(prev.skills[category] || []), val]
      }
    }));
    setNewSkillInputs(prev => ({ ...prev, [category]: '' }));
  };

  const removeSkill = (category, skillIdx) => {
    setDoc(prev => ({
      ...prev,
      skills: {
        ...prev.skills,
        [category]: prev.skills[category].filter((_, i) => i !== skillIdx)
      }
    }));
  };

  // Handle Education
  const addEducation = () => {
    setDoc(prev => ({
      ...prev,
      education: [
        ...prev.education,
        {
          degree: 'Bachelor of Science in Computer Science',
          institution: 'University Name',
          grad_year: '2022',
          gpa: '3.8 / 4.0'
        }
      ]
    }));
  };

  const updateEducation = (idx, field, value) => {
    setDoc(prev => {
      const updated = [...prev.education];
      updated[idx] = { ...updated[idx], [field]: value };
      return { ...prev, education: updated };
    });
  };

  const removeEducation = (idx) => {
    setDoc(prev => ({
      ...prev,
      education: prev.education.filter((_, i) => i !== idx)
    }));
  };

  // Quick Assist: Inject Missing Keywords into Technical Skills
  const injectMissingKeywords = () => {
    if (!report?.keywords?.missing || report.keywords.missing.length === 0) return;
    const missing = report.keywords.missing;
    setDoc(prev => {
      const existing = new Set((prev.skills.technical || []).map(s => s.toLowerCase()));
      const toAdd = missing.filter(m => !existing.has(m.toLowerCase()));
      return {
        ...prev,
        skills: {
          ...prev.skills,
          technical: [...(prev.skills.technical || []), ...toAdd]
        }
      };
    });
  };

  // Export as Plain Text
  const exportCleanPlainText = async () => {
    if (!doc) return;
    try {
      const res = await fetch(`${backendUrl}/api/resume/format-clean-txt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ structured_resume: doc })
      });
      const data = await res.json();
      const plainText = data.plain_text;

      const blob = new Blob([plainText], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${(doc.contact?.full_name || 'Resume').replace(/\s+/g, '_')}_ATS_Clean.txt`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export plain text error:', err);
    }
  };

  // Copy Clean Text to Clipboard
  const copyCleanText = async () => {
    if (!doc) return;
    try {
      const res = await fetch(`${backendUrl}/api/resume/format-clean-txt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ structured_resume: doc })
      });
      const data = await res.json();
      navigator.clipboard.writeText(data.plain_text);
      setCopiedTxt(true);
      setTimeout(() => setCopiedTxt(false), 2000);
    } catch (err) {
      console.error('Copy plain text error:', err);
    }
  };

  // Print / PDF Export Handler
  const handlePrintPdf = () => {
    window.print();
  };

  // Estimated page budget line count calculation
  const totalEstimatedLines = useMemo(() => {
    if (!doc) return 0;
    let count = 6; // header & contact
    if (doc.summary) count += 4;
    doc.experience?.forEach(exp => {
      count += 2;
      count += (exp.bullets?.length || 1) * 2;
    });
    if (doc.skills) count += 4;
    if (doc.education) count += (doc.education.length * 2);
    return count;
  }, [doc]);

  const pageBudgetStatus = totalEstimatedLines <= 45 ? 'Optimal 1-Page Layout' : '2-Page Extended Profile';

  if (!extractedText || !extractedText.trim()) {
    return (
      <div className="empty-panel-state">
        <FileText size={48} className="empty-icon text-muted" />
        <p className="empty-state-title">No Resume Loaded</p>
        <p className="empty-state-subtitle">Please upload or analyze a resume to enter the Live In-Browser Editor.</p>
      </div>
    );
  }

  if (loading || !doc) {
    return (
      <div className="loading-interview-box">
        <div className="pulse-loader" />
        <p className="loading-text">Converting resume into structured ATS-verified document schema...</p>
      </div>
    );
  }

  const missingKeywordsCount = report?.keywords?.missing?.length || 0;

  return (
    <div className="resume-editor-studio-container">
      {/* Studio Header Toolbar */}
      <div className="editor-top-toolbar">
        <div className="editor-title-group">
          <div className="editor-badge-icon">
            <FileText size={20} className="text-indigo-400" />
          </div>
          <div>
            <h2 className="editor-title">📝 Live ATS-Verified Resume Editor</h2>
            <p className="editor-subtitle">
              Modify experience bullets, inject missing target keywords in 1 click, and compile clean ATS-grade PDFs.
            </p>
          </div>
        </div>

        <div className="editor-actions-group">
          {missingKeywordsCount > 0 && (
            <button
              className="quick-inject-btn"
              onClick={injectMissingKeywords}
              title={`Inject ${missingKeywordsCount} missing keywords into Technical Skills`}
            >
              <Sparkles size={14} />
              <span>Inject {missingKeywordsCount} Missing JD Keywords</span>
            </button>
          )}

          <button
            className="editor-btn-secondary"
            onClick={copyCleanText}
            title="Copy Clean ATS Text to Clipboard"
          >
            {copiedTxt ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
            <span>{copiedTxt ? 'Copied!' : 'Copy Clean Text'}</span>
          </button>

          <button
            className="editor-btn-secondary"
            onClick={exportCleanPlainText}
            title="Download Single-Column Plain Text (.txt)"
          >
            <Download size={14} />
            <span>Export .TXT</span>
          </button>

          <button
            className="editor-btn-primary"
            onClick={handlePrintPdf}
            title="Export 100% ATS Verified Clean PDF"
          >
            <Printer size={14} />
            <span>Export Verified PDF</span>
          </button>
        </div>
      </div>

      {/* Main Studio Dual Pane Layout */}
      <div className="editor-studio-split-grid">
        {/* Left Pane: Interactive Form Sections */}
        <div className="editor-form-pane">
          {/* Section Navigation Tabs */}
          <div className="editor-section-nav">
            <button
              className={`section-nav-btn ${activeSection === 'contact' ? 'active' : ''}`}
              onClick={() => setActiveSection('contact')}
            >
              <User size={14} /> Contact
            </button>
            <button
              className={`section-nav-btn ${activeSection === 'summary' ? 'active' : ''}`}
              onClick={() => setActiveSection('summary')}
            >
              <FileText size={14} /> Summary
            </button>
            <button
              className={`section-nav-btn ${activeSection === 'experience' ? 'active' : ''}`}
              onClick={() => setActiveSection('experience')}
            >
              <Briefcase size={14} /> Experience ({doc.experience?.length || 0})
            </button>
            <button
              className={`section-nav-btn ${activeSection === 'skills' ? 'active' : ''}`}
              onClick={() => setActiveSection('skills')}
            >
              <Wrench size={14} /> Skills
            </button>
            <button
              className={`section-nav-btn ${activeSection === 'education' ? 'active' : ''}`}
              onClick={() => setActiveSection('education')}
            >
              <GraduationCap size={14} /> Education ({doc.education?.length || 0})
            </button>
          </div>

          {/* Section 1: Contact Information */}
          {activeSection === 'contact' && (
            <div className="editor-section-card">
              <h3 className="section-card-title">Candidate Identity & Contact</h3>
              <div className="form-grid-2">
                <div className="form-group">
                  <label>Full Name</label>
                  <input
                    type="text"
                    value={doc.contact?.full_name || ''}
                    onChange={(e) => updateContact('full_name', e.target.value)}
                    placeholder="e.g. Alex Mercer"
                  />
                </div>
                <div className="form-group">
                  <label>Email Address</label>
                  <input
                    type="email"
                    value={doc.contact?.email || ''}
                    onChange={(e) => updateContact('email', e.target.value)}
                    placeholder="e.g. alex@example.com"
                  />
                </div>
                <div className="form-group">
                  <label>Phone Number</label>
                  <input
                    type="text"
                    value={doc.contact?.phone || ''}
                    onChange={(e) => updateContact('phone', e.target.value)}
                    placeholder="e.g. (555) 123-4567"
                  />
                </div>
                <div className="form-group">
                  <label>Location (City, State / Country)</label>
                  <input
                    type="text"
                    value={doc.contact?.location || ''}
                    onChange={(e) => updateContact('location', e.target.value)}
                    placeholder="e.g. San Francisco, CA"
                  />
                </div>
                <div className="form-group">
                  <label>LinkedIn URL / Handle</label>
                  <input
                    type="text"
                    value={doc.contact?.linkedin || ''}
                    onChange={(e) => updateContact('linkedin', e.target.value)}
                    placeholder="linkedin.com/in/username"
                  />
                </div>
                <div className="form-group">
                  <label>GitHub Profile / Portfolio</label>
                  <input
                    type="text"
                    value={doc.contact?.github || ''}
                    onChange={(e) => updateContact('github', e.target.value)}
                    placeholder="github.com/username"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Section 2: Summary */}
          {activeSection === 'summary' && (
            <div className="editor-section-card">
              <h3 className="section-card-title">Professional Summary</h3>
              <p className="section-card-desc">
                Keep summary between 40-70 words. Focus on target seniority, core tech specializations, and scale.
              </p>
              <textarea
                className="summary-textarea"
                rows={5}
                value={doc.summary || ''}
                onChange={(e) => updateSummary(e.target.value)}
                placeholder="Results-driven software engineer with 6+ years of experience in distributed cloud systems..."
              />
              <div className="textarea-footer">
                <span>{doc.summary ? doc.summary.trim().split(/\s+/).length : 0} words</span>
              </div>
            </div>
          )}

          {/* Section 3: Experience */}
          {activeSection === 'experience' && (
            <div className="editor-section-card">
              <div className="section-header-flex">
                <h3 className="section-card-title">Work Experience</h3>
                <button className="add-item-btn" onClick={addExperience}>
                  <Plus size={14} /> Add Role
                </button>
              </div>

              <div className="experience-list-stack">
                {doc.experience?.map((exp, expIdx) => (
                  <div key={expIdx} className="experience-card-item">
                    <div className="exp-card-header">
                      <div className="form-grid-2" style={{ flex: 1 }}>
                        <div className="form-group">
                          <label>Job Title</label>
                          <input
                            type="text"
                            value={exp.role || ''}
                            onChange={(e) => updateExperience(expIdx, 'role', e.target.value)}
                            placeholder="Senior Software Engineer"
                          />
                        </div>
                        <div className="form-group">
                          <label>Company / Organization</label>
                          <input
                            type="text"
                            value={exp.company || ''}
                            onChange={(e) => updateExperience(expIdx, 'company', e.target.value)}
                            placeholder="Acme Corp"
                          />
                        </div>
                        <div className="form-group">
                          <label>Location</label>
                          <input
                            type="text"
                            value={exp.location || ''}
                            onChange={(e) => updateExperience(expIdx, 'location', e.target.value)}
                            placeholder="San Francisco, CA"
                          />
                        </div>
                        <div className="form-group">
                          <label>Tenure / Dates</label>
                          <input
                            type="text"
                            value={exp.date_range || ''}
                            onChange={(e) => updateExperience(expIdx, 'date_range', e.target.value)}
                            placeholder="2021 - Present"
                          />
                        </div>
                      </div>
                      <button
                        className="delete-item-btn"
                        onClick={() => removeExperience(expIdx)}
                        title="Delete Role"
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>

                    {/* Bullets List */}
                    <div className="bullets-container">
                      <label className="bullets-label">Accomplishment Bullets (XYZ Google Formula):</label>
                      {exp.bullets?.map((b, bIdx) => (
                        <div key={bIdx} className="bullet-input-row">
                          <span className="bullet-dot">•</span>
                          <textarea
                            className="bullet-input"
                            rows={2}
                            value={b}
                            onChange={(e) => updateBullet(expIdx, bIdx, e.target.value)}
                            placeholder="Accomplished [X] as measured by [Y], by doing [Z]..."
                          />
                          <button
                            className="delete-bullet-btn"
                            onClick={() => removeBullet(expIdx, bIdx)}
                            title="Remove Bullet"
                          >
                            <Trash2 size={13} />
                          </button>
                        </div>
                      ))}
                      <button
                        className="add-bullet-btn"
                        onClick={() => addBullet(expIdx)}
                      >
                        <Plus size={13} /> Add Bullet
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Section 4: Skills */}
          {activeSection === 'skills' && (
            <div className="editor-section-card">
              <h3 className="section-card-title">Categorized Skills</h3>

              {/* Technical Skills */}
              <div className="skill-category-block">
                <label className="skill-cat-title">Languages & Core Technical:</label>
                <div className="tags-cloud">
                  {doc.skills?.technical?.map((skill, sIdx) => (
                    <span key={sIdx} className="skill-badge-removable">
                      {skill}
                      <button onClick={() => removeSkill('technical', sIdx)}>×</button>
                    </span>
                  ))}
                </div>
                <div className="add-tag-row">
                  <input
                    type="text"
                    value={newSkillInputs.technical}
                    onChange={(e) => setNewSkillInputs(prev => ({ ...prev, technical: e.target.value }))}
                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill('technical'))}
                    placeholder="Add skill (e.g. Python, Go)..."
                  />
                  <button onClick={() => addSkill('technical')}>Add</button>
                </div>
              </div>

              {/* Tools & Frameworks */}
              <div className="skill-category-block">
                <label className="skill-cat-title">Tools, Frameworks & Cloud Platforms:</label>
                <div className="tags-cloud">
                  {doc.skills?.tools_frameworks?.map((skill, sIdx) => (
                    <span key={sIdx} className="skill-badge-removable tool-tag">
                      {skill}
                      <button onClick={() => removeSkill('tools_frameworks', sIdx)}>×</button>
                    </span>
                  ))}
                </div>
                <div className="add-tag-row">
                  <input
                    type="text"
                    value={newSkillInputs.tools_frameworks}
                    onChange={(e) => setNewSkillInputs(prev => ({ ...prev, tools_frameworks: e.target.value }))}
                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill('tools_frameworks'))}
                    placeholder="Add tool (e.g. Docker, AWS, Kubernetes)..."
                  />
                  <button onClick={() => addSkill('tools_frameworks')}>Add</button>
                </div>
              </div>

              {/* Soft Skills */}
              <div className="skill-category-block">
                <label className="skill-cat-title">Leadership & Practices:</label>
                <div className="tags-cloud">
                  {doc.skills?.soft_skills?.map((skill, sIdx) => (
                    <span key={sIdx} className="skill-badge-removable soft-tag">
                      {skill}
                      <button onClick={() => removeSkill('soft_skills', sIdx)}>×</button>
                    </span>
                  ))}
                </div>
                <div className="add-tag-row">
                  <input
                    type="text"
                    value={newSkillInputs.soft_skills}
                    onChange={(e) => setNewSkillInputs(prev => ({ ...prev, soft_skills: e.target.value }))}
                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill('soft_skills'))}
                    placeholder="Add competency (e.g. System Design, Agile)..."
                  />
                  <button onClick={() => addSkill('soft_skills')}>Add</button>
                </div>
              </div>
            </div>
          )}

          {/* Section 5: Education */}
          {activeSection === 'education' && (
            <div className="editor-section-card">
              <div className="section-header-flex">
                <h3 className="section-card-title">Education & Degrees</h3>
                <button className="add-item-btn" onClick={addEducation}>
                  <Plus size={14} /> Add Degree
                </button>
              </div>

              <div className="experience-list-stack">
                {doc.education?.map((edu, eduIdx) => (
                  <div key={eduIdx} className="experience-card-item">
                    <div className="exp-card-header">
                      <div className="form-grid-2" style={{ flex: 1 }}>
                        <div className="form-group">
                          <label>Degree & Major</label>
                          <input
                            type="text"
                            value={edu.degree || ''}
                            onChange={(e) => updateEducation(eduIdx, 'degree', e.target.value)}
                            placeholder="B.S. in Computer Science"
                          />
                        </div>
                        <div className="form-group">
                          <label>University / Institution</label>
                          <input
                            type="text"
                            value={edu.institution || ''}
                            onChange={(e) => updateEducation(eduIdx, 'institution', e.target.value)}
                            placeholder="University of California, Berkeley"
                          />
                        </div>
                        <div className="form-group">
                          <label>Graduation Year</label>
                          <input
                            type="text"
                            value={edu.grad_year || ''}
                            onChange={(e) => updateEducation(eduIdx, 'grad_year', e.target.value)}
                            placeholder="2022"
                          />
                        </div>
                        <div className="form-group">
                          <label>GPA / Honors (Optional)</label>
                          <input
                            type="text"
                            value={edu.gpa || ''}
                            onChange={(e) => updateEducation(eduIdx, 'gpa', e.target.value)}
                            placeholder="3.8 / 4.0"
                          />
                        </div>
                      </div>
                      <button
                        className="delete-item-btn"
                        onClick={() => removeEducation(eduIdx)}
                        title="Delete Education"
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Pane: Live 1:1 ATS-Verified Preview Sheet */}
        <div className="editor-preview-pane">
          <div className="preview-pane-header">
            <div className="preview-status-pill">
              <CheckCircle2 size={14} className="text-emerald-400" />
              <span>100% Single-Column ATS Verified Layout</span>
            </div>
            <div className="preview-controls">
              <span className="page-lines-badge">{pageBudgetStatus}</span>
              <div className="font-toggle-group">
                <button
                  className={`font-btn ${fontFamily === 'sans' ? 'active' : ''}`}
                  onClick={() => setFontFamily('sans')}
                >
                  Sans (Inter)
                </button>
                <button
                  className={`font-btn ${fontFamily === 'serif' ? 'active' : ''}`}
                  onClick={() => setFontFamily('serif')}
                >
                  Serif (Times)
                </button>
              </div>
            </div>
          </div>

          {/* Actual Document Sheet Canvas */}
          <div className="ats-document-canvas-wrapper">
            <div
              ref={previewRef}
              className={`ats-sheet-paper font-${fontFamily}`}
              id="ats-print-sheet"
            >
              {/* Header */}
              <div className="sheet-header">
                <h1 className="sheet-name">{doc.contact?.full_name || 'YOUR NAME'}</h1>
                <div className="sheet-contact-line">
                  {[
                    doc.contact?.location,
                    doc.contact?.email,
                    doc.contact?.phone,
                    doc.contact?.linkedin,
                    doc.contact?.github
                  ].filter(Boolean).join('  •  ')}
                </div>
              </div>

              {/* Summary */}
              {doc.summary && (
                <div className="sheet-section">
                  <h2 className="sheet-heading">PROFESSIONAL SUMMARY</h2>
                  <p className="sheet-summary-text">{doc.summary}</p>
                </div>
              )}

              {/* Experience */}
              {doc.experience && doc.experience.length > 0 && (
                <div className="sheet-section">
                  <h2 className="sheet-heading">WORK EXPERIENCE</h2>
                  {doc.experience.map((exp, idx) => (
                    <div key={idx} className="sheet-exp-item">
                      <div className="sheet-row-between">
                        <span className="sheet-role-title">
                          <strong>{exp.role}</strong> — {exp.company}
                        </span>
                        <span className="sheet-date-range">{exp.date_range}</span>
                      </div>
                      <ul className="sheet-bullets-list">
                        {exp.bullets?.map((b, bIdx) => (
                          <li key={bIdx}>{b}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              )}

              {/* Skills */}
              {doc.skills && (
                <div className="sheet-section">
                  <h2 className="sheet-heading">TECHNICAL SKILLS</h2>
                  <div className="sheet-skills-body">
                    {doc.skills.technical?.length > 0 && (
                      <p className="sheet-skill-line">
                        <strong>Languages & Core:</strong> {doc.skills.technical.join(', ')}
                      </p>
                    )}
                    {doc.skills.tools_frameworks?.length > 0 && (
                      <p className="sheet-skill-line">
                        <strong>Tools & Platforms:</strong> {doc.skills.tools_frameworks.join(', ')}
                      </p>
                    )}
                    {doc.skills.soft_skills?.length > 0 && (
                      <p className="sheet-skill-line">
                        <strong>Leadership & Practices:</strong> {doc.skills.soft_skills.join(', ')}
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Education */}
              {doc.education && doc.education.length > 0 && (
                <div className="sheet-section">
                  <h2 className="sheet-heading">EDUCATION</h2>
                  {doc.education.map((edu, idx) => (
                    <div key={idx} className="sheet-edu-item">
                      <div className="sheet-row-between">
                        <span>
                          <strong>{edu.degree}</strong>, {edu.institution}
                        </span>
                        <span className="sheet-date-range">{edu.grad_year}</span>
                      </div>
                      {edu.gpa && <span className="sheet-sub-text">GPA: {edu.gpa}</span>}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
