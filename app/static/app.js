/**
 * Ginger Burgeap CV Generator 2026 - Frontend Controller
 * Modular, clean architecture managing State, Dropzones, Cropper, Editor, and PDF Live Preview.
 */

(() => {
  'use strict';

  // =========================================================================
  // 1. APPLICATION STATE
  // =========================================================================
  const State = {
    cvData: null,
    currentLang: 'fr', // 'fr' or 'en'
    previewLang: 'fr', // 'fr' or 'en'
    selectedCvFile: null,
    selectedPhotoFile: null,
    croppedPhotoB64: null,
    rawPhotoDataUrl: null,
    zoomLevel: 0.65,
    pollAttempts: 0,
    maxPollAttempts: 150
  };

  // =========================================================================
  // 2. DOM ELEMENT REGISTRY
  // =========================================================================
  const DOM = {
    // Views
    viewUpload: document.getElementById('view-upload'),
    viewLoading: document.getElementById('view-loading'),
    viewEditor: document.getElementById('view-editor'),
    btnResetTop: document.getElementById('btn-reset-top'),
    btnThemeToggle: document.getElementById('btn-theme-toggle'),

    // CV Dropzone
    cvDropzone: document.getElementById('cv-dropzone'),
    cvFileInput: document.getElementById('cv-file-input'),
    cvDropzoneEmpty: document.getElementById('cv-dropzone-empty'),
    cvDropzoneFilled: document.getElementById('cv-dropzone-filled'),
    cvFilename: document.getElementById('cv-filename'),
    cvFilesize: document.getElementById('cv-filesize'),
    btnRemoveCv: document.getElementById('btn-remove-cv'),

    // Photo Dropzone
    photoDropzone: document.getElementById('photo-dropzone'),
    photoFileInput: document.getElementById('photo-file-input'),
    photoDropzoneEmpty: document.getElementById('photo-dropzone-empty'),
    photoDropzoneFilled: document.getElementById('photo-dropzone-filled'),
    photoPreviewImg: document.getElementById('photo-preview-img'),
    photoFilename: document.getElementById('photo-filename'),
    btnRemovePhoto: document.getElementById('btn-remove-photo'),
    cbInitialsOnly: document.getElementById('cb-initials-only'),
    btnCropPhotoV1: document.getElementById('btn-crop-photo-v1'),

    // Configuration & Action
    selectAgency: document.getElementById('select-agency'),
    btnStartProcess: document.getElementById('btn-start-process'),

    // Loading Screen
    stepTitle: document.getElementById('loading-step-title'),
    stepDesc: document.getElementById('loading-step-desc'),
    progressBar: document.getElementById('loading-progress-bar'),

    // Editor Tabs & Actions
    tabFr: document.getElementById('tab-fr'),
    tabEn: document.getElementById('tab-en'),
    btnRefreshPreview: document.getElementById('btn-refresh-preview'),
    btnPreviewFr: document.getElementById('btn-preview-fr'),
    btnPreviewEn: document.getElementById('btn-preview-en'),
    btnDownloadActive: document.getElementById('btn-download-active'),
    btnDownloadZip: document.getElementById('btn-download-zip'),
    lblDownloadLang: document.getElementById('lbl-download-lang'),

    // Live Viewer & Interactive Canvas
    rightColumnContainer: document.getElementById('right-column-container'),
    pdfViewportContainer: document.getElementById('pdf-viewport-container'),
    pdfStage: document.getElementById('pdf-stage'),
    pdfSheetContainer: document.getElementById('pdf-sheet-container'),
    pdfPanOverlay: document.getElementById('pdf-pan-overlay'),
    pdfViewerFrame: document.getElementById('pdf-viewer-frame'),
    pdfLoadingSpinner: document.getElementById('pdf-loading-spinner'),
    btnToolHand: document.getElementById('btn-tool-hand'),
    btnToolSelect: document.getElementById('btn-tool-select'),
    btnPage1: document.getElementById('btn-page-1'),
    btnPage2: document.getElementById('btn-page-2'),
    btnZoomIn: document.getElementById('btn-zoom-in'),
    btnZoomOut: document.getElementById('btn-zoom-out'),
    btnZoomWidth: document.getElementById('btn-zoom-width'),
    btnZoomFit: document.getElementById('btn-zoom-fit'),
    btnZoomReset: document.getElementById('btn-zoom-reset'),
    btnFullscreen: document.getElementById('btn-fullscreen'),
    btnOpenTab: document.getElementById('btn-open-tab'),
    lblZoomVal: document.getElementById('lbl-zoom-val'),

    // Rich Text Pitch
    inpPitch: document.getElementById('inp-pitch'),
    btnPitchBold: document.getElementById('btn-pitch-bold'),
    btnPitchItalic: document.getElementById('btn-pitch-italic'),
    btnPitchClear: document.getElementById('btn-pitch-clear'),

    // Editor Avatar
    editorAvatarImg: document.getElementById('editor-avatar-img'),
    editorAvatarInitials: document.getElementById('editor-avatar-initials'),
    editorPhotoStatus: document.getElementById('editor-photo-status'),
    editorPhotoInput: document.getElementById('editor-photo-input'),
    btnEditorCrop: document.getElementById('btn-editor-crop'),
    btnEditorChangePhoto: document.getElementById('btn-editor-change-photo'),

    // Cropper Modal
    modalCropper: document.getElementById('modal-cropper'),
    cropperImage: document.getElementById('cropper-image'),
    btnCropperClose: document.getElementById('btn-cropper-close'),
    btnCropCancel: document.getElementById('btn-crop-cancel'),
    btnCropReset: document.getElementById('btn-crop-reset'),
    btnCropApply: document.getElementById('btn-crop-apply'),
    btnCropZoomIn: document.getElementById('btn-crop-zoom-in'),
    btnCropZoomOut: document.getElementById('btn-crop-zoom-out'),
    cropZoomSlider: document.getElementById('crop-zoom-slider'),
    btnCropRotateLeft: document.getElementById('btn-crop-rotate-left'),
    btnCropRotateRight: document.getElementById('btn-crop-rotate-right')
  };

  // =========================================================================
  // 3. UTILITY HELPERS
  // =========================================================================
  const Utils = {
    cleanHtml(html) {
      if (!html) return '';
      return html
        .replace(/<b>/gi, '<strong>')
        .replace(/<\/b>/gi, '</strong>')
        .replace(/<i>/gi, '<em>')
        .replace(/<\/i>/gi, '</em>')
        .replace(/<div><br\s*[\/]?>/gi, ' ')
        .replace(/<div>/gi, ' ')
        .replace(/<\/div>/gi, '')
        .replace(/[ \t]+/g, ' ')
        .trim();
    },

    formatText(command, value = null) {
      document.execCommand(command, false, value);
    },

    downloadBlob(blob, filename) {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    },

    optimizeImage(file, maxDimension = 1200) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          const img = new Image();
          img.onload = () => {
            let width = img.width;
            let height = img.height;
            if (width > maxDimension || height > maxDimension) {
              if (width > height) {
                height = Math.round((height * maxDimension) / width);
                width = maxDimension;
              } else {
                width = Math.round((width * maxDimension) / height);
                height = maxDimension;
              }
            }
            const canvas = document.createElement('canvas');
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, width, height);
            const dataUrl = canvas.toDataURL('image/jpeg', 0.92);
            const b64 = dataUrl.split(',')[1];
            resolve({ dataUrl, b64 });
          };
          img.onerror = () => reject(new Error('Format d\'image non supporté.'));
          img.src = e.target.result;
        };
        reader.onerror = () => reject(new Error('Erreur de lecture du fichier image.'));
        reader.readAsDataURL(file);
      });
    }
  };

  const SVG_AVATAR_PLACEHOLDER = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'%3E%3Ccircle cx='24' cy='24' r='24' fill='%2313375f'/%3E%3C/svg%3E";

  // =========================================================================
  // 3.5. THEME CONTROLLER (Dark / Light Mode)
  // =========================================================================
  const ThemeController = {
    init() {
      if (DOM.btnThemeToggle) {
        DOM.btnThemeToggle.addEventListener('click', () => this.toggle());
      }
    },

    toggle() {
      const isDark = document.documentElement.classList.contains('dark');
      if (isDark) {
        document.documentElement.classList.remove('dark');
        localStorage.theme = 'light';
      } else {
        document.documentElement.classList.add('dark');
        localStorage.theme = 'dark';
      }
    }
  };

  // =========================================================================
  // 4. CROPPER CONTROLLER
  // =========================================================================
  const CropperController = {
    cropperInstance: null,
    applyCallback: null,

    open(imageSrc, onApply) {
      if (!imageSrc) return;
      this.applyCallback = onApply;
      DOM.modalCropper.classList.remove('hidden');

      if (this.cropperInstance) {
        this.cropperInstance.destroy();
        this.cropperInstance = null;
      }

      DOM.cropperImage.src = imageSrc;

      const init = () => {
        this.cropperInstance = new Cropper(DOM.cropperImage, {
          aspectRatio: 1,
          viewMode: 1,
          dragMode: 'move',
          autoCropArea: 0.85,
          restore: false,
          guides: true,
          center: true,
          highlight: false,
          cropBoxMovable: false,
          cropBoxResizable: true,
          toggleDragModeOnDblclick: false,
          zoomOnWheel: true,
          zoomOnTouch: true,
          ready() {
            if (DOM.cropZoomSlider) DOM.cropZoomSlider.value = 1;
          },
          zoom(e) {
            if (DOM.cropZoomSlider && e.detail && e.detail.ratio) {
              DOM.cropZoomSlider.value = Math.min(3, Math.max(0.1, e.detail.ratio));
            }
          }
        });
      };

      if (DOM.cropperImage.complete && DOM.cropperImage.naturalWidth > 0) {
        init();
      } else {
        DOM.cropperImage.onload = init;
      }
    },

    close() {
      DOM.modalCropper.classList.add('hidden');
      if (this.cropperInstance) {
        this.cropperInstance.destroy();
        this.cropperInstance = null;
      }
      this.applyCallback = null;
    },

    bindEvents() {
      if (DOM.btnCropperClose) DOM.btnCropperClose.addEventListener('click', () => this.close());
      if (DOM.btnCropCancel) DOM.btnCropCancel.addEventListener('click', () => this.close());

      if (DOM.btnCropReset) {
        DOM.btnCropReset.addEventListener('click', () => {
          if (this.cropperInstance) {
            this.cropperInstance.reset();
            if (DOM.cropZoomSlider) DOM.cropZoomSlider.value = 1;
          }
        });
      }

      if (DOM.btnCropZoomIn) {
        DOM.btnCropZoomIn.addEventListener('click', () => {
          if (this.cropperInstance) this.cropperInstance.zoom(0.1);
        });
      }

      if (DOM.btnCropZoomOut) {
        DOM.btnCropZoomOut.addEventListener('click', () => {
          if (this.cropperInstance) this.cropperInstance.zoom(-0.1);
        });
      }

      if (DOM.cropZoomSlider) {
        DOM.cropZoomSlider.addEventListener('input', (e) => {
          if (this.cropperInstance) {
            this.cropperInstance.zoomTo(parseFloat(e.target.value));
          }
        });
      }

      if (DOM.btnCropRotateLeft) {
        DOM.btnCropRotateLeft.addEventListener('click', () => {
          if (this.cropperInstance) this.cropperInstance.rotate(-90);
        });
      }

      if (DOM.btnCropRotateRight) {
        DOM.btnCropRotateRight.addEventListener('click', () => {
          if (this.cropperInstance) this.cropperInstance.rotate(90);
        });
      }

      if (DOM.btnCropApply) {
        DOM.btnCropApply.addEventListener('click', () => {
          if (!this.cropperInstance) return;
          const canvas = this.cropperInstance.getCroppedCanvas({
            width: 800,
            height: 800,
            imageSmoothingEnabled: true,
            imageSmoothingQuality: 'high'
          });

          const dataUrl = canvas.toDataURL('image/jpeg', 0.95);
          const b64 = dataUrl.split(',')[1];

          if (this.applyCallback) {
            this.applyCallback(b64, dataUrl);
          }
          this.close();
        });
      }
    }
  };

  // =========================================================================
  // 5. INTERACTIVE CANVAS PREVIEW CONTROLLER (Canva / Figma style)
  // =========================================================================
  const PreviewController = {
    // 2D Camera / Viewport State
    panX: 0,
    panY: 20,
    zoom: 0.70,
    minZoom: 0.30,
    maxZoom: 2.20,

    // Mouse / Drag State
    isDragging: false,
    dragStartX: 0,
    dragStartY: 0,
    initialPanX: 0,
    initialPanY: 0,
    currentTool: 'hand', // 'hand' or 'select'
    isSpacePressed: false,
    pageCount: 1,
    _animTimer: null,

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
      this.panX = mouseX - (mouseX - this.panX) * (clampedZoom / this.zoom);
      this.panY = mouseY - (mouseY - this.panY) * (clampedZoom / this.zoom);
      this.zoom = clampedZoom;

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
      const sheetWidth = 820;
      this.zoom = 1.0;
      this.panX = (DOM.pdfViewportContainer.clientWidth - sheetWidth * this.zoom) / 2;
      this.panY = 24;
      this.updateTransform(animate);
    },

    fitWidth(animate = true) {
      if (!DOM.pdfViewportContainer) return;
      const vw = DOM.pdfViewportContainer.clientWidth - 40;
      const sheetWidth = 820;
      this.zoom = Math.min(1.4, Math.max(0.40, vw / sheetWidth));
      this.panX = Math.max(12, (DOM.pdfViewportContainer.clientWidth - sheetWidth * this.zoom) / 2);
      this.panY = 20;
      this.updateTransform(animate);
    },

    fitPage(animate = true) {
      if (!DOM.pdfViewportContainer) return;
      const vw = DOM.pdfViewportContainer.clientWidth - 40;
      const vh = DOM.pdfViewportContainer.clientHeight - 40;
      const sheetWidth = 820;
      const sheetHeight = 1180;
      const fitW = vw / sheetWidth;
      const fitH = vh / sheetHeight;
      this.zoom = Math.min(fitW, fitH, 1.0);
      this.panX = (DOM.pdfViewportContainer.clientWidth - sheetWidth * this.zoom) / 2;
      this.panY = Math.max(16, (DOM.pdfViewportContainer.clientHeight - sheetHeight * this.zoom) / 2);
      this.updateTransform(animate);
    },

    goToPage(pageNum, animate = true) {
      if (!DOM.pdfViewportContainer) return;
      const sheetWidth = 820;
      const pageHeight = 1146; // height of Page 1 with margin
      this.panX = (DOM.pdfViewportContainer.clientWidth - sheetWidth * this.zoom) / 2;
      if (pageNum === 1) {
        this.panY = 20;
      } else {
        this.panY = 20 - (pageHeight * this.zoom);
      }
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

      if (DOM.pdfPanOverlay) {
        DOM.pdfPanOverlay.style.pointerEvents = (isHand || this.isSpacePressed) ? 'auto' : 'none';
        DOM.pdfPanOverlay.style.cursor = (isHand || this.isSpacePressed) ? 'grab' : 'default';
      }
      if (DOM.pdfViewportContainer) {
        DOM.pdfViewportContainer.style.cursor = (isHand || this.isSpacePressed) ? 'grab' : 'default';
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

    async refresh() {
      if (!State.cvData) return;
      DOM.pdfLoadingSpinner.classList.remove('hidden');

      try {
        const res = await fetch('/api/render-html', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ data: State.cvData, lang: State.previewLang })
        });

        if (!res.ok) throw new Error('Erreur lors du rendu HTML.');

        const html = await res.text();
        DOM.pdfViewerFrame.srcdoc = html;

        DOM.pdfViewerFrame.onload = () => {
          DOM.pdfLoadingSpinner.classList.add('hidden');
          try {
            const doc = DOM.pdfViewerFrame.contentDocument || DOM.pdfViewerFrame.contentWindow.document;
            if (doc) {
              const pages = doc.querySelectorAll('.cv-page');
              this.pageCount = pages.length;
              const iframeHeight = pages.length >= 2 ? 2360 : 1200;
              DOM.pdfViewerFrame.style.height = `${iframeHeight}px`;

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
          } catch (e) {
            console.warn('Frame inspection warning:', e);
          }
          this.fitWidth(false);
        };
      } catch (err) {
        console.error('Preview render error:', err);
        DOM.pdfLoadingSpinner.classList.add('hidden');
      }
    },

    bindEvents() {
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

      // Pointer Drag to Pan (Canva/Figma style)
      const onPointerDown = (e) => {
        if (e.button !== 0 && e.button !== 1) return; // Only left or middle click
        const canDrag = (this.currentTool === 'hand' || this.isSpacePressed || e.button === 1);
        if (!canDrag) return;

        this.isDragging = true;
        this.dragStartX = e.clientX;
        this.dragStartY = e.clientY;
        this.initialPanX = this.panX;
        this.initialPanY = this.panY;

        if (DOM.pdfViewportContainer) DOM.pdfViewportContainer.style.cursor = 'grabbing';
        if (DOM.pdfPanOverlay) DOM.pdfPanOverlay.style.cursor = 'grabbing';
      };

      const onPointerMove = (e) => {
        if (!this.isDragging) return;
        const dx = e.clientX - this.dragStartX;
        const dy = e.clientY - this.dragStartY;
        this.panX = this.initialPanX + dx;
        this.panY = this.initialPanY + dy;
        this.updateTransform(false);
      };

      const onPointerUp = () => {
        if (this.isDragging) {
          this.isDragging = false;
          const isHand = (this.currentTool === 'hand' || this.isSpacePressed);
          if (DOM.pdfViewportContainer) DOM.pdfViewportContainer.style.cursor = isHand ? 'grab' : 'default';
          if (DOM.pdfPanOverlay) DOM.pdfPanOverlay.style.cursor = isHand ? 'grab' : 'default';
        }
      };

      if (DOM.pdfViewportContainer) {
        DOM.pdfViewportContainer.addEventListener('mousedown', onPointerDown);
        window.addEventListener('mousemove', onPointerMove);
        window.addEventListener('mouseup', onPointerUp);

        // Smart Wheel: Ctrl/Pinch = Zoom at cursor, Normal wheel = Smooth vertical pan, Shift = Horizontal pan
        DOM.pdfViewportContainer.addEventListener('wheel', (e) => {
          e.preventDefault();
          if (e.ctrlKey || e.metaKey) {
            const zoomFactor = Math.pow(0.998, e.deltaY * 1.5);
            this.setZoomAtPoint(this.zoom * zoomFactor, e.clientX, e.clientY, false);
          } else if (e.shiftKey) {
            this.panX -= e.deltaY * 0.9;
            this.updateTransform(false);
          } else {
            this.panY -= e.deltaY * 0.9;
            this.updateTransform(false);
          }
        }, { passive: false });

        // Double click toggles between Fit Width and 100%
        DOM.pdfViewportContainer.addEventListener('dblclick', () => {
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
          if (DOM.pdfPanOverlay) DOM.pdfPanOverlay.style.pointerEvents = 'auto';
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
          if (DOM.pdfPanOverlay) {
            DOM.pdfPanOverlay.style.pointerEvents = (this.currentTool === 'hand') ? 'auto' : 'none';
          }
          if (DOM.pdfViewportContainer) {
            DOM.pdfViewportContainer.style.cursor = (this.currentTool === 'hand') ? 'grab' : 'default';
          }
        }
      });

      // Window resize re-anchors
      window.addEventListener('resize', () => {
        if (DOM.viewEditor && !DOM.viewEditor.classList.contains('hidden')) {
          this.fitWidth(false);
        }
      });

      if (DOM.btnPreviewFr) {
        DOM.btnPreviewFr.addEventListener('click', () => {
          State.previewLang = 'fr';
          DOM.btnPreviewFr.className = 'px-2.5 py-1 rounded bg-white dark:bg-slate-800 text-burgeap-blue dark:text-burgeap-green shadow-sm flex items-center gap-1.5 font-bold';
          DOM.btnPreviewEn.className = 'px-2.5 py-1 rounded text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white flex items-center gap-1.5 font-bold';
          if (DOM.lblDownloadLang) DOM.lblDownloadLang.textContent = 'FR';
          EditorController.saveCurrentForm();
          this.refresh();
        });
      }

      if (DOM.btnPreviewEn) {
        DOM.btnPreviewEn.addEventListener('click', () => {
          State.previewLang = 'en';
          DOM.btnPreviewEn.className = 'px-2.5 py-1 rounded bg-white dark:bg-slate-800 text-burgeap-blue dark:text-burgeap-green shadow-sm flex items-center gap-1.5 font-bold';
          DOM.btnPreviewFr.className = 'px-2.5 py-1 rounded text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white flex items-center gap-1.5 font-bold';
          if (DOM.lblDownloadLang) DOM.lblDownloadLang.textContent = 'EN';
          EditorController.saveCurrentForm();
          this.refresh();
        });
      }

      if (DOM.btnDownloadActive) {
        DOM.btnDownloadActive.addEventListener('click', async () => {
          EditorController.saveCurrentForm();
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
          EditorController.saveCurrentForm();
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
    }
  };

  // =========================================================================
  // 6. EDITOR CONTROLLER
  // =========================================================================
  const EditorController = {
    switchLang(lang) {
      this.saveCurrentForm();
      State.currentLang = lang;

      if (lang === 'fr') {
        DOM.tabFr.className = 'px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-2 bg-burgeap-blue text-white shadow-sm';
        DOM.tabEn.className = 'px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-2 bg-transparent text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700';
        document.querySelectorAll('.lang-label').forEach(el => el.textContent = 'FR');
      } else {
        DOM.tabEn.className = 'px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-2 bg-burgeap-blue text-white shadow-sm';
        DOM.tabFr.className = 'px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-2 bg-transparent text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700';
        document.querySelectorAll('.lang-label').forEach(el => el.textContent = 'EN');
      }

      this.populate();
    },

    saveCurrentForm() {
      if (!State.cvData) return;
      State.cvData.name = document.getElementById('inp-name').value;
      State.cvData.trigram = document.getElementById('inp-trigram').value;

      const isFr = (State.currentLang === 'fr');
      if (isFr) {
        State.cvData.role_fr = document.getElementById('inp-role').value;
        State.cvData.exp_fr = document.getElementById('inp-exp').value;
        State.cvData.pitch_fr = Utils.cleanHtml(DOM.inpPitch.innerHTML);
      } else {
        State.cvData.role_en = document.getElementById('inp-role').value;
        State.cvData.exp_en = document.getElementById('inp-exp').value;
        State.cvData.pitch_en = Utils.cleanHtml(DOM.inpPitch.innerHTML);
      }
    },

    populate() {
      if (!State.cvData) return;
      const isFr = (State.currentLang === 'fr');

      document.getElementById('inp-name').value = State.cvData.name || '';
      document.getElementById('inp-trigram').value = State.cvData.trigram || '';
      document.getElementById('inp-role').value = isFr ? (State.cvData.role_fr || '') : (State.cvData.role_en || '');
      document.getElementById('inp-exp').value = isFr ? (State.cvData.exp_fr || '') : (State.cvData.exp_en || '');

      DOM.inpPitch.innerHTML = isFr ? (State.cvData.pitch_fr || '') : (State.cvData.pitch_en || '');

      this.renderDynamicList('list-formations', isFr ? State.cvData.formations_fr : State.cvData.formations_en);
      this.renderDynamicList('list-competences', isFr ? State.cvData.competences_fr : State.cvData.competences_en);
      this.renderDynamicList('list-exp-pros', isFr ? State.cvData.exp_pros_fr : State.cvData.exp_pros_en);
      this.renderDynamicList('list-langs', isFr ? State.cvData.langs_fr : State.cvData.langs_en);

      this.renderQualifsList(isFr ? State.cvData.qualifs_fr : State.cvData.qualifs_en);
      this.renderRefsList(isFr ? State.cvData.refs_fr : State.cvData.refs_en);

      this.updateAvatar();
    },

    updateAvatar() {
      if (!DOM.editorAvatarImg) return;
      if (State.cvData && State.cvData.photo_b64) {
        DOM.editorAvatarImg.src = `data:image/jpeg;base64,${State.cvData.photo_b64}`;
        DOM.editorAvatarImg.classList.remove('hidden');
        DOM.editorAvatarInitials.classList.add('hidden');
        if (DOM.editorPhotoStatus) DOM.editorPhotoStatus.textContent = 'Photo studio chargée (Ajuster possible)';
      } else {
        DOM.editorAvatarImg.src = SVG_AVATAR_PLACEHOLDER;
        DOM.editorAvatarImg.classList.add('hidden');
        DOM.editorAvatarInitials.classList.remove('hidden');
        DOM.editorAvatarInitials.textContent = (State.cvData && State.cvData.initials) ? State.cvData.initials : 'GB';
        if (DOM.editorPhotoStatus) DOM.editorPhotoStatus.textContent = 'Médaillon initiales officielles';
      }
    },

    renderDynamicList(containerId, items) {
      const container = document.getElementById(containerId);
      if (!container) return;
      container.innerHTML = '';
      if (!items) return;

      items.forEach((item, idx) => {
        const row = document.createElement('div');
        row.className = 'flex items-center space-x-2';
        row.innerHTML = `
          <div contenteditable="true" class="flex-1 border border-slate-300 dark:border-slate-700 rounded px-2.5 py-1 text-xs focus:ring-1 focus:ring-burgeap-blue dark:focus:ring-burgeap-green focus:outline-none bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100">${item}</div>
          <button type="button" class="text-slate-400 hover:text-red-500 px-1.5 py-1 text-xs"><i class="fa-solid fa-xmark"></i></button>
        `;

        const editableDiv = row.querySelector('div[contenteditable]');
        row.querySelector('button').addEventListener('click', () => {
          items.splice(idx, 1);
          this.renderDynamicList(containerId, items);
        });
        editableDiv.addEventListener('input', () => {
          items[idx] = Utils.cleanHtml(editableDiv.innerHTML);
        });
        container.appendChild(row);
      });

      const btnAdd = document.createElement('button');
      btnAdd.type = 'button';
      btnAdd.className = 'text-[11px] font-bold text-burgeap-blue dark:text-burgeap-green hover:underline mt-1 flex items-center gap-1';
      btnAdd.innerHTML = '<i class="fa-solid fa-plus"></i> Ajouter une ligne';
      btnAdd.addEventListener('click', () => {
        items.push('Nouvel élément');
        this.renderDynamicList(containerId, items);
      });
      container.appendChild(btnAdd);
    },

    renderQualifsList(qualifs) {
      const container = document.getElementById('list-qualifs');
      if (!container) return;
      container.innerHTML = '';
      if (!qualifs) return;

      qualifs.forEach((q, idx) => {
        const item = document.createElement('div');
        item.className = 'py-2 border-b border-slate-200 dark:border-slate-800 last:border-b-0 space-y-1.5';
        item.innerHTML = `
          <div class="flex justify-between items-center text-[11px] font-bold text-slate-600 dark:text-slate-300">
            <span>Point ${idx + 1}</span>
            <div class="flex items-center space-x-1 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded px-1.5 py-0.5">
              <button type="button" class="btn-q-bold px-1.5 py-0.2 text-[11px] font-bold hover:bg-slate-200 dark:hover:bg-slate-700 rounded text-slate-700 dark:text-slate-200" title="Mettre en gras"><i class="fa-solid fa-bold"></i></button>
              <button type="button" class="btn-q-italic px-1.5 py-0.2 text-[11px] italic hover:bg-slate-200 dark:hover:bg-slate-700 rounded text-slate-700 dark:text-slate-200" title="Mettre en italique"><i class="fa-solid fa-italic"></i></button>
            </div>
          </div>
          <div contenteditable="true" class="q-content w-full min-h-[42px] border border-slate-300 dark:border-slate-700 rounded-lg p-2 text-xs bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 focus:ring-1 focus:ring-burgeap-blue dark:focus:ring-burgeap-green focus:outline-none leading-relaxed">${q}</div>
        `;

        const editableQ = item.querySelector('.q-content');
        item.querySelector('.btn-q-bold').addEventListener('click', (e) => {
          e.preventDefault();
          editableQ.focus();
          Utils.formatText('bold');
        });
        item.querySelector('.btn-q-italic').addEventListener('click', (e) => {
          e.preventDefault();
          editableQ.focus();
          Utils.formatText('italic');
        });
        editableQ.addEventListener('input', () => {
          qualifs[idx] = Utils.cleanHtml(editableQ.innerHTML);
        });

        container.appendChild(item);
      });
    },

    renderRefsList(refs) {
      const container = document.getElementById('list-refs');
      if (!container) return;
      container.innerHTML = '';
      if (!refs) return;

      refs.forEach((r, idx) => {
        const item = document.createElement('div');
        item.className = 'py-3 border-b border-slate-200 dark:border-slate-800 last:border-b-0 space-y-2';
        item.innerHTML = `
          <div class="flex justify-between items-center text-xs font-bold text-burgeap-blue dark:text-burgeap-green">
            <span>Mission ${idx + 1}</span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <div>
              <label class="block text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Titre Projet (MAJUSCULE)</label>
              <input type="text" value="${(r.title || '').replace(/"/g, '&quot;')}" class="inp-ref-title w-full border border-slate-300 dark:border-slate-700 rounded-lg px-2.5 py-1 text-xs font-bold bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 focus:ring-1 focus:ring-burgeap-blue dark:focus:ring-burgeap-green focus:outline-none">
            </div>
            <div>
              <label class="block text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Badge Thématique</label>
              <input type="text" value="${(r.tag || '').replace(/"/g, '&quot;')}" class="inp-ref-tag w-full border border-slate-300 dark:border-slate-700 rounded-lg px-2.5 py-1 text-xs font-semibold bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 focus:ring-1 focus:ring-burgeap-blue dark:focus:ring-burgeap-green focus:outline-none">
            </div>
          </div>
          <div>
            <label class="block text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Description Synthétique</label>
            <textarea rows="2" class="inp-ref-desc w-full border border-slate-300 dark:border-slate-700 rounded-lg p-2 text-xs bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 focus:ring-1 focus:ring-burgeap-blue dark:focus:ring-burgeap-green focus:outline-none leading-relaxed">${r.desc || ''}</textarea>
          </div>
        `;

        item.querySelector('.inp-ref-title').addEventListener('input', (e) => r.title = e.target.value);
        item.querySelector('.inp-ref-tag').addEventListener('input', (e) => r.tag = e.target.value);
        item.querySelector('.inp-ref-desc').addEventListener('input', (e) => r.desc = e.target.value);

        container.appendChild(item);
      });
    },

    bindEvents() {
      if (DOM.tabFr) DOM.tabFr.addEventListener('click', () => this.switchLang('fr'));
      if (DOM.tabEn) DOM.tabEn.addEventListener('click', () => this.switchLang('en'));

      if (DOM.btnPitchBold) {
        DOM.btnPitchBold.addEventListener('click', (e) => {
          e.preventDefault();
          DOM.inpPitch.focus();
          Utils.formatText('bold');
        });
      }
      if (DOM.btnPitchItalic) {
        DOM.btnPitchItalic.addEventListener('click', (e) => {
          e.preventDefault();
          DOM.inpPitch.focus();
          Utils.formatText('italic');
        });
      }
      if (DOM.btnPitchClear) {
        DOM.btnPitchClear.addEventListener('click', (e) => {
          e.preventDefault();
          DOM.inpPitch.focus();
          Utils.formatText('removeFormat');
        });
      }

      if (DOM.btnEditorCrop) {
        DOM.btnEditorCrop.addEventListener('click', () => {
          if (State.cvData && State.cvData.photo_b64) {
            CropperController.open(`data:image/jpeg;base64,${State.cvData.photo_b64}`, (newB64) => {
              State.cvData.photo_b64 = newB64;
              this.updateAvatar();
              PreviewController.refresh();
            });
          } else {
            DOM.editorPhotoInput.click();
          }
        });
      }

      if (DOM.btnEditorChangePhoto) {
        DOM.btnEditorChangePhoto.addEventListener('click', () => DOM.editorPhotoInput.click());
      }

      if (DOM.editorPhotoInput) {
        DOM.editorPhotoInput.addEventListener('change', (e) => {
          if (e.target.files.length > 0) {
            const file = e.target.files[0];
            Utils.optimizeImage(file).then(({ dataUrl }) => {
              CropperController.open(dataUrl, (newB64) => {
                if (!State.cvData) State.cvData = {};
                State.cvData.photo_b64 = newB64;
                this.updateAvatar();
                PreviewController.refresh();
              });
            }).catch((err) => alert('Erreur traitement image : ' + err.message));
          }
        });
      }

      if (DOM.btnResetTop) {
        DOM.btnResetTop.addEventListener('click', () => {
          if (confirm('Voulez-vous recommencer pour un nouveau collaborateur ?')) {
            State.cvData = null;
            State.selectedCvFile = null;
            State.selectedPhotoFile = null;
            State.croppedPhotoB64 = null;
            State.rawPhotoDataUrl = null;

            DOM.cvFileInput.value = '';
            DOM.photoFileInput.value = '';
            DOM.photoPreviewImg.src = SVG_AVATAR_PLACEHOLDER;
            DOM.editorAvatarImg.src = SVG_AVATAR_PLACEHOLDER;
            DOM.cvDropzoneEmpty.classList.remove('hidden');
            DOM.cvDropzoneFilled.classList.add('hidden');
            DOM.photoDropzoneEmpty.classList.remove('hidden');
            DOM.photoDropzoneFilled.classList.add('hidden');
            DOM.cbInitialsOnly.checked = false;
            UploadController.updateStartButton();

            DOM.viewEditor.classList.add('hidden');
            DOM.viewLoading.classList.add('hidden');
            DOM.viewUpload.classList.remove('hidden');
            DOM.btnResetTop.classList.add('hidden');
          }
        });
      }
    }
  };

  // =========================================================================
  // 7. UPLOAD & JOB DISPATCH CONTROLLER
  // =========================================================================
  const UploadController = {
    handleCvFile(file) {
      State.selectedCvFile = file;
      DOM.cvFilename.textContent = file.name;
      DOM.cvFilesize.textContent = (file.size / (1024 * 1024)).toFixed(2) + ' MB';
      DOM.cvDropzoneEmpty.classList.add('hidden');
      DOM.cvDropzoneFilled.classList.remove('hidden');
      this.updateStartButton();
    },

    handlePhotoFile(file) {
      State.selectedPhotoFile = file;
      DOM.cbInitialsOnly.checked = false;
      DOM.photoFilename.textContent = file.name;

      Utils.optimizeImage(file).then(({ dataUrl, b64 }) => {
        State.rawPhotoDataUrl = dataUrl;
        State.croppedPhotoB64 = b64;
        DOM.photoPreviewImg.src = dataUrl;
        DOM.photoDropzoneEmpty.classList.add('hidden');
        DOM.photoDropzoneFilled.classList.remove('hidden');

        CropperController.open(dataUrl, (newB64, newDataUrl) => {
          State.croppedPhotoB64 = newB64;
          DOM.photoPreviewImg.src = newDataUrl;
        });
      }).catch((err) => alert('Erreur image : ' + err.message));
    },

    updateStartButton() {
      DOM.btnStartProcess.disabled = !State.selectedCvFile;
    },

    async startJob() {
      if (!State.selectedCvFile) return;

      DOM.viewUpload.classList.add('hidden');
      DOM.viewLoading.classList.remove('hidden');
      DOM.btnResetTop.classList.remove('hidden');

      const formData = new FormData();
      formData.append('cv_file', State.selectedCvFile);
      if (State.croppedPhotoB64 && !DOM.cbInitialsOnly.checked) {
        formData.append('photo_b64', State.croppedPhotoB64);
      } else if (State.selectedPhotoFile && !DOM.cbInitialsOnly.checked) {
        formData.append('photo_file', State.selectedPhotoFile);
      }
      formData.append('agency', DOM.selectAgency.value);

      DOM.progressBar.style.width = '15%';
      DOM.stepTitle.textContent = 'Envoi du document...';
      DOM.stepDesc.textContent = 'Initialisation du traitement IA sécurisé.';

      try {
        const queueRes = await fetch('/api/parse-cv-job', {
          method: 'POST',
          body: formData
        });

        if (!queueRes.ok) {
          const text = await queueRes.text();
          let msg = `Erreur (${queueRes.status})`;
          try {
            const j = JSON.parse(text);
            if (j.detail) msg = j.detail;
          } catch (_) {}
          throw new Error(msg);
        }

        const { job_id } = await queueRes.json();
        let attempts = 0;
        let completed = false;

        while (attempts < State.maxPollAttempts && !completed) {
          await new Promise(r => setTimeout(r, 1500));
          attempts++;

          const statusRes = await fetch(`/api/parse-cv-status/${job_id}`);
          if (!statusRes.ok) continue;

          const job = await statusRes.json();
          if (job.status === 'processing') {
            if (job.progress) DOM.progressBar.style.width = `${job.progress}%`;
            if (job.step) DOM.stepTitle.textContent = job.step;
            if (job.desc) DOM.stepDesc.textContent = job.desc;
          } else if (job.status === 'completed') {
            completed = true;
            State.cvData = job.data;
            DOM.progressBar.style.width = '100%';
            DOM.stepTitle.textContent = 'Finalisation de la mise en page...';
            DOM.stepDesc.textContent = 'CV prêt ! Ouverture de l\'éditeur.';
            setTimeout(() => {
              DOM.viewLoading.classList.add('hidden');
              DOM.viewEditor.classList.remove('hidden');
              EditorController.populate();
              PreviewController.refresh();
            }, 500);
            return;
          } else if (job.status === 'failed') {
            throw new Error(job.error || 'Erreur lors du traitement du CV.');
          }
        }

        if (!completed) {
          throw new Error('Délai d\'attente dépassé lors de la génération.');
        }

      } catch (err) {
        alert('Erreur : ' + err.message);
        DOM.viewLoading.classList.add('hidden');
        DOM.viewUpload.classList.remove('hidden');
        DOM.btnResetTop.classList.add('hidden');
      }
    },

    bindEvents() {
      // CV File
      DOM.cvDropzone.addEventListener('click', (e) => {
        if (e.target.closest('#btn-remove-cv')) return;
        DOM.cvFileInput.click();
      });
      DOM.cvFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) this.handleCvFile(e.target.files[0]);
      });
      DOM.cvDropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        DOM.cvDropzone.classList.add('border-burgeap-blue', 'bg-blue-50/50');
      });
      DOM.cvDropzone.addEventListener('dragleave', () => {
        DOM.cvDropzone.classList.remove('border-burgeap-blue', 'bg-blue-50/50');
      });
      DOM.cvDropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        DOM.cvDropzone.classList.remove('border-burgeap-blue', 'bg-blue-50/50');
        if (e.dataTransfer.files.length > 0) this.handleCvFile(e.dataTransfer.files[0]);
      });
      DOM.btnRemoveCv.addEventListener('click', (e) => {
        e.stopPropagation();
        State.selectedCvFile = null;
        DOM.cvFileInput.value = '';
        DOM.cvDropzoneEmpty.classList.remove('hidden');
        DOM.cvDropzoneFilled.classList.add('hidden');
        this.updateStartButton();
      });

      // Photo File
      DOM.photoDropzone.addEventListener('click', (e) => {
        if (e.target.closest('#btn-remove-photo')) return;
        DOM.photoFileInput.click();
      });
      DOM.photoFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) this.handlePhotoFile(e.target.files[0]);
      });
      DOM.btnRemovePhoto.addEventListener('click', (e) => {
        e.stopPropagation();
        State.selectedPhotoFile = null;
        DOM.photoFileInput.value = '';
        DOM.photoPreviewImg.src = SVG_AVATAR_PLACEHOLDER;
        DOM.photoDropzoneEmpty.classList.remove('hidden');
        DOM.photoDropzoneFilled.classList.add('hidden');
      });
      DOM.cbInitialsOnly.addEventListener('change', () => {
        if (DOM.cbInitialsOnly.checked) {
          State.selectedPhotoFile = null;
          DOM.photoFileInput.value = '';
          DOM.photoPreviewImg.src = SVG_AVATAR_PLACEHOLDER;
          DOM.photoDropzoneEmpty.classList.remove('hidden');
          DOM.photoDropzoneFilled.classList.add('hidden');
        }
      });
      if (DOM.btnCropPhotoV1) {
        DOM.btnCropPhotoV1.addEventListener('click', (e) => {
          e.stopPropagation();
          if (State.rawPhotoDataUrl) {
            CropperController.open(State.rawPhotoDataUrl, (newB64, newDataUrl) => {
              State.croppedPhotoB64 = newB64;
              DOM.photoPreviewImg.src = newDataUrl;
            });
          }
        });
      }

      // Start Button
      DOM.btnStartProcess.addEventListener('click', () => this.startJob());
    }
  };

  // =========================================================================
  // 8. APPLICATION BOOTSTRAP
  // =========================================================================
  document.addEventListener('DOMContentLoaded', () => {
    ThemeController.init();
    CropperController.bindEvents();
    PreviewController.bindEvents();
    EditorController.bindEvents();
    UploadController.bindEvents();
  });

  // Expose for testing and automation
  window.__App = {
    State,
    DOM,
    ThemeController,
    PreviewController,
    EditorController,
    UploadController,
    CropperController
  };

})();

