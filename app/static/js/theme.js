/**
 * Theme Controller
 * Manages Dark Mode and Light Mode switching with localStorage persistence.
 */
import { DOM } from './dom.js';

export const ThemeController = {
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
