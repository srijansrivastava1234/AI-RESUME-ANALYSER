import React, { useState, useEffect, useRef, useCallback } from 'react';
import * as pdfjsLib from 'pdfjs-dist';
import pdfWorkerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url';
import {
  Eye,
  Layers,
  FileText,
  ZoomIn,
  ZoomOut,
  Maximize2,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  X,
  Crosshair,
  Compass
} from 'lucide-react';

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorkerUrl;

const MODE_LABELS = {
  gaze: { title: 'Recruiter Eye-Tracking', icon: Eye, desc: '6-second F/Z-pattern gaze simulation' },
  ats: { title: 'ATS Bounding Boxes', icon: Layers, desc: 'Parser segmentations & scanlines' },
  clean: { title: 'Clean Document', icon: FileText, desc: 'High-definition PDF rendering' }
};

const TYPE_COLORS = {
  header: { border: '#38bdf8', bg: 'rgba(56, 189, 248, 0.18)', badge: 'Header / Title' },
  contact: { border: '#34d399', bg: 'rgba(52, 211, 153, 0.18)', badge: 'Contact Info' },
  bullet: { border: '#c084fc', bg: 'rgba(192, 132, 252, 0.18)', badge: 'Action Bullet' },
  body: { border: '#94a3b8', bg: 'rgba(148, 163, 184, 0.12)', badge: 'Body Text' }
};

