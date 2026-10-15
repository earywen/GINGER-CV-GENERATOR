// Ginger Burgeap CV Generator 2026 - Frontend Controller

let cvData = null;
let currentLang = 'fr'; // 'fr' or 'en'
let previewLang = 'fr'; // 'fr' or 'en'
let selectedCvFile = null;
let selectedPhotoFile = null;
let zoomLevel = 0.65;

// DOM Elements
const viewUpload = document.getElementById('view-upload');
const viewLoading = document.getElementById('view-loading');
const viewEditor = document.getElementById('view-editor');
const btnResetTop = document.getElementById('btn-reset-top');

const cvDropzone = document.getElementById('cv-dropzone');
const cvFileInput = document.getElementById('cv-file-input');
const cvDropzoneEmpty = document.getElementById('cv-dropzone-empty');
const cvDropzoneFilled = document.getElementById('cv-dropzone-filled');
const cvFilename = document.getElementById('cv-filename');
const cvFilesize = document.getElementById('cv-filesize');
const btnRemoveCv = document.getElementById('btn-remove-cv');

const photoDropzone = document.getElementById('photo-dropzone');
const photoFileInput = document.getElementById('photo-file-input');
const photoDropzoneEmpty = document.getElementById('photo-dropzone-empty');
const photoDropzoneFilled = document.getElementById('photo-dropzone-filled');
const photoPreviewImg = document.getElementById('photo-preview-img');
const photoFilename = document.getElementById('photo-filename');
const btnRemovePhoto = document.getElementById('btn-remove-photo');
const cbInitialsOnly = document.getElementById('cb-initials-only');
const selectAgency = document.getElementById('select-agency');
const btnStartProcess = document.getElementById('btn-start-process');

const tabFr = document.getElementById('tab-fr');
const tabEn = document.getElementById('tab-en');
const btnRefreshPreview = document.getElementById('btn-refresh-preview');
const btnPreviewFr = document.getElementById('btn-preview-fr');
const btnPreviewEn = document.getElementById('btn-preview-en');
const btnDownloadActive = document.getElementById('btn-download-active');
const btnDownloadZip = document.getElementById('btn-download-zip');
const lblDownloadLang = document.getElementById('lbl-download-lang');
const pdfViewerFrame = document.getElementById('pdf-viewer-frame');
const pdfLoadingSpinner = document.getElementById('pdf-loading-spinner');

// Zoom Elements
const btnZoomIn = document.getElementById('btn-zoom-in');
const btnZoomOut = document.getElementById('btn-zoom-out');
const btnZoomFit = document.getElementById('btn-zoom-fit');
const btnOpenTab = document.getElementById('btn-open-tab');
const lblZoomVal = document.getElementById('lbl-zoom-val');

// Pitch Toolbar Buttons
const inpPitch = document.getElementById('inp-pitch');
const btnPitchBold = document.getElementById('btn-pitch-bold');
const btnPitchItalic = document.getElementById('btn-pitch-italic');
const btnPitchClear = document.getElementById('btn-pitch-clear');

if (btnPitchBold) {
  btnPitchBold.addEventListener('click', (e) => {
    e.preventDefault();
    inpPitch.focus();
    document.execCommand('bold', false, null);
  });
}
if (btnPitchItalic) {
  btnPitchItalic.addEventListener('click', (e) => {
    e.preventDefault();
    inpPitch.focus();
    document.execCommand('italic', false, null);
  });
}
if (btnPitchClear) {
  btnPitchClear.addEventListener('click', (e) => {
    e.preventDefault();
    inpPitch.focus();
    document.execCommand('removeFormat', false, null);
  });
}

// Zoom Functions
function applyZoomToIframe() {
  try {
    const doc = pdfViewerFrame.contentDocument || pdfViewerFrame.contentWindow.document;
    if (doc) {
      const pages = doc.querySelectorAll('.cv-page');
      pages.forEach(page => {
        page.style.transform = `scale(${zoomLevel.toFixed(2)})`;
        page.style.transformOrigin = 'top center';
        
        const scaledHeight = 1122 * zoomLevel;
        page.style.marginBottom = `${Math.max(20, scaledHeight - 1122 + 40)}px`;
      });
    }
  } catch (e) {
    console.error('Zoom error:', e);
  }
}

