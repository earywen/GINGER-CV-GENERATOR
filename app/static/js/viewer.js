/**
 * Interactive Canvas Preview Controller
 * Provides Figma/Canva style 2D viewport navigation, pan/zoom clamping,
 * HTML shadow DOM preview rendering, and export dispatching.
 */
import { State } from './state.js';
import { DOM } from './dom.js';
import { Utils } from './utils.js';

export const PreviewController = {
  // 2D Camera / Viewport State
  panX: 0,
  panY: 20,
  zoom: 0.70,
  minZoom: 0.25,
  maxZoom: 3.50,

  // Mouse / Drag State
  isDragging: false,
  lastPointerX: 0,
  lastPointerY: 0,
  currentTool: 'hand', // 'hand' or 'select'
  isSpacePressed: false,
  pageCount: 1,
  shadowRoot: null,
  _animTimer: null,
  _hasInitialFit: false,
  _renderSeq: 0,

  getDocDimensions() {
    const sheetWidth = 794;
    const pageHeight = 1123;
    const gap = 24;
    const count = Math.max(1, this.pageCount || 1);
    return {
      width: sheetWidth,
      height: count * pageHeight + (count - 1) * gap
    };
  },

  clampPan(targetPanX, targetPanY, targetZoom = this.zoom) {
    if (!DOM.pdfViewportContainer) return { x: targetPanX, y: targetPanY };

    const vw = DOM.pdfViewportContainer.clientWidth;
    const vh = DOM.pdfViewportContainer.clientHeight;
    if (!vw || !vh) return { x: targetPanX, y: targetPanY };

    const doc = this.getDocDimensions();
    const scaledW = doc.width * targetZoom;
    const scaledH = doc.height * targetZoom;

    const edgeMargin = 32;

    // Horizontal clamping
    let minPanX, maxPanX;
    if (scaledW >= vw) {
      minPanX = vw - scaledW - edgeMargin;
      maxPanX = edgeMargin;
    } else {
      const centerX = (vw - scaledW) / 2;
      const slack = Math.min(80, Math.max(20, (vw - scaledW) * 0.25));
      minPanX = centerX - slack;
      maxPanX = centerX + slack;
    }

    // Vertical clamping
    let minPanY, maxPanY;
    if (scaledH >= vh) {
      minPanY = vh - scaledH - edgeMargin;
      maxPanY = edgeMargin;
    } else {
      const centerY = Math.max(24, (vh - scaledH) / 2);
      const slack = Math.min(80, Math.max(20, (vh - scaledH) * 0.25));
      minPanY = centerY - slack;
      maxPanY = centerY + slack;
    }

    return {
      x: Math.min(maxPanX, Math.max(minPanX, targetPanX)),
      y: Math.min(maxPanY, Math.max(minPanY, targetPanY))
    };
  },

  updateTransform(animate = false) {
    if (!DOM.pdfStage) return;

    if (animate) {
      DOM.pdfStage.style.transition = 'transform 0.22s cubic-bezier(0.2, 0.8, 0.2, 1)';
      clearTimeout(this._animTimer);
      this._animTimer = setTimeout(() => {
        if (DOM.pdfStage) DOM.pdfStage.style.transition = 'none';
      }, 240);
    } else {
      DOM.pdfStage.style.transition = 'none';
    }

    DOM.pdfStage.style.transform = `translate3d(${this.panX.toFixed(1)}px, ${this.panY.toFixed(1)}px, 0) scale(${this.zoom.toFixed(3)})`;

    if (DOM.lblZoomVal) {
      DOM.lblZoomVal.textContent = `${Math.round(this.zoom * 100)}%`;
    }
  },

  setZoomAtPoint(newZoom, clientX, clientY, animate = false) {
    const clampedZoom = Math.min(this.maxZoom, Math.max(this.minZoom, newZoom));
    if (!DOM.pdfViewportContainer) return;

    const rect = DOM.pdfViewportContainer.getBoundingClientRect();
    const mouseX = clientX - rect.left;
    const mouseY = clientY - rect.top;

    // Anchor formula keeping the point under the mouse invariant:
    const newPanX = mouseX - (mouseX - this.panX) * (clampedZoom / this.zoom);
    const newPanY = mouseY - (mouseY - this.panY) * (clampedZoom / this.zoom);
    this.zoom = clampedZoom;

    const clamped = this.clampPan(newPanX, newPanY, this.zoom);
    this.panX = clamped.x;
    this.panY = clamped.y;

    this.updateTransform(animate);
  },

  zoomIn() {
    if (!DOM.pdfViewportContainer) return;
    const rect = DOM.pdfViewportContainer.getBoundingClientRect();
    this.setZoomAtPoint(this.zoom * 1.20, rect.left + rect.width / 2, rect.top + rect.height / 2, true);
  },

  zoomOut() {
    if (!DOM.pdfViewportContainer) return;
    const rect = DOM.pdfViewportContainer.getBoundingClientRect();
    this.setZoomAtPoint(this.zoom / 1.20, rect.left + rect.width / 2, rect.top + rect.height / 2, true);
  },

  zoomReset(animate = true) {
    if (!DOM.pdfViewportContainer) return;
    const doc = this.getDocDimensions();
    this.zoom = 1.0;
    const targetX = (DOM.pdfViewportContainer.clientWidth - doc.width * this.zoom) / 2;
    const targetY = 24;
    const clamped = this.clampPan(targetX, targetY, this.zoom);
    this.panX = clamped.x;
    this.panY = clamped.y;
    this.updateTransform(animate);
  },

  fitWidth(animate = true) {
    if (!DOM.pdfViewportContainer) return;
    const vw = DOM.pdfViewportContainer.clientWidth - 48;
    const doc = this.getDocDimensions();
    this.zoom = Math.min(1.6, Math.max(0.35, vw / doc.width));
    const targetX = (DOM.pdfViewportContainer.clientWidth - doc.width * this.zoom) / 2;
    const targetY = 24;
    const clamped = this.clampPan(targetX, targetY, this.zoom);
    this.panX = clamped.x;
    this.panY = clamped.y;
    this.updateTransform(animate);
  },

  fitPage(animate = true) {
    if (!DOM.pdfViewportContainer) return;
    const vw = DOM.pdfViewportContainer.clientWidth - 48;
    const vh = DOM.pdfViewportContainer.clientHeight - 48;
    const doc = this.getDocDimensions();
    const singlePageH = 1123;
    const fitW = vw / doc.width;
    const fitH = vh / singlePageH;
    this.zoom = Math.min(fitW, fitH, 1.0);
    const targetX = (DOM.pdfViewportContainer.clientWidth - doc.width * this.zoom) / 2;
    const targetY = Math.max(16, (DOM.pdfViewportContainer.clientHeight - singlePageH * this.zoom) / 2);
    const clamped = this.clampPan(targetX, targetY, this.zoom);
    this.panX = clamped.x;
    this.panY = clamped.y;
    this.updateTransform(animate);
  },

  goToPage(pageNum, animate = true) {
    if (!DOM.pdfViewportContainer) return;
    const doc = this.getDocDimensions();
    const pageHeight = 1123;
    const gap = 24;
    const targetX = (DOM.pdfViewportContainer.clientWidth - doc.width * this.zoom) / 2;
    let targetY = 24;
    if (pageNum === 2) {
      targetY = 24 - ((pageHeight + gap) * this.zoom);
    }
    const clamped = this.clampPan(targetX, targetY, this.zoom);
    this.panX = clamped.x;
    this.panY = clamped.y;
    this.updateTransform(animate);
  },

  setTool(tool) {
    this.currentTool = tool;
    const isHand = (tool === 'hand');

    if (DOM.btnToolHand && DOM.btnToolSelect) {
      if (isHand) {
        DOM.btnToolHand.className = 'px-2 py-1 rounded bg-white dark:bg-slate-800 text-burgeap-blue dark:text-burgeap-green shadow-xs transition flex items-center gap-1';
        DOM.btnToolSelect.className = 'px-2 py-1 rounded text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition flex items-center gap-1';
      } else {
        DOM.btnToolSelect.className = 'px-2 py-1 rounded bg-white dark:bg-slate-800 text-burgeap-blue dark:text-burgeap-green shadow-xs transition flex items-center gap-1';
        DOM.btnToolHand.className = 'px-2 py-1 rounded text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition flex items-center gap-1';
      }
    }

    const activeDrag = (isHand || this.isSpacePressed);
    if (DOM.pdfPanOverlay) {
      DOM.pdfPanOverlay.style.pointerEvents = activeDrag ? 'auto' : 'none';
      DOM.pdfPanOverlay.style.cursor = activeDrag ? 'grab' : 'default';
      if (activeDrag) {
        DOM.pdfPanOverlay.classList.remove('hidden');
      } else {
        DOM.pdfPanOverlay.classList.add('hidden');
      }
    }
    if (DOM.pdfViewportContainer) {
      DOM.pdfViewportContainer.style.cursor = activeDrag ? 'grab' : 'default';
    }
  },

  toggleFullscreen() {
    const container = DOM.rightColumnContainer;
    if (!container) return;
    if (!document.fullscreenElement) {
      container.requestFullscreen().catch(err => console.error(err));
    } else {
      document.exitFullscreen().catch(err => console.error(err));
    }
  },

  async refresh(silent = false) {
    if (!State.cvData) return;
    const seq = ++this._renderSeq;
    if (!silent && DOM.pdfLoadingSpinner) DOM.pdfLoadingSpinner.classList.remove('hidden');

    const refreshIcon = DOM.btnRefreshPreview ? DOM.btnRefreshPreview.querySelector('.fa-arrows-rotate') : null;
    if (refreshIcon) refreshIcon.classList.add('fa-spin');

    if (!this.shadowRoot && DOM.pdfShadowHost) {
      this.shadowRoot = DOM.pdfShadowHost.attachShadow({ mode: 'open' });
    }

    try {
      const res = await fetch('/api/render-html', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: State.cvData, lang: State.previewLang })
      });

      if (!res.ok) throw new Error('Erreur lors du rendu HTML.');

      const html = await res.text();
      if (seq !== this._renderSeq) return; // Discard outdated response

      if (this.shadowRoot) {
        this.shadowRoot.innerHTML = html;
        const pages = this.shadowRoot.querySelectorAll('.cv-page');
        this.pageCount = pages.length;

        if (DOM.btnPage2) {
          if (this.pageCount >= 2) {
            DOM.btnPage2.classList.remove('opacity-40', 'cursor-not-allowed');
            DOM.btnPage2.removeAttribute('disabled');
            DOM.btnPage2.title = 'Aller à la page 2 (2)';
          } else {
            DOM.btnPage2.classList.add('opacity-40', 'cursor-not-allowed');
            DOM.btnPage2.setAttribute('disabled', 'true');
            DOM.btnPage2.title = 'Le CV tient sur 1 seule page';
          }
        }
      }

      if (!this._hasInitialFit) {
        this._hasInitialFit = true;
        this.fitWidth(false);
      } else {
        const clamped = this.clampPan(this.panX, this.panY, this.zoom);
        this.panX = clamped.x;
        this.panY = clamped.y;
        this.updateTransform(false);
      }
    } catch (err) {
      console.error('Preview render error:', err);
    } finally {
      if (seq === this._renderSeq) {
        if (!silent && DOM.pdfLoadingSpinner) DOM.pdfLoadingSpinner.classList.add('hidden');
        if (refreshIcon) refreshIcon.classList.remove('fa-spin');
      }
    }
  },

  bindEvents(onSaveForm) {
    // Toolbar Buttons
    if (DOM.btnToolHand) DOM.btnToolHand.addEventListener('click', () => this.setTool('hand'));
    if (DOM.btnToolSelect) DOM.btnToolSelect.addEventListener('click', () => this.setTool('select'));
    if (DOM.btnPage1) DOM.btnPage1.addEventListener('click', () => this.goToPage(1));
    if (DOM.btnPage2) DOM.btnPage2.addEventListener('click', () => this.goToPage(2));
    if (DOM.btnZoomIn) DOM.btnZoomIn.addEventListener('click', () => this.zoomIn());
    if (DOM.btnZoomOut) DOM.btnZoomOut.addEventListener('click', () => this.zoomOut());
    if (DOM.btnZoomWidth) DOM.btnZoomWidth.addEventListener('click', () => this.fitWidth(true));
    if (DOM.btnZoomFit) DOM.btnZoomFit.addEventListener('click', () => this.fitPage(true));
    if (DOM.btnZoomReset) DOM.btnZoomReset.addEventListener('click', () => this.zoomReset(true));
    if (DOM.btnFullscreen) DOM.btnFullscreen.addEventListener('click', () => this.toggleFullscreen());

    if (DOM.btnOpenTab) {
      DOM.btnOpenTab.addEventListener('click', async () => {
        if (onSaveForm) onSaveForm();
        if (DOM.pdfLoadingSpinner) DOM.pdfLoadingSpinner.classList.remove('hidden');
        try {
          const res = await fetch('/api/export-pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data: State.cvData, lang: State.previewLang })
          });
          const blob = await res.blob();
          const blobUrl = URL.createObjectURL(blob);
          window.open(blobUrl, '_blank');
        } catch (e) {
          console.error('Error opening PDF in new tab:', e);
        } finally {
          if (DOM.pdfLoadingSpinner) DOM.pdfLoadingSpinner.classList.add('hidden');
        }
      });
    }

    // Pointer Drag to Pan (Canva/Figma style) with boundary clamping
    const onPointerDown = (e) => {
      if (e.button !== 0 && e.button !== 1) return; // Only left or middle click
      const isBackground = (e.target === DOM.pdfViewportContainer || e.target === DOM.pdfStage || e.target === DOM.pdfSheetContainer);
      const canDrag = (this.currentTool === 'hand' || this.isSpacePressed || e.button === 1 || isBackground);
      if (!canDrag) return;

      this.isDragging = true;
      this.lastPointerX = e.clientX;
      this.lastPointerY = e.clientY;

      if (DOM.pdfViewportContainer) DOM.pdfViewportContainer.classList.add('cursor-grabbing');
      if (DOM.pdfPanOverlay) DOM.pdfPanOverlay.classList.add('cursor-grabbing');
    };

    const onPointerMove = (e) => {
      if (!this.isDragging) return;
      const dx = e.clientX - this.lastPointerX;
      const dy = e.clientY - this.lastPointerY;
      this.lastPointerX = e.clientX;
      this.lastPointerY = e.clientY;

      const clamped = this.clampPan(this.panX + dx, this.panY + dy);
      this.panX = clamped.x;
      this.panY = clamped.y;
      this.updateTransform(false);
    };

    const onPointerUp = () => {
      if (this.isDragging) {
        this.isDragging = false;
        if (DOM.pdfViewportContainer) DOM.pdfViewportContainer.classList.remove('cursor-grabbing');
        if (DOM.pdfPanOverlay) DOM.pdfPanOverlay.classList.remove('cursor-grabbing');
      }
    };

    if (DOM.pdfViewportContainer) {
      DOM.pdfViewportContainer.addEventListener('mousedown', onPointerDown);
      window.addEventListener('mousemove', onPointerMove);
      window.addEventListener('mouseup', onPointerUp);
      window.addEventListener('blur', onPointerUp);

      // Smart Wheel: Ctrl/Pinch = Zoom at cursor, Normal wheel = Smooth vertical pan, Shift = Horizontal pan
      DOM.pdfViewportContainer.addEventListener('wheel', (e) => {
        e.preventDefault();
        if (e.ctrlKey || e.metaKey) {
          const zoomFactor = Math.pow(0.998, e.deltaY * 1.5);
          this.setZoomAtPoint(this.zoom * zoomFactor, e.clientX, e.clientY, false);
        } else if (e.shiftKey) {
          const clamped = this.clampPan(this.panX - e.deltaY * 0.9, this.panY);
          this.panX = clamped.x;
          this.panY = clamped.y;
          this.updateTransform(false);
        } else {
          const clamped = this.clampPan(this.panX, this.panY - e.deltaY * 0.9);
          this.panX = clamped.x;
          this.panY = clamped.y;
          this.updateTransform(false);
        }
      }, { passive: false });

      // Double click toggles between Fit Width and 100%
      DOM.pdfViewportContainer.addEventListener('dblclick', (e) => {
        if (e.target.closest && e.target.closest('button, select, input, textarea')) return;
        if (Math.abs(this.zoom - 1.0) < 0.1) {
          this.fitWidth(true);
        } else {
          this.zoomReset(true);
        }
      });
    }

    // Keyboard Shortcuts
    window.addEventListener('keydown', (e) => {
      const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
      const isContentEditable = document.activeElement && document.activeElement.isContentEditable;
      if (['input', 'textarea', 'select'].includes(activeTag) || isContentEditable) return;

      if (e.code === 'Space' && !this.isSpacePressed) {
        this.isSpacePressed = true;
        if (DOM.pdfPanOverlay) {
          DOM.pdfPanOverlay.classList.remove('hidden');
          DOM.pdfPanOverlay.style.pointerEvents = 'auto';
        }
        if (DOM.pdfViewportContainer) DOM.pdfViewportContainer.style.cursor = 'grab';
      } else if (e.key === 'h' || e.key === 'H') {
        this.setTool('hand');
      } else if (e.key === 'v' || e.key === 'V') {
        this.setTool('select');
      } else if (e.key === 'w' || e.key === 'W') {
        this.fitWidth(true);
      } else if (e.key === 'a' || e.key === 'A') {
        this.fitPage(true);
      } else if (e.key === '0') {
        this.zoomReset(true);
      } else if (e.key === '+' || e.key === '=') {
        this.zoomIn();
      } else if (e.key === '-') {
        this.zoomOut();
      } else if (e.key === '1') {
        this.goToPage(1);
      } else if (e.key === '2' && this.pageCount >= 2) {
        this.goToPage(2);
      } else if (e.key === 'f' || e.key === 'F') {
        this.toggleFullscreen();
      }
    });

    window.addEventListener('keyup', (e) => {
      if (e.code === 'Space') {
        this.isSpacePressed = false;
        const isHand = (this.currentTool === 'hand');
        if (DOM.pdfPanOverlay) {
          DOM.pdfPanOverlay.style.pointerEvents = isHand ? 'auto' : 'none';
          if (isHand) {
            DOM.pdfPanOverlay.classList.remove('hidden');
          } else {
            DOM.pdfPanOverlay.classList.add('hidden');
          }
        }
        if (DOM.pdfViewportContainer) {
          DOM.pdfViewportContainer.style.cursor = isHand ? 'grab' : 'default';
        }
      }
    });

    // Window resize re-anchors
    window.addEventListener('resize', () => {
      if (DOM.viewEditor && !DOM.viewEditor.classList.contains('hidden')) {
        this.fitWidth(false);
      }
    });

    if (DOM.btnDownloadActive) {
      DOM.btnDownloadActive.addEventListener('click', async () => {
        if (onSaveForm) onSaveForm();
        const res = await fetch('/api/export-pdf', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ data: State.cvData, lang: State.previewLang })
        });
        const blob = await res.blob();
        const name = (State.cvData.name || 'Collaborateur').replace(/\s+/g, '_');
        Utils.downloadBlob(blob, `CV_${name}_${State.previewLang.toUpperCase()}.pdf`);
      });
    }

    if (DOM.btnDownloadZip) {
      DOM.btnDownloadZip.addEventListener('click', async () => {
        if (onSaveForm) onSaveForm();
        const res = await fetch('/api/export-zip', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ data: State.cvData })
        });
        const blob = await res.blob();
        const name = (State.cvData.name || 'Collaborateur').replace(/\s+/g, '_');
        Utils.downloadBlob(blob, `CV_${name}_BURGEAP_2026.zip`);
      });
    }

    this.setTool('hand');
  }
};
