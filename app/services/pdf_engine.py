# -*- coding: utf-8 -*-
import os
import base64
import weasyprint

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "templates", "cv_template.html")
LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "static", "assets", "logo.png")

if os.path.exists(LOGO_PATH):
    with open(LOGO_PATH, "rb") as lf:
        LOGO_B64 = base64.b64encode(lf.read()).decode("utf-8")
else:
    LOGO_B64 = ""

GINGER_CURVE_SVG = '<svg viewBox="0 0 4507.26 4493.29" xmlns="http://www.w3.org/2000/svg" style="position: absolute; bottom: 0; right: 0; width: 33mm; height: 33mm; pointer-events: none;"><path d="M4436.17 4447.4 4436.17 70.71C2786.59 3317.65 59.48 4447.4 59.48 4447.4L4436.17 4447.4Z" fill="#FFFFFF"/><path d="M4436.17 4447.4 1501.68 4447.4C1501.68 4447.4 3402.47 3376.93 4436.17 426.98L4436.17 4447.4Z" fill="#96C63E"/></svg>'

def get_footer_text(agency_str: str, is_fr: bool) -> str:
    u = (agency_str or "").upper()
    if is_fr:
        if "ILE-DE-FRANCE" in u and "NORD-OUEST" in u:
            return "Ginger Burgeap – Direction Régionale Nord-Ouest & Ile-de-France"
        elif "ILE-DE-FRANCE" in u:
            return "Ginger Burgeap – Direction Régionale Ile-de-France"
        elif "QSE" in u or "QUALIT" in u:
            return "Ginger Burgeap – Direction QSE & Métrologies"
        else:
            return "Ginger Burgeap – Direction Régionale Nord-Ouest"
    else:
        if "ILE-DE-FRANCE" in u and "NORD-OUEST" in u:
            return "Ginger Burgeap – North-West & Ile-de-France Regional Directorate"
        elif "ILE-DE-FRANCE" in u:
            return "Ginger Burgeap – Ile-de-France Regional Directorate"
        elif "QSE" in u or "QUALIT" in u:
            return "Ginger Burgeap – QSE & Metrology Directorate"
        else:
            return "Ginger Burgeap – North-West Regional Directorate"