function setZoom(val) {
  zoomLevel = Math.max(0.35, Math.min(1.80, val));
  if (lblZoomVal) lblZoomVal.textContent = `${Math.round(zoomLevel * 100)}%`;
  applyZoomToIframe();
}

function autoFitZoom() {
  if (!pdfViewerFrame) return;
  const vh = pdfViewerFrame.clientHeight - 40;
  const vw = pdfViewerFrame.clientWidth - 40;
  if (vh > 100 && vw > 100) {
    const fitH = vh / 1122;
    const fitW = vw / 794;
    setZoom(Math.min(fitH, fitW, 0.90));
  } else {
    setZoom(0.65);
  }
}

if (btnZoomIn) {
  btnZoomIn.addEventListener('click', () => setZoom(zoomLevel + 0.15));
}
if (btnZoomOut) {
  btnZoomOut.addEventListener('click', () => setZoom(zoomLevel - 0.15));
}
if (btnZoomFit) {
  btnZoomFit.addEventListener('click', () => autoFitZoom());
}
if (btnOpenTab) {
  btnOpenTab.addEventListener('click', async () => {
    saveCurrentFormToData();
    const res = await fetch('/api/render-preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: cvData, lang: previewLang })
    });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank');
  });
}

// Setup Dropzones & File Selectors
cvDropzone.addEventListener('click', (e) => {
  if (e.target.closest('#btn-remove-cv')) return;
  cvFileInput.click();
});

cvFileInput.addEventListener('change', (e) => {
  if (e.target.files.length > 0) {
    handleCvFile(e.target.files[0]);
  }
});

cvDropzone.addEventListener('dragover', (e) => {
  e.preventDefault();
  cvDropzone.classList.add('border-burgeap-blue', 'bg-blue-50/50');
});

cvDropzone.addEventListener('dragleave', () => {
  cvDropzone.classList.remove('border-burgeap-blue', 'bg-blue-50/50');
});

cvDropzone.addEventListener('drop', (e) => {
  e.preventDefault();
  cvDropzone.classList.remove('border-burgeap-blue', 'bg-blue-50/50');
  if (e.dataTransfer.files.length > 0) {
    handleCvFile(e.dataTransfer.files[0]);
  }
});

btnRemoveCv.addEventListener('click', (e) => {
  e.stopPropagation();
  selectedCvFile = null;
  cvFileInput.value = '';
  cvDropzoneEmpty.classList.remove('hidden');
  cvDropzoneFilled.classList.add('hidden');
  updateStartButton();
});

function handleCvFile(file) {
  selectedCvFile = file;
  cvFilename.textContent = file.name;
  cvFilesize.textContent = (file.size / (1024 * 1024)).toFixed(2) + ' MB';
  cvDropzoneEmpty.classList.add('hidden');
  cvDropzoneFilled.classList.remove('hidden');
  updateStartButton();
}

// Photo Handlers
photoDropzone.addEventListener('click', (e) => {
  if (e.target.closest('#btn-remove-photo')) return;
  photoFileInput.click();
});

photoFileInput.addEventListener('change', (e) => {
  if (e.target.files.length > 0) {
    handlePhotoFile(e.target.files[0]);
  }
});

btnRemovePhoto.addEventListener('click', (e) => {
  e.stopPropagation();
  selectedPhotoFile = null;
  photoFileInput.value = '';
  photoDropzoneEmpty.classList.remove('hidden');
  photoDropzoneFilled.classList.add('hidden');
});

cbInitialsOnly.addEventListener('change', () => {
  if (cbInitialsOnly.checked) {
    selectedPhotoFile = null;
    photoFileInput.value = '';
    photoDropzoneEmpty.classList.remove('hidden');
    photoDropzoneFilled.classList.add('hidden');
  }
});

// ==================== CROPPER MODAL CONTROLLER ====================
let currentCropper = null;
let cropperApplyCallback = null;
let croppedPhotoB64 = null;
let rawPhotoDataUrl = null;

const modalCropper = document.getElementById('modal-cropper');
const cropperImage = document.getElementById('cropper-image');
const btnCropperClose = document.getElementById('btn-cropper-close');
const btnCropCancel = document.getElementById('btn-crop-cancel');
const btnCropReset = document.getElementById('btn-crop-reset');
const btnCropApply = document.getElementById('btn-crop-apply');
const btnCropZoomIn = document.getElementById('btn-crop-zoom-in');
const btnCropZoomOut = document.getElementById('btn-crop-zoom-out');
const cropZoomSlider = document.getElementById('crop-zoom-slider');
const btnCropRotateLeft = document.getElementById('btn-crop-rotate-left');
const btnCropRotateRight = document.getElementById('btn-crop-rotate-right');
const btnCropPhotoV1 = document.getElementById('btn-crop-photo-v1');

