/**
 * Ginger Burgeap CV Generator 2026 - Main Application Entrypoint
 * Orchestrates modules, event wiring, and initial state restoration.
 */
import { State } from './state.js';
import { DOM } from './dom.js';
import { ThemeController } from './theme.js';
import { CropperController } from './cropper.js';
import { PreviewController } from './viewer.js';
import { EditorController } from './editor.js';
import { UploadController } from './jobs.js';
import { SessionController } from './session.js';
import { AboutController, ConfirmModal } from './modals.js';

function initApp() {
  ThemeController.init();
  CropperController.bindEvents();

  // Wire Editor Controller handlers
  EditorController.setHandlers({
    onPreviewRefresh: (silent) => PreviewController.refresh(silent),
    onScheduleAutoSave: () => SessionController.scheduleAutoSave(),
    onOpenCropper: (src, callback) => CropperController.open(src, callback)
  });
  EditorController.bindEvents();

  // Wire Preview Controller
  PreviewController.bindEvents(() => EditorController.saveCurrentForm());

  // Wire Upload Controller handlers
  UploadController.setHandlers({
    onJobSuccess: () => {
      EditorController.populate();
      PreviewController.refresh();
      SessionController.saveImmediately();
    },
    onOpenCropper: (src, callback) => CropperController.open(src, callback)
  });
  UploadController.bindEvents();

  // Wire Session Controller
  SessionController.init({
    onSaveForm: () => EditorController.saveCurrentForm(),
    onRestore: (lang) => {
      EditorController.switchLang(lang, false);
      PreviewController.refresh();
    },
    onClear: () => {
      UploadController.updateStartButton();
    }
  });

  // Wire Modals
  AboutController.init();
  ConfirmModal.init();

  // Header reset button
  if (DOM.btnResetTop) {
    DOM.btnResetTop.addEventListener('click', async () => {
      const confirmed = await ConfirmModal.show({
        title: 'Nouveau collaborateur',
        message: 'Voulez-vous recommencer pour un nouveau collaborateur ? Le brouillon actuel sera réinitialisé.',
        acceptText: 'Recommencer',
        cancelText: 'Annuler',
        danger: false,
        icon: 'fa-solid fa-arrows-rotate'
      });
      if (confirmed) {
        SessionController.clearSession();
      }
    });
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}

// Global debug exposure for testing and test automation
window.__App = {
  State,
  DOM,
  ThemeController,
  PreviewController,
  EditorController,
  UploadController,
  CropperController,
  SessionController,
  AboutController,
  ConfirmModal
};
