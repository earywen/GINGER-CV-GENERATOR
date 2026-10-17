/**
 * Modals Controller (About & Custom Confirm Modal)
 * Provides elegant, non-blocking UI dialogs styled according to Ginger Burgeap charte.
 */
import { DOM } from './dom.js';
import { Utils } from './utils.js';
import { State } from './state.js';

export const AboutController = {
  init() {
    if (!DOM.btnAbout || !DOM.modalAbout) return;

    DOM.btnAbout.addEventListener('click', () => this.open());
    if (DOM.btnAboutClose) DOM.btnAboutClose.addEventListener('click', () => this.close());
    if (DOM.btnAboutFooterClose) DOM.btnAboutFooterClose.addEventListener('click', () => this.close());

    // Close on backdrop click (click outside modal content)
    DOM.modalAbout.addEventListener('click', (e) => {
      if (e.target === DOM.modalAbout) {
        this.close();
      }
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !DOM.modalAbout.classList.contains('hidden')) {
        this.close();
      }
    });

    this.bindTabs();
  },

  open() {
    DOM.modalAbout.classList.remove('hidden');
  },

  close() {
    DOM.modalAbout.classList.add('hidden');
  },

  bindTabs() {
    const tabs = [
      { btn: DOM.tabAboutDesc, panel: DOM.panelAboutDesc },
      { btn: DOM.tabAboutGuide, panel: DOM.panelAboutGuide },
      { btn: DOM.tabAboutCredits, panel: DOM.panelAboutCredits }
    ];

    tabs.forEach(({ btn, panel }) => {
      if (!btn || !panel) return;
      btn.addEventListener('click', () => {
        tabs.forEach(t => {
          if (t.btn && t.panel) {
            const isActive = (t.btn === btn);
            t.panel.classList.toggle('hidden', !isActive);
            t.btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
            if (isActive) {
              t.btn.className = 'py-3 px-3.5 border-b-2 border-burgeap-blue dark:border-burgeap-green text-burgeap-blue dark:text-burgeap-green font-bold flex items-center gap-2 transition cursor-pointer';
            } else {
              t.btn.className = 'py-3 px-3.5 border-b-2 border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 flex items-center gap-2 transition cursor-pointer';
            }
          }
        });
      });
    });
  }
};

export const ConfirmModal = {
  _resolve: null,

  init() {
    if (!DOM.modalConfirm) return;

    if (DOM.modalConfirmBtnCancel) {
      DOM.modalConfirmBtnCancel.addEventListener('click', () => this.respond(false));
    }
    if (DOM.modalConfirmBtnAccept) {
      DOM.modalConfirmBtnAccept.addEventListener('click', () => this.respond(true));
    }

    DOM.modalConfirm.addEventListener('click', (e) => {
      if (e.target === DOM.modalConfirm) {
        this.respond(false);
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && DOM.modalConfirm && !DOM.modalConfirm.classList.contains('hidden')) {
        this.respond(false);
      }
    });
  },

  respond(confirmed) {
    if (DOM.modalConfirm) DOM.modalConfirm.classList.add('hidden');
    if (this._resolve) {
      this._resolve(confirmed);
      this._resolve = null;
    }
  },

  show({
    title = 'Nouveau collaborateur',
    message = 'Voulez-vous recommencer pour un nouveau collaborateur ? Le brouillon actuel sera réinitialisé.',
    acceptText = 'Recommencer',
    cancelText = 'Annuler',
    danger = false,
    icon = 'fa-solid fa-arrows-rotate'
  } = {}) {
    return new Promise((resolve) => {
      this._resolve = resolve;
      if (!DOM.modalConfirm) {
        resolve(window.confirm(message));
        return;
      }

      if (DOM.modalConfirmTitle) DOM.modalConfirmTitle.textContent = title;
      if (DOM.modalConfirmMessage) DOM.modalConfirmMessage.textContent = message;
      if (DOM.modalConfirmAcceptText) DOM.modalConfirmAcceptText.textContent = acceptText;
      if (DOM.modalConfirmCancelText) DOM.modalConfirmCancelText.textContent = cancelText;
      if (DOM.modalConfirmIcon) DOM.modalConfirmIcon.className = icon;

      if (danger) {
        if (DOM.modalConfirmBtnAccept) {
          DOM.modalConfirmBtnAccept.className = 'px-4 py-2 rounded-xl text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 shadow-sm transition flex items-center gap-1.5 focus:outline-none focus:ring-2 focus:ring-rose-400';
        }
        if (DOM.modalConfirmIconWrap) {
          DOM.modalConfirmIconWrap.className = 'w-10 h-10 rounded-xl bg-rose-100 dark:bg-rose-950/50 text-rose-600 dark:text-rose-400 flex items-center justify-center shrink-0 text-base border border-rose-200 dark:border-rose-800/60 mt-0.5';
        }
      } else {
        if (DOM.modalConfirmBtnAccept) {
          DOM.modalConfirmBtnAccept.className = 'px-4 py-2 rounded-xl text-xs font-bold text-white bg-burgeap-blue hover:bg-burgeap-dark shadow-sm transition flex items-center gap-1.5 focus:outline-none focus:ring-2 focus:ring-burgeap-green';
        }
        if (DOM.modalConfirmIconWrap) {
          DOM.modalConfirmIconWrap.className = 'w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-950/50 text-amber-600 dark:text-amber-400 flex items-center justify-center shrink-0 text-base border border-amber-200 dark:border-amber-800/60 mt-0.5';
        }
      }

      DOM.modalConfirm.classList.remove('hidden');
      if (DOM.modalConfirmBtnAccept) DOM.modalConfirmBtnAccept.focus();
    });
  }
};