const btnEditorCrop = document.getElementById('btn-editor-crop');
const btnEditorChangePhoto = document.getElementById('btn-editor-change-photo');
const editorPhotoInput = document.getElementById('editor-photo-input');

function openCropperModal(imageSrc, onApply) {
  if (!imageSrc) return;
  cropperApplyCallback = onApply;
  modalCropper.classList.remove('hidden');

  if (currentCropper) {
    currentCropper.destroy();
    currentCropper = null;
  }

  cropperImage.src = imageSrc;

  const initCropper = () => {
    currentCropper = new Cropper(cropperImage, {
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
        if (cropZoomSlider) cropZoomSlider.value = 1;
      },
      zoom(e) {
        if (cropZoomSlider && e.detail && e.detail.ratio) {
          cropZoomSlider.value = Math.min(3, Math.max(0.1, e.detail.ratio));
        }
      }
    });
  };

  if (cropperImage.complete && cropperImage.naturalWidth > 0) {
    initCropper();
  } else {
    cropperImage.onload = initCropper;
  }
}

function closeCropperModal() {
  modalCropper.classList.add('hidden');
  if (currentCropper) {
    currentCropper.destroy();
    currentCropper = null;
  }
  cropperApplyCallback = null;
}

if (btnCropperClose) btnCropperClose.addEventListener('click', closeCropperModal);
if (btnCropCancel) btnCropCancel.addEventListener('click', closeCropperModal);

if (btnCropReset) {
  btnCropReset.addEventListener('click', () => {
    if (currentCropper) {
      currentCropper.reset();
      if (cropZoomSlider) cropZoomSlider.value = 1;
    }
  });
}

if (btnCropZoomIn) {
  btnCropZoomIn.addEventListener('click', () => {
    if (currentCropper) currentCropper.zoom(0.1);
  });
}

if (btnCropZoomOut) {
  btnCropZoomOut.addEventListener('click', () => {
    if (currentCropper) currentCropper.zoom(-0.1);
  });
}

if (cropZoomSlider) {
  cropZoomSlider.addEventListener('input', (e) => {
    if (currentCropper) {
      currentCropper.zoomTo(parseFloat(e.target.value));
    }
  });
}

if (btnCropRotateLeft) {
  btnCropRotateLeft.addEventListener('click', () => {
    if (currentCropper) currentCropper.rotate(-90);
  });
}

if (btnCropRotateRight) {
  btnCropRotateRight.addEventListener('click', () => {
    if (currentCropper) currentCropper.rotate(90);
  });
}

if (btnCropApply) {
  btnCropApply.addEventListener('click', () => {
    if (!currentCropper) return;
    const canvas = currentCropper.getCroppedCanvas({
      width: 800,
      height: 800,
      imageSmoothingEnabled: true,
      imageSmoothingQuality: 'high'
    });

    const dataUrl = canvas.toDataURL('image/jpeg', 0.95);
    const b64 = dataUrl.split(',')[1];

    if (cropperApplyCallback) {
      cropperApplyCallback(b64, dataUrl);
    }
    closeCropperModal();
  });
}

if (btnCropPhotoV1) {
  btnCropPhotoV1.addEventListener('click', (e) => {
    e.stopPropagation();
    if (rawPhotoDataUrl) {
      openCropperModal(rawPhotoDataUrl, (newB64, newDataUrl) => {
        croppedPhotoB64 = newB64;
        photoPreviewImg.src = newDataUrl;
      });
    }
  });
}

if (btnEditorCrop) {
  btnEditorCrop.addEventListener('click', () => {
    if (cvData && cvData.photo_b64) {
      openCropperModal(`data:image/jpeg;base64,${cvData.photo_b64}`, (newB64) => {
        cvData.photo_b64 = newB64;
        updateEditorAvatarDisplay();
        refreshPdfPreview();
      });
    } else {
      editorPhotoInput.click();
    }
  });
}

if (btnEditorChangePhoto) {
  btnEditorChangePhoto.addEventListener('click', () => {
    editorPhotoInput.click();
  });
}

