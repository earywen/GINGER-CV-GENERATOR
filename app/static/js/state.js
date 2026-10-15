/**
 * Application State
 * Centralized reactive model for Ginger Burgeap CV Generator 2026.
 */

export const State = {
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