export const FeedbackController = {
  category: 'bug',
  screenshotB64: null,
  isSubmitting: false,

  init() {
    if (!DOM.btnFeedback || !DOM.modalFeedback) return;

    DOM.btnFeedback.addEventListener('click', () => this.open());
    if (DOM.btnFeedbackClose) DOM.btnFeedbackClose.addEventListener('click', () => this.close());
    if (DOM.btnFeedbackCancel) DOM.btnFeedbackCancel.addEventListener('click', () => this.close());

    // Close on backdrop click
    DOM.modalFeedback.addEventListener('click', (e) => {
      if (e.target === DOM.modalFeedback) {
        this.close();
      }
    });

    // Close on Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && DOM.modalFeedback && !DOM.modalFeedback.classList.contains('hidden')) {
        this.close();
      }
    });

    this.bindPills();
    this.bindScreenshot();
    this.bindSubmit();
  },

  open() {
    if (!DOM.modalFeedback) return;
    DOM.modalFeedback.classList.remove('hidden');
    // Focus message field
    setTimeout(() => {
      if (DOM.feedbackMessage) DOM.feedbackMessage.focus();
    }, 50);
  },

  close() {
    if (!DOM.modalFeedback) return;
    DOM.modalFeedback.classList.add('hidden');
  },

  resetForm() {
    this.setCategory('bug');
    this.removeScreenshot();
    if (DOM.feedbackMessage) DOM.feedbackMessage.value = '';
    if (DOM.feedbackContact) DOM.feedbackContact.value = '';
    if (DOM.feedbackIncludeDiag) DOM.feedbackIncludeDiag.checked = true;
    if (DOM.feedbackScreenshotInput) DOM.feedbackScreenshotInput.value = '';
  },

  setCategory(cat) {
    this.category = cat;
    const pills = [
      { el: DOM.feedbackPillBug, key: 'bug', activeClasses: 'border-rose-500 bg-rose-50 text-rose-700 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-500/60 shadow-xs' },
      { el: DOM.feedbackPillIdea, key: 'idea', activeClasses: 'border-amber-500 bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-500/60 shadow-xs' },
      { el: DOM.feedbackPillOther, key: 'other', activeClasses: 'border-burgeap-blue bg-blue-50 text-burgeap-blue dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-500/60 shadow-xs' }
    ];
    const defaultClasses = 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 text-slate-600 dark:text-slate-300 hover:border-slate-400';

    pills.forEach(({ el, key, activeClasses }) => {
      if (!el) return;
      const isActive = (key === cat);
      el.className = `feedback-cat-pill py-2 px-3 rounded-xl border text-xs font-semibold flex items-center justify-center gap-1.5 transition cursor-pointer ${isActive ? activeClasses : defaultClasses}`;
    });
  },

  bindPills() {
    if (DOM.feedbackPillBug) DOM.feedbackPillBug.addEventListener('click', () => this.setCategory('bug'));
    if (DOM.feedbackPillIdea) DOM.feedbackPillIdea.addEventListener('click', () => this.setCategory('idea'));
    if (DOM.feedbackPillOther) DOM.feedbackPillOther.addEventListener('click', () => this.setCategory('other'));
  },

  bindScreenshot() {
    const dropzone = DOM.feedbackScreenshotDropzone;
    const fileInput = DOM.feedbackScreenshotInput;
    const removeBtn = DOM.feedbackScreenshotRemove;

    if (dropzone && fileInput) {
      dropzone.addEventListener('click', () => fileInput.click());
      
      fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
          this.handleImageFile(e.target.files[0]);
        }
      });

      // Drag & drop
      ['dragenter', 'dragover'].forEach(name => {
        dropzone.addEventListener(name, (e) => {
          e.preventDefault();
          e.stopPropagation();
          dropzone.classList.add('border-burgeap-blue', 'bg-blue-50/50', 'dark:bg-slate-800');
        });
      });

      ['dragleave', 'drop'].forEach(name => {
        dropzone.addEventListener(name, (e) => {
          e.preventDefault();
          e.stopPropagation();
          dropzone.classList.remove('border-burgeap-blue', 'bg-blue-50/50', 'dark:bg-slate-800');
        });
      });

      dropzone.addEventListener('drop', (e) => {
        if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
          this.handleImageFile(e.dataTransfer.files[0]);
        }
      });
    }

    if (removeBtn) {
      removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.removeScreenshot();
      });
    }

    // Paste handler when modal is open
    document.addEventListener('paste', (e) => {
      if (!DOM.modalFeedback || DOM.modalFeedback.classList.contains('hidden')) return;
      const items = e.clipboardData?.items;
      if (!items) return;
      for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
          const file = items[i].getAsFile();
          if (file) {
            e.preventDefault();
            this.handleImageFile(file);
            break;
          }
        }
      }
    });
  },

  async handleImageFile(file) {
    if (!file.type.startsWith('image/')) {
      Utils.toast('Format d\'image non supporté (PNG, JPG, WebP uniquement).', 'warning');
      return;
    }
    try {
      const { dataUrl, b64 } = await Utils.optimizeImage(file, 1400);
      this.screenshotB64 = b64;
      if (DOM.feedbackScreenshotImg) DOM.feedbackScreenshotImg.src = dataUrl;
      if (DOM.feedbackScreenshotDropzone) DOM.feedbackScreenshotDropzone.classList.add('hidden');
      if (DOM.feedbackScreenshotPreview) DOM.feedbackScreenshotPreview.classList.remove('hidden');
    } catch (err) {
      Utils.toast('Impossible de traiter la capture d\'écran.', 'error');
    }
  },

  removeScreenshot() {
    this.screenshotB64 = null;
    if (DOM.feedbackScreenshotInput) DOM.feedbackScreenshotInput.value = '';
    if (DOM.feedbackScreenshotImg) DOM.feedbackScreenshotImg.src = '';
    if (DOM.feedbackScreenshotPreview) DOM.feedbackScreenshotPreview.classList.add('hidden');
    if (DOM.feedbackScreenshotDropzone) DOM.feedbackScreenshotDropzone.classList.remove('hidden');
  },

  collectDiagnostics() {
    const isEditorActive = DOM.viewEditor && !DOM.viewEditor.classList.contains('hidden');
    return {
      userAgent: navigator.userAgent,
      language: navigator.language,
      platform: navigator.platform,
      screen: {
        availWidth: window.screen?.availWidth,
        availHeight: window.screen?.availHeight,
        windowWidth: window.innerWidth,
        windowHeight: window.innerHeight,
        pixelRatio: window.devicePixelRatio
      },
      activeStage: isEditorActive ? 'editor' : 'upload',
      hasLoadedCv: !!(State && State.cvData),
      appVersion: '2.6.0',
      timestamp: new Date().toISOString()
    };
  },

  bindSubmit() {
    if (!DOM.btnFeedbackSubmit) return;

    DOM.btnFeedbackSubmit.addEventListener('click', async () => {
      if (this.isSubmitting) return;

      const message = DOM.feedbackMessage ? DOM.feedbackMessage.value.trim() : '';
      if (!message || message.length < 3) {
        if (DOM.feedbackMessage) {
          DOM.feedbackMessage.focus();
          DOM.feedbackMessage.classList.add('ring-2', 'ring-red-500');
          setTimeout(() => DOM.feedbackMessage.classList.remove('ring-2', 'ring-red-500'), 2000);
        }
        Utils.toast('Veuillez saisir une description pour votre retour (minimum 3 caractères).', 'warning');
        return;
      }

      const contact = DOM.feedbackContact ? DOM.feedbackContact.value.trim() : '';
      const includeDiag = DOM.feedbackIncludeDiag ? DOM.feedbackIncludeDiag.checked : true;
      const diagnostics = includeDiag ? this.collectDiagnostics() : null;

      const payload = {
        category: this.category,
        message,
        contact: contact || null,
        include_diagnostics: includeDiag,
        diagnostics,
        screenshot_b64: this.screenshotB64
      };

      this.setLoading(true);

      try {
        const res = await fetch('/api/feedback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || 'Erreur serveur lors de la transmission.');
        }

        const data = await res.json();
        this.close();
        this.resetForm();
        Utils.toast(data.message || 'Merci pour votre retour ! Transmis avec succès.', 'info');
      } catch (err) {
        console.error('Feedback submit error:', err);
        Utils.toast(err.message || 'Échec de l\'envoi du retour. Veuillez réessayer.', 'error');
      } finally {
        this.setLoading(false);
      }
    });
  },

  setLoading(isLoading) {
    this.isSubmitting = isLoading;
    if (DOM.btnFeedbackSubmit) {
      DOM.btnFeedbackSubmit.disabled = isLoading;
      DOM.btnFeedbackSubmit.classList.toggle('opacity-70', isLoading);
      DOM.btnFeedbackSubmit.classList.toggle('cursor-not-allowed', isLoading);
    }
    if (DOM.btnFeedbackSubmitIcon) {
      DOM.btnFeedbackSubmitIcon.className = isLoading
        ? 'fa-solid fa-spinner fa-spin text-burgeap-green'
        : 'fa-solid fa-paper-plane text-burgeap-green';
    }
    if (DOM.btnFeedbackSubmitText) {
      DOM.btnFeedbackSubmitText.textContent = isLoading ? 'Envoi en cours...' : 'Envoyer le retour';
    }
  }
};
