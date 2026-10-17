/**
 * Modals Controller (About & Custom Confirm Modal)
 * Provides elegant, non-blocking UI dialogs styled according to Ginger Burgeap charte.
 */
import { DOM } from './dom.js';

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