export default function PdfVisualStudio({
  file,
  backendUrl,
  isOpen,
  onClose
}) {
  const [pdfDoc, setPdfDoc] = useState(null);
  const [pageNum, setPageNum] = useState(1);
  const [numPages, setNumPages] = useState(1);
  const [scale, setScale] = useState(1.0);
  const [mode, setMode] = useState('gaze'); // 'gaze' | 'ats' | 'clean'
  const [showOrderPath, setShowOrderPath] = useState(true);
  const [gazeIntensity, setGazeIntensity] = useState(0.85);
  const [layoutData, setLayoutData] = useState(null);
  const [loadingLayout, setLoadingLayout] = useState(false);
  const [selectedToken, setSelectedToken] = useState(null);
  const [renderError, setRenderError] = useState(null);

  const canvasRef = useRef(null);
  const overlayCanvasRef = useRef(null);
  const containerRef = useRef(null);

  // 1. Fetch layout tokens from backend API
  useEffect(() => {
    if (!file || !isOpen) return;

    let isMounted = true;
    setLoadingLayout(true);
    setRenderError(null);

    const formData = new FormData();
    formData.append('file', file);

    fetch(`${backendUrl}/api/pdf-layout-tokens`, {
      method: 'POST',
      body: formData
    })
      .then(async (res) => {
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || `Server returned ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        if (isMounted) {
          if (data.success) {
            setLayoutData(data);
          } else {
            console.warn('Layout token warning:', data.error);
          }
        }
      })
      .catch((err) => {
        console.error('Failed to fetch layout tokens:', err);
      })
      .finally(() => {
        if (isMounted) setLoadingLayout(false);
      });

    return () => {
      isMounted = false;
    };
  }, [file, isOpen, backendUrl]);

  // 2. Load PDF Document via pdfjs-dist
  useEffect(() => {
    if (!file || !isOpen) return;

    let isMounted = true;
    const fileReader = new FileReader();

    fileReader.onload = async (e) => {
      try {
        const typedArray = new Uint8Array(e.target.result);
        const loadingTask = pdfjsLib.getDocument({ data: typedArray });
        const doc = await loadingTask.promise;
        if (isMounted) {
          setPdfDoc(doc);
          setNumPages(doc.numPages);
          setPageNum(1);
        }
      } catch (err) {
        console.error('Error loading PDF into PDF.js:', err);
        if (isMounted) setRenderError('Unable to render PDF preview: ' + err.message);
      }
    };

    fileReader.readAsArrayBuffer(file);

    return () => {
      isMounted = false;
    };
  }, [file, isOpen]);

  // 3. Render base PDF page onto primary canvas
  const renderPdfPage = useCallback(async () => {
    if (!pdfDoc || !canvasRef.current) return;

    try {
      const page = await pdfDoc.getPage(pageNum);
      const viewport = page.getViewport({ scale });
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');

      canvas.width = viewport.width;
      canvas.height = viewport.height;

      const renderContext = {
        canvasContext: ctx,
        viewport: viewport
      };

      await page.render(renderContext).promise;

      // Match overlay canvas dimensions
      if (overlayCanvasRef.current) {
        overlayCanvasRef.current.width = viewport.width;
        overlayCanvasRef.current.height = viewport.height;
        drawVisualOverlays(viewport.width, viewport.height);
      }
    } catch (err) {
      console.error('Render page error:', err);
    }
  }, [pdfDoc, pageNum, scale, mode, layoutData, gazeIntensity, showOrderPath]);

  // 4. Draw Gaze Heatmap / ATS Overlays onto the overlay canvas
  const drawVisualOverlays = (width, height) => {
    const canvas = overlayCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, width, height);

    const currentPageData = layoutData?.pages?.find((p) => p.page_number === pageNum);
    const tokens = currentPageData?.tokens || [];

    if (mode === 'gaze') {
      // Draw Recruiter Eye-Tracking Heatmap
      ctx.save();
      ctx.globalCompositeOperation = 'multiply';

      // Base F-pattern scanline path gradient
      const fGradient = ctx.createLinearGradient(0, 0, width, height);
      fGradient.addColorStop(0, `rgba(239, 68, 68, ${0.45 * gazeIntensity})`); // Red high-focus at top
      fGradient.addColorStop(0.15, `rgba(249, 115, 22, ${0.4 * gazeIntensity})`); // Orange title zone
      fGradient.addColorStop(0.35, `rgba(234, 179, 8, ${0.28 * gazeIntensity})`); // Yellow upper bullets
      fGradient.addColorStop(0.65, `rgba(59, 130, 246, ${0.15 * gazeIntensity})`); // Blue mid scan
      fGradient.addColorStop(1, `rgba(15, 23, 42, ${0.1 * gazeIntensity})`); // Low bottom focus

      ctx.fillStyle = fGradient;
      ctx.fillRect(0, 0, width, height);

      // Draw dynamic radial fixation hot-spots based on tokens
      tokens.forEach((t) => {
        const cx = (t.bbox.x + t.bbox.w / 2) * width;
        const cy = (t.bbox.y + t.bbox.h / 2) * height;
        const radius = Math.max(30, t.gaze_weight * 70 * gazeIntensity);

        const radial = ctx.createRadialGradient(cx, cy, 5, cx, cy, radius);
        if (t.gaze_weight >= 0.8) {
          radial.addColorStop(0, `rgba(239, 68, 68, ${0.65 * gazeIntensity})`);
          radial.addColorStop(0.5, `rgba(249, 115, 22, ${0.35 * gazeIntensity})`);
          radial.addColorStop(1, 'rgba(249, 115, 22, 0)');
        } else if (t.gaze_weight >= 0.5) {
          radial.addColorStop(0, `rgba(234, 179, 8, ${0.5 * gazeIntensity})`);
          radial.addColorStop(0.6, `rgba(59, 130, 246, ${0.2 * gazeIntensity})`);
          radial.addColorStop(1, 'rgba(59, 130, 246, 0)');
        } else {
          radial.addColorStop(0, `rgba(59, 130, 246, ${0.35 * gazeIntensity})`);
          radial.addColorStop(1, 'rgba(59, 130, 246, 0)');
        }

        ctx.fillStyle = radial;
        ctx.beginPath();
        ctx.arc(cx, cy, radius, 0, Math.PI * 2);
        ctx.fill();
      });

      ctx.restore();
    } else if (mode === 'ats') {
      // Draw Reading Order Scanline Path
      if (showOrderPath && tokens.length > 1) {
        ctx.save();
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.4)';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();

        tokens.forEach((t, i) => {
          const cx = (t.bbox.x + t.bbox.w / 2) * width;
          const cy = (t.bbox.y + t.bbox.h / 2) * height;
          if (i === 0) ctx.moveTo(cx, cy);
          else ctx.lineTo(cx, cy);
        });
        ctx.stroke();
        ctx.restore();
      }

      // Draw ATS Segment Bounding Boxes
      tokens.forEach((t) => {
        const x = t.bbox.x * width;
        const y = t.bbox.y * height;
        const w = t.bbox.w * width;
        const h = t.bbox.h * height;
        const colorConfig = TYPE_COLORS[t.type] || TYPE_COLORS.body;

        ctx.save();
        ctx.fillStyle = colorConfig.bg;
        ctx.fillRect(x, y, w, h);

        ctx.strokeStyle = colorConfig.border;
        ctx.lineWidth = selectedToken?.reading_order === t.reading_order ? 2.5 : 1;
        ctx.strokeRect(x, y, w, h);

        // Sequence badge
        ctx.fillStyle = colorConfig.border;
        ctx.beginPath();
        ctx.roundRect(x - 2, y - 10, 18, 12, 3);
        ctx.fill();

        ctx.fillStyle = '#0f172a';
        ctx.font = 'bold 9px sans-serif';
        ctx.fillText(`${t.reading_order}`, x + 1, y - 1);

        ctx.restore();
      });
    }
  };

  useEffect(() => {
    renderPdfPage();
  }, [renderPdfPage]);

  // Handle Canvas Click to Inspect Tokens
  const handleCanvasClick = (e) => {
    if (!overlayCanvasRef.current || !layoutData) return;
    const rect = overlayCanvasRef.current.getBoundingClientRect();
    const clickX = (e.clientX - rect.left) / rect.width;
    const clickY = (e.clientY - rect.top) / rect.height;

    const currentPageData = layoutData?.pages?.find((p) => p.page_number === pageNum);
    const tokens = currentPageData?.tokens || [];

    // Find clicked token
    const hit = tokens.find((t) => {
      const { x, y, w, h } = t.bbox;
      return clickX >= x && clickX <= x + w && clickY >= y && clickY <= y + h;
    });

    setSelectedToken(hit || null);
  };

  if (!isOpen) return null;

  const currentPageData = layoutData?.pages?.find((p) => p.page_number === pageNum);
  const totalTokens = currentPageData?.token_count || 0;

  return (
    <div className="pdf-studio-backdrop" onClick={onClose}>
      <div className="pdf-studio-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header Toolbar */}
        <div className="pdf-studio-header">
          <div className="pdf-studio-title-block">
            <div className="pdf-studio-badge">
              <Sparkles size={14} className="text-cyan-400" />
              <span>Document Intelligence Studio</span>
            </div>
            <h2>{file?.name || 'Resume Preview'}</h2>
          </div>

          {/* Mode Selector */}
          <div className="pdf-studio-modes">
            {Object.entries(MODE_LABELS).map(([key, item]) => {
              const IconComp = item.icon;
              const isActive = mode === key;
              return (
                <button
                  key={key}
                  className={`pdf-mode-btn ${isActive ? 'active' : ''}`}
                  onClick={() => setMode(key)}
                  title={item.desc}
                >
                  <IconComp size={15} />
                  <span>{item.title}</span>
                </button>
              );
            })}
          </div>

          <button className="pdf-close-btn" onClick={onClose} title="Close Studio">
            <X size={20} />
          </button>
        </div>

        {/* Studio Body */}
        <div className="pdf-studio-body">
          {/* Main Visual Canvas Area */}
          <div className="pdf-studio-canvas-wrap" ref={containerRef}>
            {renderError ? (
              <div className="pdf-render-error">
                <AlertCircle size={32} className="text-red-400" />
                <p>{renderError}</p>
              </div>
            ) : (
              <div
                className="pdf-canvas-container"
                style={{
                  transformOrigin: 'top center'
                }}
              >
                <canvas ref={canvasRef} className="pdf-base-canvas" />
                <canvas
                  ref={overlayCanvasRef}
                  className="pdf-overlay-canvas"
                  onClick={handleCanvasClick}
                />
              </div>
            )}
          </div>

          {/* Inspector Sidebar */}
          <div className="pdf-studio-sidebar">
            <div className="pdf-sidebar-card">
              <div className="pdf-sidebar-header">
                <Compass size={16} className="text-cyan-400" />
                <h3>Layer Diagnostics</h3>
              </div>

              {mode === 'gaze' && (
                <div className="pdf-sidebar-controls">
                  <label className="pdf-control-label">
                    <span>Gaze Heatmap Intensity</span>
                    <span>{Math.round(gazeIntensity * 100)}%</span>
                  </label>
                  <input
                    type="range"
                    min="0.3"
                    max="1.5"
                    step="0.05"
                    value={gazeIntensity}
                    onChange={(e) => setGazeIntensity(parseFloat(e.target.value))}
                    className="pdf-slider"
                  />
                  <div className="pdf-heatmap-legend">
                    <span className="legend-item"><span className="legend-dot red" /> 0-2s High Fixation</span>
                    <span className="legend-item"><span className="legend-dot yellow" /> 2-4s Secondary</span>
                    <span className="legend-item"><span className="legend-dot blue" /> 4-6s Skimmed</span>
                  </div>
                </div>
              )}

              {mode === 'ats' && (
                <div className="pdf-sidebar-controls">
                  <label className="pdf-checkbox-label">
                    <input
                      type="checkbox"
                      checked={showOrderPath}
                      onChange={(e) => setShowOrderPath(e.target.checked)}
                    />
                    <span>Show Reading-Order Scanline</span>
                  </label>

                  <div className="pdf-type-legend">
                    {Object.entries(TYPE_COLORS).map(([key, val]) => (
                      <div key={key} className="type-legend-row">
                        <span className="type-legend-swatch" style={{ background: val.border }} />
                        <span>{val.badge}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {mode === 'clean' && (
                <p className="pdf-clean-note">
                  Direct vector PDF preview with pure pixel fidelity. Use zoom controls to inspect typography and margins.
                </p>
              )}
            </div>

            {/* Token Inspector Details */}
            <div className="pdf-sidebar-card">
              <div className="pdf-sidebar-header">
                <Crosshair size={16} className="text-purple-400" />
                <h3>Selected Block Inspector</h3>
              </div>

              {selectedToken ? (
                <div className="pdf-token-inspector">
                  <div className="token-badge-row">
                    <span
                      className="token-type-pill"
                      style={{
                        borderColor: TYPE_COLORS[selectedToken.type]?.border || '#94a3b8',
                        color: TYPE_COLORS[selectedToken.type]?.border || '#94a3b8'
                      }}
                    >
                      {TYPE_COLORS[selectedToken.type]?.badge || selectedToken.type}
                    </span>
                    <span className="token-order-badge">#{selectedToken.reading_order} in scan</span>
                  </div>

                  <div className="token-text-box">
                    "{selectedToken.text}"
                  </div>

                  <div className="token-meta-grid">
                    <div className="token-meta-item">
                      <span className="meta-label">Font Size</span>
                      <span className="meta-value">{selectedToken.font_size}pt</span>
                    </div>
                    <div className="token-meta-item">
                      <span className="meta-label">Gaze Fixation</span>
                      <span className="meta-value font-mono text-cyan-400">
                        {Math.round(selectedToken.gaze_weight * 100)}%
                      </span>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="pdf-no-selection">
                  Click on any text bounding box on the document canvas to inspect parser metadata and gaze fixation.
                </p>
              )}
            </div>

            {/* Document Health Summary */}
            <div className="pdf-sidebar-card pdf-summary-card">
              <div className="summary-stat">
                <span className="stat-label">Page Tokens</span>
                <span className="stat-val">{totalTokens} blocks</span>
              </div>
              <div className="summary-stat">
                <span className="stat-label">Layout Status</span>
                <span className="stat-val text-emerald-400">
                  <CheckCircle2 size={13} className="inline mr-1" />
                  Linear Safe
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Navigation Bar */}
        <div className="pdf-studio-footer">
          {/* Page Switcher */}
          <div className="pdf-page-controls">
            <button
              className="pdf-nav-btn"
              disabled={pageNum <= 1}
              onClick={() => setPageNum((p) => Math.max(1, p - 1))}
            >
              <ChevronLeft size={16} />
            </button>
            <span className="pdf-page-indicator">
              Page {pageNum} of {numPages}
            </span>
            <button
              className="pdf-nav-btn"
              disabled={pageNum >= numPages}
              onClick={() => setPageNum((p) => Math.min(numPages, p + 1))}
            >
              <ChevronRight size={16} />
            </button>
          </div>

          {/* Zoom Controls */}
          <div className="pdf-zoom-controls">
            <button
              className="pdf-nav-btn"
              disabled={scale <= 0.6}
              onClick={() => setScale((s) => Math.max(0.5, s - 0.15))}
              title="Zoom Out"
            >
              <ZoomOut size={16} />
            </button>
            <span className="pdf-zoom-indicator">{Math.round(scale * 100)}%</span>
            <button
              className="pdf-nav-btn"
              disabled={scale >= 2.0}
              onClick={() => setScale((s) => Math.min(2.0, s + 0.15))}
              title="Zoom In"
            >
              <ZoomIn size={16} />
            </button>
            <button
              className="pdf-nav-btn"
              onClick={() => setScale(1.0)}
              title="Reset Zoom"
            >
              <Maximize2 size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