if (editorPhotoInput) {
  editorPhotoInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      const file = e.target.files[0];
      optimizeImage(file).then(({ dataUrl }) => {
        openCropperModal(dataUrl, (newB64) => {
          if (!cvData) cvData = {};
          cvData.photo_b64 = newB64;
          updateEditorAvatarDisplay();
          refreshPdfPreview();
        });
      }).catch((err) => {
        alert('Erreur lors du traitement de l\'image : ' + err.message);
      });
    }
  });
}

function updateEditorAvatarDisplay() {
  const avatarImg = document.getElementById('editor-avatar-img');
  const avatarInitials = document.getElementById('editor-avatar-initials');
  const photoStatus = document.getElementById('editor-photo-status');

  if (!avatarImg) return;

  if (cvData && cvData.photo_b64) {
    avatarImg.src = `data:image/jpeg;base64,${cvData.photo_b64}`;
    avatarImg.classList.remove('hidden');
    avatarInitials.classList.add('hidden');
    if (photoStatus) photoStatus.textContent = 'Photo studio chargée (cliquer sur Ajuster)';
  } else {
    avatarImg.src = '';
    avatarImg.classList.add('hidden');
    avatarInitials.classList.remove('hidden');
    avatarInitials.textContent = (cvData && cvData.initials) ? cvData.initials : 'GB';
    if (photoStatus) photoStatus.textContent = 'Médaillon initiales (aucune photo)';
  }
}

function optimizeImage(file, maxDimension = 1200) {
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

function handlePhotoFile(file) {
  selectedPhotoFile = file;
  cbInitialsOnly.checked = false;
  photoFilename.textContent = file.name;

  optimizeImage(file).then(({ dataUrl, b64 }) => {
    rawPhotoDataUrl = dataUrl;
    croppedPhotoB64 = b64;
    photoPreviewImg.src = dataUrl;
    photoDropzoneEmpty.classList.add('hidden');
    photoDropzoneFilled.classList.remove('hidden');

    // Automatically open cropper so user can visually verify and adjust
    openCropperModal(dataUrl, (newB64, newDataUrl) => {
      croppedPhotoB64 = newB64;
      photoPreviewImg.src = newDataUrl;
    });
  }).catch((err) => {
    alert('Erreur lors du traitement de l\'image : ' + err.message);
  });
}

function updateStartButton() {
  btnStartProcess.disabled = !selectedCvFile;
}

// Start Processing via Async Job Polling
btnStartProcess.addEventListener('click', async () => {
  if (!selectedCvFile) return;

  viewUpload.classList.add('hidden');
  viewLoading.classList.remove('hidden');
  btnResetTop.classList.remove('hidden');

  const formData = new FormData();
  formData.append('cv_file', selectedCvFile);
  if (croppedPhotoB64 && !cbInitialsOnly.checked) {
    formData.append('photo_b64', croppedPhotoB64);
  } else if (selectedPhotoFile && !cbInitialsOnly.checked) {
    formData.append('photo_file', selectedPhotoFile);
  }
  formData.append('agency', selectAgency.value);

  const stepTitle = document.getElementById('loading-step-title');
  const stepDesc = document.getElementById('loading-step-desc');
  const progressBar = document.getElementById('loading-progress-bar');

  progressBar.style.width = '15%';
  stepTitle.textContent = 'Envoi du document...';
  stepDesc.textContent = 'Initialisation du traitement IA sécurisé.';

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
      } catch (_) {
        if (text.includes('<title>')) {
          const m = text.match(/<title>(.*?)<\/title>/i);
          if (m && m[1]) msg = `${queueRes.status} : ${m[1]}`;
        }
      }
      throw new Error(msg);
    }

    const { job_id } = await queueRes.json();

    let pollAttempts = 0;
    const maxAttempts = 150; // up to ~3.5 minutes
    let completed = false;

    while (pollAttempts < maxAttempts && !completed) {
      await new Promise(r => setTimeout(r, 1500));
      pollAttempts++;

      try {
        const statusRes = await fetch(`/api/parse-cv-status/${job_id}`);
        if (!statusRes.ok) continue;

        const job = await statusRes.json();
        if (job.status === 'processing') {
          if (job.progress) progressBar.style.width = `${job.progress}%`;
          if (job.step) stepTitle.textContent = job.step;
          if (job.desc) stepDesc.textContent = job.desc;
        } else if (job.status === 'completed') {
          completed = true;
          cvData = job.data;
          progressBar.style.width = '100%';
          stepTitle.textContent = 'Finalisation de la mise en page...';
          stepDesc.textContent = 'CV prêt ! Ouverture de l\'éditeur.';
          setTimeout(() => {
            viewLoading.classList.add('hidden');
            viewEditor.classList.remove('hidden');
            populateEditor();
            refreshPdfPreview();
          }, 500);
          return;
        } else if (job.status === 'failed') {
          throw new Error(job.error || 'Erreur lors du traitement du CV.');
        }
      } catch (pollErr) {
        if (pollErr.message && !pollErr.message.includes('fetch')) {
          throw pollErr;
        }
      }
    }

    if (!completed) {
      throw new Error('Délai d\'attente dépassé lors de la génération. Veuillez réessayer.');
    }

  } catch (error) {
    alert('Erreur : ' + error.message);
    viewLoading.classList.add('hidden');
    viewUpload.classList.remove('hidden');
    btnResetTop.classList.add('hidden');
  }
});

