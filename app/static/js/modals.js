/**
 * About & Help Modal Controller
 * Handles user documentation, developer credits, and changelog modal.
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
