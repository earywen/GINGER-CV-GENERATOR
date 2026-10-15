/**
 * Frontend Utilities
 * Formatting, image downscaling, and DOM helpers.
 */

export const SVG_AVATAR_PLACEHOLDER = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'%3E%3Ccircle cx='24' cy='24' r='24' fill='%2313375f'/%3E%3C/svg%3E";

export const Utils = {
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
