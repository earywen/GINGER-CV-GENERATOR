/**
 * Cropper Controller
 * Integrates Cropper.js for circular avatar and studio bust portrait cropping.
 */
import { DOM } from './dom.js';

export const CropperController = {
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
      // Cropper is loaded globally via cropper.min.js
      this.cropperInstance = new window.Cropper(DOM.cropperImage, {
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