// Editor Tabs (FR / EN)
tabFr.addEventListener('click', () => switchEditorLang('fr'));
tabEn.addEventListener('click', () => switchEditorLang('en'));

function switchEditorLang(lang) {
  saveCurrentFormToData();
  currentLang = lang;
  
  if (lang === 'fr') {
    tabFr.className = 'px-3.5 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-2 bg-burgeap-blue text-white shadow-sm';
    tabEn.className = 'px-3.5 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-2 bg-transparent text-slate-600 hover:bg-slate-200';
    document.querySelectorAll('.lang-label').forEach(el => el.textContent = 'FR');
  } else {
    tabEn.className = 'px-3.5 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-2 bg-burgeap-blue text-white shadow-sm';
    tabFr.className = 'px-3.5 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-2 bg-transparent text-slate-600 hover:bg-slate-200';
    document.querySelectorAll('.lang-label').forEach(el => el.textContent = 'EN');
  }
  
  populateEditor();
}

function cleanHtmlFormatting(html) {
  if (!html) return '';
  return html
    .replace(/<b>/gi, '<strong>')
    .replace(/<\/b>/gi, '</strong>')
    .replace(/<i>/gi, '<em>')
    .replace(/<\/i>/gi, '</em>')
    .replace(/<div><br><\/div>/gi, ' ')
    .replace(/<div>/gi, ' ')
    .replace(/<\/div>/gi, '')
    .trim();
}

function populateEditor() {
  if (!cvData) return;

  document.getElementById('inp-name').value = cvData.name || '';
  document.getElementById('inp-trigram').value = cvData.trigram || '';

  const isFr = (currentLang === 'fr');
  document.getElementById('inp-role').value = isFr ? (cvData.role_fr || '') : (cvData.role_en || '');
  document.getElementById('inp-exp').value = isFr ? (cvData.exp_fr || '') : (cvData.exp_en || '');
  
  const pitchContent = isFr ? (cvData.pitch_fr || '') : (cvData.pitch_en || '');
  inpPitch.innerHTML = pitchContent;

  renderDynamicList('list-formations', isFr ? cvData.formations_fr : cvData.formations_en);
  renderDynamicList('list-competences', isFr ? cvData.competences_fr : cvData.competences_en);
  renderDynamicList('list-exp-pros', isFr ? cvData.exp_pros_fr : cvData.exp_pros_en);
  renderDynamicList('list-langs', isFr ? cvData.langs_fr : cvData.langs_en);
  renderQualifsList(isFr ? cvData.qualifs_fr : cvData.qualifs_en);
  renderRefsList(isFr ? cvData.refs_fr : cvData.refs_en);
  updateEditorAvatarDisplay();
}

