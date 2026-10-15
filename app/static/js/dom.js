/**
 * DOM Element Registry
 * Centralized, lazy access to DOM nodes for Ginger Burgeap CV Generator 2026.
 */

const get = (id) => document.getElementById(id);

export const DOM = {
  // Views
  get viewUpload() { return get('view-upload'); },
  get viewLoading() { return get('view-loading'); },
  get viewEditor() { return get('view-editor'); },
  get btnResetTop() { return get('btn-reset-top'); },
  get btnThemeToggle() { return get('btn-theme-toggle'); },

  // CV Dropzone
  get cvDropzone() { return get('cv-dropzone'); },
  get cvFileInput() { return get('cv-file-input'); },
  get cvDropzoneEmpty() { return get('cv-dropzone-empty'); },
  get cvDropzoneFilled() { return get('cv-dropzone-filled'); },
  get cvFilename() { return get('cv-filename'); },
  get cvFilesize() { return get('cv-filesize'); },
  get btnRemoveCv() { return get('btn-remove-cv'); },

  // Photo Dropzone
  get photoDropzone() { return get('photo-dropzone'); },
  get photoFileInput() { return get('photo-file-input'); },
  get photoDropzoneEmpty() { return get('photo-dropzone-empty'); },
  get photoDropzoneFilled() { return get('photo-dropzone-filled'); },
  get photoPreviewImg() { return get('photo-preview-img'); },
  get photoFilename() { return get('photo-filename'); },
  get btnRemovePhoto() { return get('btn-remove-photo'); },
  get cbInitialsOnly() { return get('cb-initials-only'); },
  get btnCropPhotoV1() { return get('btn-crop-photo-v1'); },

  // Configuration & Action
  get selectAgency() { return get('select-agency'); },
  get btnStartProcess() { return get('btn-start-process'); },

  // Loading Screen
  get stepTitle() { return get('loading-step-title'); },
  get stepDesc() { return get('loading-step-desc'); },
  get progressBar() { return get('loading-progress-bar'); },

  // Editor Tabs & Actions
  get tabFr() { return get('tab-fr'); },
  get tabEn() { return get('tab-en'); },
  get btnRefreshPreview() { return get('btn-refresh-preview'); },
  get btnDownloadActive() { return get('btn-download-active'); },
  get btnDownloadZip() { return get('btn-download-zip'); },
  get lblDownloadLang() { return get('lbl-download-lang'); },
  get chkShowBadges() { return get('chk-show-badges'); },

  // Live Viewer & Interactive Canvas
  get rightColumnContainer() { return get('right-column-container'); },
  get pdfViewportContainer() { return get('pdf-viewport-container'); },
  get pdfStage() { return get('pdf-stage'); },
  get pdfSheetContainer() { return get('pdf-sheet-container'); },
  get pdfShadowHost() { return get('pdf-shadow-host'); },
  get pdfPanOverlay() { return get('pdf-pan-overlay'); },
  get pdfLoadingSpinner() { return get('pdf-loading-spinner'); },
  get btnToolHand() { return get('btn-tool-hand'); },
  get btnToolSelect() { return get('btn-tool-select'); },
  get btnPage1() { return get('btn-page-1'); },
  get btnPage2() { return get('btn-page-2'); },
  get btnZoomIn() { return get('btn-zoom-in'); },
  get btnZoomOut() { return get('btn-zoom-out'); },
  get btnZoomWidth() { return get('btn-zoom-width'); },
  get btnZoomFit() { return get('btn-zoom-fit'); },
  get btnZoomReset() { return get('btn-zoom-reset'); },
  get btnFullscreen() { return get('btn-fullscreen'); },
  get btnOpenTab() { return get('btn-open-tab'); },
  get lblZoomVal() { return get('lbl-zoom-val'); },

  // Rich Text Pitch
  get inpPitch() { return get('inp-pitch'); },
  get btnPitchBold() { return get('btn-pitch-bold'); },
  get btnPitchItalic() { return get('btn-pitch-italic'); },
  get btnPitchClear() { return get('btn-pitch-clear'); },

  // Editor Avatar
  get editorAvatarImg() { return get('editor-avatar-img'); },
  get editorAvatarInitials() { return get('editor-avatar-initials'); },
  get editorPhotoStatus() { return get('editor-photo-status'); },
  get editorPhotoInput() { return get('editor-photo-input'); },
  get btnEditorCrop() { return get('btn-editor-crop'); },
  get btnEditorChangePhoto() { return get('btn-editor-change-photo'); },

  // Cropper Modal
  get modalCropper() { return get('modal-cropper'); },
  get cropperImage() { return get('cropper-image'); },
  get btnCropperClose() { return get('btn-cropper-close'); },
  get btnCropCancel() { return get('btn-crop-cancel'); },
  get btnCropReset() { return get('btn-crop-reset'); },
  get btnCropApply() { return get('btn-crop-apply'); },
  get btnCropZoomIn() { return get('btn-crop-zoom-in'); },
  get btnCropZoomOut() { return get('btn-crop-zoom-out'); },
  get cropZoomSlider() { return get('crop-zoom-slider'); },
  get btnCropRotateLeft() { return get('btn-crop-rotate-left'); },
  get btnCropRotateRight() { return get('btn-crop-rotate-right'); },

  // Session & Persistence Indicators
  get saveStatusIndicator() { return get('save-status-indicator'); },
  get saveStatusText() { return get('save-status-text'); },
  get sessionToast() { return get('session-toast'); },
  get sessionToastMsg() { return get('session-toast-msg'); },
  get btnSessionToastClose() { return get('btn-session-toast-close'); },

  // About Modal
  get btnAbout() { return get('btn-about'); },
  get modalAbout() { return get('modal-about'); },
  get btnAboutClose() { return get('btn-about-close'); },
  get btnAboutFooterClose() { return get('btn-about-footer-close'); },
  get tabAboutDesc() { return get('tab-about-desc'); },
  get tabAboutGuide() { return get('tab-about-guide'); },
  get tabAboutCredits() { return get('tab-about-credits'); },
  get panelAboutDesc() { return get('panel-about-desc'); },
  get panelAboutGuide() { return get('panel-about-guide'); },
  get panelAboutCredits() { return get('panel-about-credits'); }
};
