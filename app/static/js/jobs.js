/**
 * Upload & Job Dispatch Controller
 * Handles drag-and-drop file ingestion, photo preparation, and background job polling.
 */
import { State } from './state.js';
import { DOM } from './dom.js';
import { Utils, SVG_AVATAR_PLACEHOLDER } from './utils.js';

export const UploadController = {
  _onJobSuccess: null,
  _onOpenCropper: null,

  setHandlers({ onJobSuccess, onOpenCropper }) {
    this._onJobSuccess = onJobSuccess;
    this._onOpenCropper = onOpenCropper;
  },

  handleCvFile(file) {
    State.selectedCvFile = file;
    DOM.cvFilename.textContent = file.name;
    DOM.cvFilesize.textContent = (file.size / (1024 * 1024)).toFixed(2) + ' MB';
    DOM.cvDropzoneEmpty.classList.add('hidden');
    DOM.cvDropzoneFilled.classList.remove('hidden');
    this.updateStartButton();
  },

  handlePhotoFile(file) {
    State.selectedPhotoFile = file;
    DOM.cbInitialsOnly.checked = false;
    DOM.photoFilename.textContent = file.name;

    Utils.optimizeImage(file).then(({ dataUrl, b64 }) => {
      State.rawPhotoDataUrl = dataUrl;
      State.croppedPhotoB64 = b64;
      DOM.photoPreviewImg.src = dataUrl;
      DOM.photoDropzoneEmpty.classList.add('hidden');
      DOM.photoDropzoneFilled.classList.remove('hidden');

      if (this._onOpenCropper) {
        this._onOpenCropper(dataUrl, (newB64, newDataUrl) => {
          State.croppedPhotoB64 = newB64;
          DOM.photoPreviewImg.src = newDataUrl;
        });
      }
    }).catch((err) => Utils.toast('Erreur image : ' + err.message, 'error'));
  },

  updateStartButton() {
    DOM.btnStartProcess.disabled = !State.selectedCvFile;
  },

  async startJob() {
    if (!State.selectedCvFile) return;

    DOM.viewUpload.classList.add('hidden');
    DOM.viewLoading.classList.remove('hidden');
    DOM.btnResetTop.classList.remove('hidden');

    const formData = new FormData();
    formData.append('cv_file', State.selectedCvFile);
    if (State.croppedPhotoB64 && !DOM.cbInitialsOnly.checked) {
      formData.append('photo_b64', State.croppedPhotoB64);
    } else if (State.selectedPhotoFile && !DOM.cbInitialsOnly.checked) {
      formData.append('photo_file', State.selectedPhotoFile);
    }
    formData.append('agency', DOM.selectAgency.value);

    DOM.progressBar.style.width = '15%';
    DOM.stepTitle.textContent = 'Envoi du document...';
    DOM.stepDesc.textContent = 'Initialisation du traitement IA sécurisé.';

    try {
      const queueRes = await fetch('/api/parse-cv-job', {
        method: 'POST',
        body: formData
      });

      if (!queueRes.ok) {
        const text = await queueRes.text();
        let msg = `Erreur (${queueRes.status})`;
        try {
          const j = JSON.parse(text);
          if (j.detail) msg = j.detail;
        } catch (_) {}
        throw new Error(msg);
      }

      const { job_id } = await queueRes.json();
      let attempts = 0;
      let completed = false;

      while (attempts < State.maxPollAttempts && !completed) {
        await new Promise(r => setTimeout(r, 1500));
        attempts++;

        const statusRes = await fetch(`/api/parse-cv-status/${job_id}`);
        if (!statusRes.ok) continue;

        const job = await statusRes.json();
        if (job.status === 'processing') {
          if (job.progress) DOM.progressBar.style.width = `${job.progress}%`;
          if (job.step) DOM.stepTitle.textContent = job.step;
          if (job.desc) DOM.stepDesc.textContent = job.desc;
        } else if (job.status === 'completed') {
          completed = true;
          State.cvData = job.data;
          DOM.progressBar.style.width = '100%';
          DOM.stepTitle.textContent = 'Finalisation de la mise en page...';
          DOM.stepDesc.textContent = 'CV prêt ! Ouverture de l\'éditeur.';
          setTimeout(() => {
            DOM.viewLoading.classList.add('hidden');
            DOM.viewEditor.classList.remove('hidden');
            DOM.btnResetTop.classList.remove('hidden');
            if (this._onJobSuccess) this._onJobSuccess();
          }, 500);
          return;
        } else if (job.status === 'failed') {
          throw new Error(job.error || 'Erreur lors du traitement du CV.');
        }
      }

      if (!completed) {
        throw new Error('Délai d\'attente dépassé lors de la génération.');
      }

    } catch (err) {
      Utils.toast('Erreur : ' + err.message, 'error');
      DOM.viewLoading.classList.add('hidden');
      DOM.viewUpload.classList.remove('hidden');
      DOM.btnResetTop.classList.add('hidden');
    }
  },

  bindEvents() {
    // CV File
    DOM.cvDropzone.addEventListener('click', (e) => {
      if (e.target.closest('#btn-remove-cv')) return;
      DOM.cvFileInput.click();
    });
    DOM.cvFileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) this.handleCvFile(e.target.files[0]);
    });
    DOM.cvDropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      DOM.cvDropzone.classList.add('border-burgeap-blue', 'bg-blue-50/50');
    });
    DOM.cvDropzone.addEventListener('dragleave', () => {
      DOM.cvDropzone.classList.remove('border-burgeap-blue', 'bg-blue-50/50');
    });
    DOM.cvDropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      DOM.cvDropzone.classList.remove('border-burgeap-blue', 'bg-blue-50/50');
      if (e.dataTransfer.files.length > 0) this.handleCvFile(e.dataTransfer.files[0]);
    });
    DOM.btnRemoveCv.addEventListener('click', (e) => {
      e.stopPropagation();
      State.selectedCvFile = null;
      DOM.cvFileInput.value = '';
      DOM.cvDropzoneEmpty.classList.remove('hidden');
      DOM.cvDropzoneFilled.classList.add('hidden');
      this.updateStartButton();
    });

    // Photo File
    DOM.photoDropzone.addEventListener('click', (e) => {
      if (e.target.closest('#btn-remove-photo')) return;
      DOM.photoFileInput.click();
    });
    DOM.photoFileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) this.handlePhotoFile(e.target.files[0]);
    });
    DOM.btnRemovePhoto.addEventListener('click', (e) => {
      e.stopPropagation();
      State.selectedPhotoFile = null;
      DOM.photoFileInput.value = '';
      DOM.photoPreviewImg.src = SVG_AVATAR_PLACEHOLDER;
      DOM.photoDropzoneEmpty.classList.remove('hidden');
      DOM.photoDropzoneFilled.classList.add('hidden');
    });
    DOM.cbInitialsOnly.addEventListener('change', () => {
      if (DOM.cbInitialsOnly.checked) {
        State.selectedPhotoFile = null;
        DOM.photoFileInput.value = '';
        DOM.photoPreviewImg.src = SVG_AVATAR_PLACEHOLDER;
        DOM.photoDropzoneEmpty.classList.remove('hidden');
        DOM.photoDropzoneFilled.classList.add('hidden');
      }
    });
    if (DOM.btnCropPhotoV1) {
      DOM.btnCropPhotoV1.addEventListener('click', (e) => {
        e.stopPropagation();
        if (State.rawPhotoDataUrl && this._onOpenCropper) {
          this._onOpenCropper(State.rawPhotoDataUrl, (newB64, newDataUrl) => {
            State.croppedPhotoB64 = newB64;
            DOM.photoPreviewImg.src = newDataUrl;
          });
        }
      });
    }

    // Start Button
    DOM.btnStartProcess.addEventListener('click', () => this.startJob());
  }
};