function renderDynamicList(containerId, items) {
  const container = document.getElementById(containerId);
  container.innerHTML = '';
  if (!items) return;

  items.forEach((item, idx) => {
    const row = document.createElement('div');
    row.className = 'flex items-center space-x-2';
    
    row.innerHTML = `
      <div contenteditable="true" class="flex-1 border border-slate-300 rounded px-2.5 py-1 text-xs focus:ring-1 focus:ring-burgeap-blue focus:outline-none bg-white">${item}</div>
      <button type="button" class="text-slate-400 hover:text-red-500 px-1.5 py-1 text-xs"><i class="fa-solid fa-xmark"></i></button>
    `;
    
    const editableDiv = row.querySelector('div[contenteditable]');
    row.querySelector('button').addEventListener('click', () => {
      items.splice(idx, 1);
      renderDynamicList(containerId, items);
    });
    editableDiv.addEventListener('input', () => {
      items[idx] = cleanHtmlFormatting(editableDiv.innerHTML);
    });
    container.appendChild(row);
  });

  const btnAdd = document.createElement('button');
  btnAdd.type = 'button';
  btnAdd.className = 'text-[11px] font-bold text-burgeap-blue hover:underline mt-1 flex items-center gap-1';
  btnAdd.innerHTML = '<i class="fa-solid fa-plus"></i> Ajouter une ligne';
  btnAdd.addEventListener('click', () => {
    items.push('Nouvel élément');
    renderDynamicList(containerId, items);
  });
  container.appendChild(btnAdd);
}

function renderQualifsList(qualifs) {
  const container = document.getElementById('list-qualifs');
  container.innerHTML = '';
  if (!qualifs) return;

  qualifs.forEach((q, idx) => {
    const card = document.createElement('div');
    card.className = 'bg-slate-50 border border-slate-200 rounded-lg p-2.5 space-y-1.5';
    
    card.innerHTML = `
      <div class="flex justify-between items-center text-[11px] font-bold text-slate-600">
        <span>Point ${idx + 1}</span>
        <div class="flex items-center space-x-1 bg-white border border-slate-200 rounded px-1.5 py-0.5">
          <button type="button" class="btn-q-bold px-1.5 py-0.2 text-[11px] font-bold hover:bg-slate-100 rounded text-slate-700" title="Mettre en gras"><i class="fa-solid fa-bold"></i></button>
          <button type="button" class="btn-q-italic px-1.5 py-0.2 text-[11px] italic hover:bg-slate-100 rounded text-slate-700" title="Mettre en italique"><i class="fa-solid fa-italic"></i></button>
        </div>
      </div>
      <div contenteditable="true" class="q-content w-full min-h-[42px] border border-slate-300 rounded p-1.5 text-xs bg-white focus:ring-1 focus:ring-burgeap-blue focus:outline-none leading-relaxed">${q}</div>
    `;

    const editableQ = card.querySelector('.q-content');
    card.querySelector('.btn-q-bold').addEventListener('click', (e) => {
      e.preventDefault();
      editableQ.focus();
      document.execCommand('bold', false, null);
    });
    card.querySelector('.btn-q-italic').addEventListener('click', (e) => {
      e.preventDefault();
      editableQ.focus();
      document.execCommand('italic', false, null);
    });
    editableQ.addEventListener('input', () => {
      qualifs[idx] = cleanHtmlFormatting(editableQ.innerHTML);
    });

    container.appendChild(card);
  });
}

function renderRefsList(refs) {
  const container = document.getElementById('list-refs');
  container.innerHTML = '';
  if (!refs) return;

  refs.forEach((r, idx) => {
    const card = document.createElement('div');
    card.className = 'ref-card bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-2';
    card.innerHTML = `
      <div class="flex justify-between items-center text-xs font-bold text-burgeap-blue">
        <span>Mission ${idx + 1}</span>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
        <div>
          <label class="block text-[10px] font-bold text-slate-500 uppercase">Titre Projet (MAJUSCULE)</label>
          <input type="text" value="${(r.title || '').replace(/"/g, '&quot;')}" class="inp-ref-title w-full border border-slate-300 rounded px-2 py-1 text-xs font-bold bg-white">
        </div>
        <div>
          <label class="block text-[10px] font-bold text-slate-500 uppercase">Badge Thématique</label>
          <input type="text" value="${(r.tag || '').replace(/"/g, '&quot;')}" class="inp-ref-tag w-full border border-slate-300 rounded px-2 py-1 text-xs font-semibold bg-white">
        </div>
      </div>
      <div>
        <label class="block text-[10px] font-bold text-slate-500 uppercase">Description Synthétique</label>
        <textarea rows="2" class="inp-ref-desc w-full border border-slate-300 rounded p-1.5 text-xs bg-white">${r.desc || ''}</textarea>
      </div>
    `;

    card.querySelector('.inp-ref-title').addEventListener('input', (e) => r.title = e.target.value);
    card.querySelector('.inp-ref-tag').addEventListener('input', (e) => r.tag = e.target.value);
    card.querySelector('.inp-ref-desc').addEventListener('input', (e) => r.desc = e.target.value);

    container.appendChild(card);
  });
}

