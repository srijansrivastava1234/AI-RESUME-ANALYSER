import React from 'react';
import { UploadCloud, FileText, AlertTriangle } from 'lucide-react';

const MAX_SIZE_MB = 10;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export default function Dropzone({
  file,
  dragActive,
  handleDrag,
  handleDrop,
  handleFileChange,
  removeFile,
  error
}) {
  const sizePercent = file ? Math.min((file.size / MAX_SIZE_BYTES) * 100, 100) : 0;
  const sizeColor = sizePercent > 85 ? '#ef4444' : sizePercent > 60 ? '#f59e0b' : '#22c55e';

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
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>PDF, DOCX, TXT formats only (max. {MAX_SIZE_MB}MB)</p>
          <input 
            id="file-upload" 
            type="file" 
            accept=".pdf,.docx,.txt" 
            onChange={handleFileChange} 
            style={{ display: 'none' }} 
          />
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', borderRadius: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <FileText style={{ color: 'var(--primary)' }} />
              <div style={{ maxWidth: '180px', overflow: 'hidden' }}>
                <p style={{ fontSize: '0.9rem', fontWeight: 600, textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>{file.name}</p>
                <p style={{ fontSize: '0.75rem', color: sizeColor, fontWeight: 600 }}>{formatBytes(file.size)} / {MAX_SIZE_MB} MB</p>
              </div>
            </div>
            <button onClick={removeFile} style={{ background: 'transparent', border: 'none', color: 'var(--danger)', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600 }}>Remove</button>
          </div>
          <div style={{ height: '4px', background: 'rgba(255,255,255,0.08)', borderRadius: '2px', overflow: 'hidden' }}>
            <div style={{
              height: '100%',
              width: `${sizePercent}%`,
              background: sizeColor,
              borderRadius: '2px',
              transition: 'width 0.4s ease'
            }} />
          </div>
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
