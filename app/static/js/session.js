/**
 * Session & Draft Controller
 * Manages auto-save debouncing, localStorage caching, and server-side draft sync.
 */
import { State } from './state.js';
import { DOM } from './dom.js';
import { SVG_AVATAR_PLACEHOLDER } from './utils.js';

export const SessionController = {
  STORAGE_KEY: 'burgeap_cv_draft_v1',
  saveTimeout: null,
  _onSaveForm: null,
  _onRestore: null,
  _onClear: null,

  init({ onSaveForm, onRestore, onClear }) {
    this._onSaveForm = onSaveForm;
    this._onRestore = onRestore;
    this._onClear = onClear;

    if (DOM.btnSessionToastClose) {
      DOM.btnSessionToastClose.addEventListener('click', () => {
        if (DOM.sessionToast) DOM.sessionToast.classList.add('hidden');
      });
    }

    // Check and restore draft on startup
    this.checkAndRestore();

    // Ensure immediate sync when window is closing or hidden
    window.addEventListener('beforeunload', () => {
      this.saveImmediately();
    });
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        this.saveImmediately();
      }
    });
  },

  setSaveStatus(status) {
    if (!DOM.saveStatusText) return;
    if (status === 'saving') {
      DOM.saveStatusText.textContent = 'Enregistrement...';
      if (DOM.saveStatusIndicator) {
        DOM.saveStatusIndicator.className = 'text-[11px] font-medium text-amber-600 dark:text-amber-400 flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-amber-100/60 dark:bg-amber-900/30 select-none transition';
        const icon = DOM.saveStatusIndicator.querySelector('i');
        if (icon) icon.className = 'fa-solid fa-spinner animate-spin text-[11px]';
      }
    } else if (status === 'saved') {
      DOM.saveStatusText.textContent = 'Sauvegardé';
      if (DOM.saveStatusIndicator) {
        DOM.saveStatusIndicator.className = 'text-[11px] font-medium text-slate-500 dark:text-slate-400 flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-200/50 dark:bg-slate-700/50 select-none transition';
        const icon = DOM.saveStatusIndicator.querySelector('i');
        if (icon) icon.className = 'fa-solid fa-cloud-arrow-up text-burgeap-green text-[11px]';
      }
    }
  },

  debouncedSave() {
    this.setSaveStatus('saving');
    clearTimeout(this.saveTimeout);
    this.saveTimeout = setTimeout(() => {
      this.saveImmediately();
    }, 400);
  },

  scheduleAutoSave() {
    this.debouncedSave();
  },

  saveImmediately() {
    if (!State.cvData) return;
    if (this._onSaveForm) this._onSaveForm();

    const payload = {
      cvData: State.cvData,
      currentLang: State.currentLang,
      previewLang: State.previewLang,
      updatedAt: Date.now()
    };

    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(payload));
    } catch (e) {
      console.warn('LocalStorage save failed:', e);
    }

    this.setSaveStatus('saved');

    // Asynchronously sync to backend session cookie without blocking
    fetch('/api/session/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ draft: payload })
    }).catch(() => {});
  },

  async checkAndRestore() {
    let draftPayload = null;

    // 1. Try LocalStorage
    try {
      const raw = localStorage.getItem(this.STORAGE_KEY);
      if (raw) {
        draftPayload = JSON.parse(raw);
      }
    } catch (e) {
      console.warn('Error reading localStorage:', e);
    }

    // 2. If nothing in LocalStorage, check server session cookie
    if (!draftPayload || !draftPayload.cvData) {
      try {
        const res = await fetch('/api/session/draft');
        if (res.ok) {
          const data = await res.json();
          if (data.has_draft && data.draft) {
            draftPayload = data.draft;
          }
        }
      } catch (e) {
        console.warn('Error checking server session:', e);
      }
    }

    // 3. If draft exists, restore it!
    if (draftPayload && draftPayload.cvData) {
      State.cvData = draftPayload.cvData;
      State.currentLang = draftPayload.currentLang || 'fr';
      State.previewLang = draftPayload.previewLang || 'fr';

      DOM.viewUpload.classList.add('hidden');
      DOM.viewLoading.classList.add('hidden');
      DOM.viewEditor.classList.remove('hidden');
      DOM.btnResetTop.classList.remove('hidden');

      if (this._onRestore) {
        this._onRestore(State.currentLang);
      }

      this.showToast('Brouillon restauré automatiquement depuis votre session.');
      this.setSaveStatus('saved');
    }
  },

  showToast(message) {
    if (!DOM.sessionToast) return;
    if (DOM.sessionToastMsg) DOM.sessionToastMsg.textContent = message;
    DOM.sessionToast.classList.remove('hidden');
    setTimeout(() => {
      if (DOM.sessionToast) DOM.sessionToast.classList.add('hidden');
    }, 4500);
  },

  clearSession() {
    try {
      localStorage.removeItem(this.STORAGE_KEY);
    } catch (e) {}

    fetch('/api/session/draft', { method: 'DELETE' }).catch(() => {});
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

    if (this._onClear) this._onClear();

    DOM.viewEditor.classList.add('hidden');
    DOM.viewLoading.classList.add('hidden');
    DOM.viewUpload.classList.remove('hidden');
    DOM.btnResetTop.classList.add('hidden');
    this.showToast('Brouillon effacé. Prêt pour un nouveau CV.');
  }
};
