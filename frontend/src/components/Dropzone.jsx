import React from 'react';
import { UploadCloud, FileText, AlertTriangle } from 'lucide-react';

export default function Dropzone({
  file,
  dragActive,
  handleDrag,
  handleDrop,
  handleFileChange,
  removeFile,
  error
}) {
  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Upload Resume</h3>
      
      {!file ? (
        <div 
          className={`dropzone-container ${dragActive ? 'active' : ''}`}
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          onClick={() => document.getElementById('file-upload').click()}
        >
          <UploadCloud className="upload-icon" style={{ width: '40px', height: '40px', margin: '0 auto 0.75rem' }} />
          <p style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.25rem' }}>Drag & drop your resume</p>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>PDF, DOCX, TXT formats only (max. 10MB)</p>
          <input 
            id="file-upload" 
            type="file" 
            accept=".pdf,.docx,.txt" 
            onChange={handleFileChange} 
            style={{ display: 'none' }} 
          />
        </div>
      ) : (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', borderRadius: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <FileText style={{ color: 'var(--primary)' }} />
            <div style={{ maxWidth: '180px', overflow: 'hidden' }}>
              <p style={{ fontSize: '0.9rem', fontWeight: 600, textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>{file.name}</p>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{(file.size / 1024).toFixed(1)} KB</p>
            </div>
          </div>
          <button onClick={removeFile} style={{ background: 'transparent', border: 'none', color: 'var(--danger)', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600 }}>Remove</button>
        </div>
      )}

      {error && (
        <div style={{ padding: '0.75rem', background: 'var(--danger-bg)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '8px', color: 'var(--danger)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertTriangle style={{ width: '16px', height: '16px', flexShrink: 0 }} />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