function saveCurrentFormToData() {
  if (!cvData) return;
  cvData.name = document.getElementById('inp-name').value;
  cvData.trigram = document.getElementById('inp-trigram').value;

  const isFr = (currentLang === 'fr');
  if (isFr) {
    cvData.role_fr = document.getElementById('inp-role').value;
    cvData.exp_fr = document.getElementById('inp-exp').value;
    cvData.pitch_fr = cleanHtmlFormatting(inpPitch.innerHTML);
  } else {
    cvData.role_en = document.getElementById('inp-role').value;
    cvData.exp_en = document.getElementById('inp-exp').value;
    cvData.pitch_en = cleanHtmlFormatting(inpPitch.innerHTML);
  }
}

// Live Preview Buttons
btnRefreshPreview.addEventListener('click', () => {
  saveCurrentFormToData();
  refreshPdfPreview();
});

btnPreviewFr.addEventListener('click', () => {
  previewLang = 'fr';
  btnPreviewFr.className = 'px-2.5 py-1 rounded bg-white text-burgeap-blue shadow-sm flex items-center gap-1.5 font-bold';
  btnPreviewEn.className = 'px-2.5 py-1 rounded text-slate-600 hover:text-slate-900 flex items-center gap-1.5 font-bold';
  lblDownloadLang.textContent = 'FR';
  saveCurrentFormToData();
  refreshPdfPreview();
});

btnPreviewEn.addEventListener('click', () => {
  previewLang = 'en';
  btnPreviewEn.className = 'px-2.5 py-1 rounded bg-white text-burgeap-blue shadow-sm flex items-center gap-1.5 font-bold';
  btnPreviewFr.className = 'px-2.5 py-1 rounded text-slate-600 hover:text-slate-900 flex items-center gap-1.5 font-bold';
  lblDownloadLang.textContent = 'EN';
  saveCurrentFormToData();
  refreshPdfPreview();
});

async function refreshPdfPreview() {
  if (!cvData) return;
  pdfLoadingSpinner.classList.remove('hidden');

  try {
    const response = await fetch('/api/render-html', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: cvData, lang: previewLang })
    });

    if (!response.ok) throw new Error('Erreur lors du rendu de la prévisualisation.');

    const htmlContent = await response.text();
    pdfViewerFrame.srcdoc = htmlContent;

    pdfViewerFrame.onload = () => {
      pdfLoadingSpinner.classList.add('hidden');
      applyZoomToIframe();
    };

  } catch (err) {
    console.error(err);
    pdfLoadingSpinner.classList.add('hidden');
  }
}

// Export Downloads
btnDownloadActive.addEventListener('click', async () => {
  saveCurrentFormToData();
  const response = await fetch('/api/export-pdf', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: cvData, lang: previewLang })
  });
  const blob = await response.blob();
  const filename = `CV_${(cvData.name || 'Collaborateur').replace(/\\s+/g, '_')}_${previewLang.toUpperCase()}.pdf`;
  downloadBlob(blob, filename);
});

btnDownloadZip.addEventListener('click', async () => {
  saveCurrentFormToData();
  const response = await fetch('/api/export-zip', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: cvData })
  });
  const blob = await response.blob();
  const filename = `CV_${(cvData.name || 'Collaborateur').replace(/\\s+/g, '_')}_BURGEAP_2026.zip`;
  downloadBlob(blob, filename);
});

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// Reset Top Button
btnResetTop.addEventListener('click', () => {
  if (confirm('Voulez-vous recommencer pour un nouveau collaborateur ?')) {
    cvData = null;
    selectedCvFile = null;
    selectedPhotoFile = null;
    croppedPhotoB64 = null;
    rawPhotoDataUrl = null;
    cvFileInput.value = '';
    photoFileInput.value = '';
    cvDropzoneEmpty.classList.remove('hidden');
    cvDropzoneFilled.classList.add('hidden');
    photoDropzoneEmpty.classList.remove('hidden');
    photoDropzoneFilled.classList.add('hidden');
    cbInitialsOnly.checked = false;
    updateStartButton();

    viewEditor.classList.add('hidden');
    viewLoading.classList.add('hidden');
    viewUpload.classList.remove('hidden');
    btnResetTop.classList.add('hidden');
  }
});