def render_html_template(data: dict, lang: str = "fr", font_scale: float = None, p1_count: int = None) -> str:
    is_fr = (lang.lower() == "fr")
    name = data.get("name", "Prénom NOM")
    role = data.get("role_fr" if is_fr else "role_en", "Titre du Poste")
    exp = data.get("exp_fr" if is_fr else "exp_en", "Années d'expérience")
    agency = data.get("agency_fr" if is_fr else "agency_en", "GINGER BURGEAP")
    footer_text = get_footer_text(agency, is_fr)
    t_projets_missions = "PROJETS & MISSIONS" if is_fr else "PROJECTS & MISSIONS"
    
    refs = data.get("refs_fr" if is_fr else "refs_en", [])
    total_refs = len(refs)

    # Maximize Page 1 filling down to bottom footer (holds up to 10 references)
    if p1_count is None:
        p1_count = total_refs if total_refs <= 10 else 10

    if font_scale is None:
        if p1_count <= 8:
            font_scale = 1.0
        elif p1_count == 9:
            font_scale = 0.97
        else: # 10
            font_scale = 0.95 if is_fr else 0.93

    photo_b64 = data.get("photo_b64")
    initials = data.get("initials")
    if not initials and not photo_b64:
        parts = name.split()
        initials = "".join(p[0].upper() for p in parts[:2]) if parts else "GB"
        
    if photo_b64:
        photo_html = f'<div class="photo-circle"><img src="data:image/jpeg;base64,{photo_b64}" alt="{name}" /></div>'
    else:
        photo_html = f'<div class="photo-circle initials-avatar"><span>{initials}</span></div>'
        
    t_formations = data.get("t_formations_fr", "FORMATIONS & DIPLÔMES") if is_fr else data.get("t_formations_en", "DEGREES & TRAINING")
    formations = data.get("formations_fr" if is_fr else "formations_en", [])
    formations_html = "".join(f"<li>{f}</li>" for f in formations)
    
    t_competences = data.get("t_competences_fr", "COMPÉTENCES CLÉS") if is_fr else data.get("t_competences_en", "CORE COMPETENCIES")
    competences = data.get("competences_fr" if is_fr else "competences_en", [])
    competences_html = "".join(f"<li>{c}</li>" for c in competences)
    
    t_exp_pro = "EXPÉRIENCES PROFESSIONNELLES" if is_fr else "PROFESSIONAL EXPERIENCE"
    exp_pros = data.get("exp_pros_fr" if is_fr else "exp_pros_en", [])
    exp_pro_html = "".join(f"<li>{e}</li>" for e in exp_pros)
    
    t_lang = "LANGUES & MOBILITÉ" if is_fr else "LANGUAGES & MOBILITY"
    langs = data.get("langs_fr" if is_fr else "langs_en", [])
    langs_html = "".join(f"<li>{l}</li>" for l in langs)
    
    t_profil = "PROFIL ET PARCOURS" if is_fr else "PROFILE & BACKGROUND"
    pitch = data.get("pitch_fr" if is_fr else "pitch_en", "")
    
    t_qualif = "PRINCIPALES QUALIFICATIONS" if is_fr else "CORE QUALIFICATIONS & EXPERTISE"
    qualifs = data.get("qualifs_fr" if is_fr else "qualifs_en", [])
    qualifs_html = "".join(f"<li>{q}</li>" for q in qualifs)
    
    t_refs = "PRINCIPALES RÉFÉRENCES – MISSIONS RÉCENTES" if is_fr else "KEY PROJECT REFERENCES – RECENT MISSIONS"
    
    # Split references between Page 1 and Page 2 (Option B)
    # Page 1 goes all the way to the bottom before ever overflowing to Page 2
    if total_refs <= p1_count:
        refs_p1 = refs
        refs_p2 = []
        has_p2 = False
        page_1_pagination = ""
        page_2_html = ""
    else:
        refs_p1 = refs[:p1_count]
        refs_p2 = refs[p1_count:p1_count + 8]
        has_p2 = True
        page_1_pagination = "Page 1 / 2"
        
        t_refs_p2 = "PRINCIPALES RÉFÉRENCES – SUITE DES MISSIONS" if is_fr else "KEY PROJECT REFERENCES – CONTINUED MISSIONS"
        t_suite_sidebar = "RÉFÉRENCES & EXPERTISE" if is_fr else "REFERENCES & EXPERTISE"
        desc_suite_sidebar = "Suite des missions et projets d'ingénierie conseil réalisés pour les maîtres d'ouvrage publics et privés." if is_fr else "Continued project references and environmental engineering missions conducted for public and private stakeholders."
        
        refs_p2_html = "".join(
            f'<div class="ref-item">'
            f'<div><span class="ref-header-line">{r.get("title", "")}</span>'
            f'<span class="ref-badge {"green" if (idx + len(refs_p1)) % 2 == 1 else ""}">{r.get("tag", "")}</span></div>'
            f'<div class="ref-desc-text">{r.get("desc", "")}</div>'
            f'</div>'
            for idx, r in enumerate(refs_p2)
        )
        
        page_2_html = f'''<div class="cv-page cv-page-2" id="cv-page-2">
  <div class="left-column left-column-p2">
    <div class="identity-block" style="margin-top: 5mm;">
      <h1>{name}</h1>
      <div class="job-title">{role}</div>
      <div class="experience-tag">{exp}</div>
    </div>
    <div class="side-sections-wrapper" style="margin-top: 8px;">
      <div>
        <div class="side-section-title">{t_suite_sidebar}</div>
        <p style="font-size: {6.8 * font_scale:.2f}pt; line-height: 1.35; color: #f8fafc; margin-bottom: 8px;">
          {desc_suite_sidebar}
        </p>
      </div>
      <div>
        <div class="side-section-title">{t_competences}</div>
        <ul class="side-list">{competences_html}</ul>
      </div>
    </div>
    {GINGER_CURVE_SVG}
  </div>
  <div class="right-column">
    <div class="right-header">
      <div class="agency-text">{agency} • {t_projets_missions}</div>
      <img class="logo-img" src="data:image/png;base64,{LOGO_B64}" alt="GINGER BURGEAP" />
    </div>
    <div>
      <div class="main-section-title">{t_refs_p2}</div>
      {refs_p2_html}
    </div>
  </div>
  <div class="page-footer">
    <span>{footer_text}</span>
    <span class="pagination-text">Page 2 / 2</span>
  </div>
</div>'''
    
    refs_html = "".join(
        f'<div class="ref-item">'
        f'<div><span class="ref-header-line">{r.get("title", "")}</span>'
        f'<span class="ref-badge {"green" if idx % 2 == 1 else ""}">{r.get("tag", "")}</span></div>'
        f'<div class="ref-desc-text">{r.get("desc", "")}</div>'
        f'</div>'
        for idx, r in enumerate(refs_p1)
    )
    
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as tf:
        tpl = tf.read()
        
    replacements = {
        "__LANG__": lang,
        "__NAME__": name,
        "__ROLE__": role,
        "__EXP__": exp,
        "__AGENCY__": agency,
        "__FOOTER_TEXT__": footer_text,
        "__PHOTO_HTML__": photo_html,
        "__LOGO_B64__": LOGO_B64,
        "__GINGER_CURVE_SVG__": GINGER_CURVE_SVG,
        "__T_FORMATIONS__": t_formations,
        "__FORMATIONS_HTML__": formations_html,
        "__T_COMPETENCES__": t_competences,
        "__COMPETENCES_HTML__": competences_html,
        "__T_EXP_PRO__": t_exp_pro,
        "__EXP_PRO_HTML__": exp_pro_html,
        "__T_LANG__": t_lang,
        "__LANGS_HTML__": langs_html,
        "__T_PROFIL__": t_profil,
        "__PITCH__": pitch,
        "__T_QUALIF__": t_qualif,
        "__QUALIFS_HTML__": qualifs_html,
        "__T_REFS__": t_refs,
        "__REFS_HTML__": refs_html,
        "__PAGE_1_PAGINATION__": page_1_pagination,
        "__PAGE_2_HTML__": page_2_html,
        "__BASE_FONT__": f"{7.9 * font_scale:.2f}",
        "__SIDE_FONT__": f"{6.8 * font_scale:.2f}",
        "__BODY_FONT__": f"{7.1 * font_scale:.2f}",
        "__LINE_HEIGHT__": f"{1.28 * font_scale:.2f}",
        "__GAP_SIZE__": str(int(6 * font_scale))
    }
    
    for k, v in replacements.items():
        tpl = tpl.replace(k, v)
        
    return tpl

