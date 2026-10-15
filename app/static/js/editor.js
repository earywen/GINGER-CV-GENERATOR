/**
 * Editor Controller
 * Handles dynamic form binding, list management (degrees, training, skills, refs),
 * language switching, and live preview scheduling.
 */
import { State } from './state.js';
import { DOM } from './dom.js';
import { Utils, SVG_AVATAR_PLACEHOLDER } from './utils.js';

export const EditorController = {
  _livePreviewTimer: null,
  _onPreviewRefresh: null,
  _onScheduleAutoSave: null,
  _onOpenCropper: null,

  setHandlers({ onPreviewRefresh, onScheduleAutoSave, onOpenCropper }) {
    this._onPreviewRefresh = onPreviewRefresh;
    this._onScheduleAutoSave = onScheduleAutoSave;
    this._onOpenCropper = onOpenCropper;
  },

  scheduleLivePreview(immediate = false) {
    clearTimeout(this._livePreviewTimer);
    const delay = immediate ? 0 : 300;
    this._livePreviewTimer = setTimeout(() => {
      this.saveCurrentForm();
      if (this._onPreviewRefresh) this._onPreviewRefresh(true);
      if (this._onScheduleAutoSave) this._onScheduleAutoSave();
    }, delay);
  },

  switchLang(lang, shouldSave = true) {
    if (shouldSave) this.saveCurrentForm();
    State.currentLang = lang;
    State.previewLang = lang;

    if (lang === 'fr') {
      DOM.tabFr.className = 'px-2.5 sm:px-3 py-1 rounded-md text-xs font-bold transition flex items-center gap-1.5 bg-burgeap-blue text-white shadow-xs';
      DOM.tabEn.className = 'px-2.5 sm:px-3 py-1 rounded-md text-xs font-bold transition flex items-center gap-1.5 bg-transparent text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white';
      document.querySelectorAll('.lang-label').forEach(el => el.textContent = 'FR');
    } else {
      DOM.tabEn.className = 'px-2.5 sm:px-3 py-1 rounded-md text-xs font-bold transition flex items-center gap-1.5 bg-burgeap-blue text-white shadow-xs';
      DOM.tabFr.className = 'px-2.5 sm:px-3 py-1 rounded-md text-xs font-bold transition flex items-center gap-1.5 bg-transparent text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white';
      document.querySelectorAll('.lang-label').forEach(el => el.textContent = 'EN');
    }

    if (DOM.lblDownloadLang) {
      DOM.lblDownloadLang.textContent = lang.toUpperCase();
    }

    this.populate();
    if (this._onPreviewRefresh) this._onPreviewRefresh(false);
    if (this._onScheduleAutoSave) this._onScheduleAutoSave();
  },

  saveCurrentForm() {
    if (!State.cvData) return;
    const inpName = document.getElementById('inp-name');
    const inpTrigram = document.getElementById('inp-trigram');
    const inpRole = document.getElementById('inp-role');
    const inpExp = document.getElementById('inp-exp');

    if (inpName) State.cvData.name = inpName.value;
    if (inpTrigram) State.cvData.trigram = inpTrigram.value;

    const isFr = (State.currentLang === 'fr');
    if (isFr) {
      if (inpRole) State.cvData.role_fr = inpRole.value;
      if (inpExp) State.cvData.exp_fr = inpExp.value;
      if (DOM.inpPitch) State.cvData.pitch_fr = Utils.cleanHtml(DOM.inpPitch.innerHTML);
    } else {
      if (inpRole) State.cvData.role_en = inpRole.value;
      if (inpExp) State.cvData.exp_en = inpExp.value;
      if (DOM.inpPitch) State.cvData.pitch_en = Utils.cleanHtml(DOM.inpPitch.innerHTML);
    }

    if (DOM.chkShowBadges) {
      State.cvData.show_badges = DOM.chkShowBadges.checked;
    }
  },

  populate() {
    if (!State.cvData) return;
    const isFr = (State.currentLang === 'fr');

    if (DOM.chkShowBadges) {
      DOM.chkShowBadges.checked = (State.cvData.show_badges !== false);
    }

    const inpName = document.getElementById('inp-name');
    const inpTrigram = document.getElementById('inp-trigram');
    const inpRole = document.getElementById('inp-role');
    const inpExp = document.getElementById('inp-exp');

    if (inpName) inpName.value = State.cvData.name || '';
    if (inpTrigram) inpTrigram.value = State.cvData.trigram || '';
    if (inpRole) inpRole.value = isFr ? (State.cvData.role_fr || '') : (State.cvData.role_en || '');
    if (inpExp) {
      inpExp.value = isFr ? (State.cvData.exp_fr || '') : (State.cvData.exp_en || '');
      inpExp.placeholder = isFr ? "Ex: 6 ans d'expérience, dont 3 ans chez GINGER BURGEAP" : "Ex: 6 years of experience, including 3 years at GINGER BURGEAP";
    }

    if (DOM.inpPitch) {
      DOM.inpPitch.innerHTML = isFr ? (State.cvData.pitch_fr || '') : (State.cvData.pitch_en || '');
    }

    if (!State.cvData.diplomes_fr) State.cvData.diplomes_fr = [];
    if (!State.cvData.diplomes_en) State.cvData.diplomes_en = [];
    if (!State.cvData.formations_fr) State.cvData.formations_fr = [];
    if (!State.cvData.formations_en) State.cvData.formations_en = [];

    // Backward compatibility: if cvData has old formations array containing academic degrees
    if (State.cvData.diplomes_fr.length === 0 && State.cvData.formations_fr.length > 0) {
      State.cvData.diplomes_fr = [...State.cvData.formations_fr];
      State.cvData.diplomes_en = [...(State.cvData.formations_en || [])];
      State.cvData.formations_fr = [];
      State.cvData.formations_en = [];
    }

    this.renderDynamicList('list-diplomes', isFr ? State.cvData.diplomes_fr : State.cvData.diplomes_en);
    this.renderDynamicList('list-formations', isFr ? State.cvData.formations_fr : State.cvData.formations_en);
    this.renderDynamicList('list-competences', isFr ? State.cvData.competences_fr : State.cvData.competences_en);
    this.renderDynamicList('list-exp-pros', isFr ? State.cvData.exp_pros_fr : State.cvData.exp_pros_en);
    this.renderDynamicList('list-langs', isFr ? State.cvData.langs_fr : State.cvData.langs_en);

    this.renderQualifsList(isFr ? State.cvData.qualifs_fr : State.cvData.qualifs_en);
    this.renderRefsList(isFr ? State.cvData.refs_fr : State.cvData.refs_en);

    this.updateAvatar();
  },

  updateAvatar() {
    if (!DOM.editorAvatarImg) return;
    if (State.cvData && State.cvData.photo_b64) {
      DOM.editorAvatarImg.src = `data:image/jpeg;base64,${State.cvData.photo_b64}`;
      DOM.editorAvatarImg.classList.remove('hidden');
      DOM.editorAvatarInitials.classList.add('hidden');
      if (DOM.editorPhotoStatus) DOM.editorPhotoStatus.textContent = 'Photo studio chargée (Ajuster possible)';
    } else {
      DOM.editorAvatarImg.src = SVG_AVATAR_PLACEHOLDER;
      DOM.editorAvatarImg.classList.add('hidden');
      DOM.editorAvatarInitials.classList.remove('hidden');
      DOM.editorAvatarInitials.textContent = (State.cvData && State.cvData.initials) ? State.cvData.initials : 'GB';
      if (DOM.editorPhotoStatus) DOM.editorPhotoStatus.textContent = 'Médaillon initiales officielles';
    }
  },

  renderDynamicList(containerId, items) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';
    if (!items) return;

    items.forEach((item, idx) => {
      const row = document.createElement('div');
      row.className = 'flex items-center space-x-2';
      row.innerHTML = `
        <div contenteditable="true" class="flex-1 border border-slate-300 dark:border-slate-700 rounded px-2.5 py-1 text-xs focus:ring-1 focus:ring-burgeap-blue dark:focus:ring-burgeap-green focus:outline-none bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100">${item}</div>
        <button type="button" class="text-slate-400 hover:text-red-500 px-1.5 py-1 text-xs"><i class="fa-solid fa-xmark"></i></button>
      `;

      const editableDiv = row.querySelector('div[contenteditable]');
      row.querySelector('button').addEventListener('click', () => {
        items.splice(idx, 1);
        this.renderDynamicList(containerId, items);
        this.scheduleLivePreview(true);
      });
      editableDiv.addEventListener('input', () => {
        items[idx] = Utils.cleanHtml(editableDiv.innerHTML);
        this.scheduleLivePreview(false);
      });
      container.appendChild(row);
    });

    const btnAdd = document.createElement('button');
    btnAdd.type = 'button';
    btnAdd.className = 'text-[11px] font-bold text-burgeap-blue dark:text-burgeap-green hover:underline mt-1 flex items-center gap-1';
    btnAdd.innerHTML = '<i class="fa-solid fa-plus"></i> Ajouter une ligne';
    btnAdd.addEventListener('click', () => {
      items.push('Nouvel élément');
      this.renderDynamicList(containerId, items);
      this.scheduleLivePreview(true);
    });
    container.appendChild(btnAdd);
  },

  renderQualifsList(qualifs) {
    const container = document.getElementById('list-qualifs');
    if (!container) return;
    container.innerHTML = '';
    if (!qualifs) return;

    qualifs.forEach((q, idx) => {
      const item = document.createElement('div');
      item.className = 'py-2 border-b border-slate-200 dark:border-slate-800 last:border-b-0 space-y-1.5';
      item.innerHTML = `
        <div class="flex justify-between items-center text-[11px] font-bold text-slate-600 dark:text-slate-300">
          <span>Point ${idx + 1}</span>
          <div class="flex items-center space-x-1 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded px-1.5 py-0.5">
            <button type="button" class="btn-q-bold px-1.5 py-0.2 text-[11px] font-bold hover:bg-slate-200 dark:hover:bg-slate-700 rounded text-slate-700 dark:text-slate-200" title="Mettre en gras"><i class="fa-solid fa-bold"></i></button>
            <button type="button" class="btn-q-italic px-1.5 py-0.2 text-[11px] italic hover:bg-slate-200 dark:hover:bg-slate-700 rounded text-slate-700 dark:text-slate-200" title="Mettre en italique"><i class="fa-solid fa-italic"></i></button>
          </div>
        </div>
        <div contenteditable="true" class="q-content w-full min-h-[42px] border border-slate-300 dark:border-slate-700 rounded-lg p-2 text-xs bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 focus:ring-1 focus:ring-burgeap-blue dark:focus:ring-burgeap-green focus:outline-none leading-relaxed">${q}</div>
      `;

      const editableQ = item.querySelector('.q-content');
      item.querySelector('.btn-q-bold').addEventListener('click', (e) => {
        e.preventDefault();
        editableQ.focus();
        Utils.formatText('bold');
        qualifs[idx] = Utils.cleanHtml(editableQ.innerHTML);
        this.scheduleLivePreview(true);
      });
      item.querySelector('.btn-q-italic').addEventListener('click', (e) => {
        e.preventDefault();
        editableQ.focus();
        Utils.formatText('italic');
        qualifs[idx] = Utils.cleanHtml(editableQ.innerHTML);
        this.scheduleLivePreview(true);
      });
      editableQ.addEventListener('input', () => {
        qualifs[idx] = Utils.cleanHtml(editableQ.innerHTML);
        this.scheduleLivePreview(false);
      });

      container.appendChild(item);
    });
  },

  renderRefsList(refs) {
    const container = document.getElementById('list-refs');
    if (!container) return;
    container.innerHTML = '';
    if (!refs) return;

    refs.forEach((r, idx) => {
      const item = document.createElement('div');
      item.className = 'py-3 border-b border-slate-200 dark:border-slate-800 last:border-b-0 space-y-2';
      item.innerHTML = `
        <div class="flex justify-between items-center text-xs font-bold text-burgeap-blue dark:text-burgeap-green">
          <span>Mission ${idx + 1}</span>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <div>
            <label class="block text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Titre Projet (MAJUSCULE)</label>
            <input type="text" value="${(r.title || '').replace(/"/g, '&quot;')}" class="inp-ref-title w-full border border-slate-300 dark:border-slate-700 rounded-lg px-2.5 py-1 text-xs font-bold bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 focus:ring-1 focus:ring-burgeap-blue dark:focus:ring-burgeap-green focus:outline-none">
          </div>
          <div>
            <label class="block text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Badge Thématique</label>
            <input type="text" value="${(r.tag || '').replace(/"/g, '&quot;')}" class="inp-ref-tag w-full border border-slate-300 dark:border-slate-700 rounded-lg px-2.5 py-1 text-xs font-semibold bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 focus:ring-1 focus:ring-burgeap-blue dark:focus:ring-burgeap-green focus:outline-none">
          </div>
        </div>
        <div>
          <label class="block text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Description Synthétique</label>
          <textarea rows="2" class="inp-ref-desc w-full border border-slate-300 dark:border-slate-700 rounded-lg p-2 text-xs bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 focus:ring-1 focus:ring-burgeap-blue dark:focus:ring-burgeap-green focus:outline-none leading-relaxed">${r.desc || ''}</textarea>
        </div>
      `;

      item.querySelector('.inp-ref-title').addEventListener('input', (e) => {
        r.title = e.target.value;
        this.scheduleLivePreview(false);
      });
      item.querySelector('.inp-ref-tag').addEventListener('input', (e) => {
        r.tag = e.target.value;
        this.scheduleLivePreview(false);
      });
      item.querySelector('.inp-ref-desc').addEventListener('input', (e) => {
        r.desc = e.target.value;
        this.scheduleLivePreview(false);
      });

      container.appendChild(item);
    });
  },

  bindEvents() {
    if (DOM.tabFr) DOM.tabFr.addEventListener('click', () => this.switchLang('fr'));
    if (DOM.tabEn) DOM.tabEn.addEventListener('click', () => this.switchLang('en'));
    if (DOM.btnRefreshPreview) {
      DOM.btnRefreshPreview.addEventListener('click', () => {
        this.saveCurrentForm();
        if (this._onPreviewRefresh) this._onPreviewRefresh(false);
        if (this._onScheduleAutoSave) this._onScheduleAutoSave();
      });
    }

    const chkBadges = document.getElementById('chk-show-badges');
    if (chkBadges) {
      const toggleHandler = (e) => {
        if (!State.cvData) State.cvData = {};
        State.cvData.show_badges = e.target.checked;
        this.saveCurrentForm();
        if (this._onPreviewRefresh) this._onPreviewRefresh(true);
        if (this._onScheduleAutoSave) this._onScheduleAutoSave();
      };
      chkBadges.addEventListener('change', toggleHandler);
      chkBadges.addEventListener('input', toggleHandler);
    }

    if (DOM.btnPitchBold) {
      DOM.btnPitchBold.addEventListener('click', (e) => {
        e.preventDefault();
        DOM.inpPitch.focus();
        Utils.formatText('bold');
        this.scheduleLivePreview(true);
      });
    }
    if (DOM.btnPitchItalic) {
      DOM.btnPitchItalic.addEventListener('click', (e) => {
        e.preventDefault();
        DOM.inpPitch.focus();
        Utils.formatText('italic');
        this.scheduleLivePreview(true);
      });
    }
    if (DOM.btnPitchClear) {
      DOM.btnPitchClear.addEventListener('click', (e) => {
        e.preventDefault();
        DOM.inpPitch.focus();
        Utils.formatText('removeFormat');
        this.scheduleLivePreview(true);
      });
    }

    if (DOM.btnEditorCrop) {
      DOM.btnEditorCrop.addEventListener('click', () => {
        if (State.cvData && State.cvData.photo_b64) {
          if (this._onOpenCropper) {
            this._onOpenCropper(`data:image/jpeg;base64,${State.cvData.photo_b64}`, (newB64) => {
              State.cvData.photo_b64 = newB64;
              this.updateAvatar();
              if (this._onPreviewRefresh) this._onPreviewRefresh(false);
            });
          }
        } else {
          DOM.editorPhotoInput.click();
        }
      });
    }

    if (DOM.btnEditorChangePhoto) {
      DOM.btnEditorChangePhoto.addEventListener('click', () => DOM.editorPhotoInput.click());
    }

    if (DOM.editorPhotoInput) {
      DOM.editorPhotoInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
          const file = e.target.files[0];
          Utils.optimizeImage(file).then(({ dataUrl }) => {
            if (this._onOpenCropper) {
              this._onOpenCropper(dataUrl, (newB64) => {
                if (!State.cvData) State.cvData = {};
                State.cvData.photo_b64 = newB64;
                this.updateAvatar();
                if (this._onPreviewRefresh) this._onPreviewRefresh(false);
              });
            }
          }).catch((err) => alert('Erreur traitement image : ' + err.message));
        }
      });
    }

    // Real-time Auto-Save & Reactive Live Preview
    if (DOM.viewEditor) {
      DOM.viewEditor.addEventListener('input', () => {
        this.saveCurrentForm();
        this.scheduleLivePreview(false);
        if (this._onScheduleAutoSave) this._onScheduleAutoSave();
      });
    }
  }
};