def generate_pdf_bytes(data: dict, lang: str = "fr") -> bytes:
    is_fr = (lang.lower() == "fr")
    refs = data.get("refs_fr" if is_fr else "refs_en", [])
    total_refs = len(refs)
    
    # Fill Page 1 all the way down to the bottom (up to 10 references)
    target_p1 = total_refs if total_refs <= 10 else 10
    expected_pages = 1 if total_refs <= 10 else 2
    
    candidate_scales = [0.95, 0.94, 0.93] if target_p1 >= 10 else ([0.97, 0.95] if target_p1 == 9 else [1.0, 0.97, 0.95])
    if not is_fr and target_p1 >= 10:
        candidate_scales = [0.93, 0.94, 0.92, 0.95]
        
    for scale in candidate_scales:
        html = render_html_template(data, lang=lang, font_scale=scale, p1_count=target_p1)
        doc = weasyprint.HTML(string=html).render()
        if len(doc.pages) == expected_pages:
            return doc.write_pdf()
            
    # Fallback with p1=9 if 10 caused an unexpected spill
    if target_p1 > 9:
        for scale in [0.96, 0.94]:
            html = render_html_template(data, lang=lang, font_scale=scale, p1_count=9)
            doc = weasyprint.HTML(string=html).render()
            if len(doc.pages) == expected_pages:
                return doc.write_pdf()

    # Final fallback
    html = render_html_template(data, lang=lang, font_scale=0.93, p1_count=min(total_refs, 9))
    return weasyprint.HTML(string=html).write_pdf()
