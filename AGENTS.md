# Mémoire & Règles du Projet Ginger Burgeap CV Generator 2026

## 1. Vue d'ensemble & Architecture
* **Mission** : Générateur officiel de CV pour les collaborateurs Ginger Burgeap (formats 1 à 2 pages A4, bilingue FR/EN miroir, charte officielle 2026).
* **Architecture Backend** :
  * **Framework** : FastAPI asynchrone (`app/main.py`, `app/routers/cv.py`, `app/routers/render.py`).
  * **Validation & Données** : Pydantic V2 (`app/models/cv.py`) avec contraintes strictes.
  * **Moteur d'extraction** : [`app/services/extractor.py`](file:///home/beelink/projets/burgeap-cv-generator/app/services/extractor.py) avec support prioritaire **`anymd`** (Markdown structuré, conservation des tableaux multi-colonnes, OCR) et fallback vers `pdfplumber` / `pypdf` / `docx` / `pptx`.
  * **Orchestration IA** : [`app/services/ai_parser.py`](file:///home/beelink/projets/burgeap-cv-generator/app/services/ai_parser.py) via `agy` CLI (Gemini 3.8 Flash, authentification OAuth Pro) avec prompt métier, contraintes anti-IA et auto-réparation de traduction.
  * **Rendu PDF** : WeasyPrint + Jinja2 (`app/services/pdf_engine.py`, `app/templates/cv_template.html`).
* **Frontend** : Dual-pane réactif sans build lourd (Tailwind CSS, JS moderne, Cropper.js pour les portraits, thèmes Light/Dark).

## 2. Environnement & Commandes
* **Port** : `8085` (`http://localhost:8085`)
* **Lancement direct** : `python3 serve.py`
* **Processus PM2** : `burgeap-cv-generator` (`ecosystem.config.js`)
* **Interpréteur Python / Venv** : `/home/beelink/venv_antigravity_bot/bin/python3`
* **Tests unitaires & régression** :
  ```bash
  /home/beelink/venv_antigravity_bot/bin/pytest
  ```

## 3. Plugins & Intégrations Antigravity
* **`anymd` (CLI & MCP)** :
  * Utilisé en priorité dans `extractor.py` (`extract_text_with_anymd`) pour convertir les documents complexes (tableaux 2 colonnes, scans avec OCR).
  * Accessible à la volée via le serveur MCP `anymd` (`read`, `inspect`, `outline`, `search`).
* **`avoid-ai-writing`** :
  * Intégré au prompt de `ai_parser.py` (Section 8) : interdiction formelle des tournures clichées IA dans `pitch_fr` et `pitch_en` ("Fort de X années", "Passionné par", "Dynamique et polyvalent", "Pivotal", "Delve", "Beacon", "Spearheaded").
  * Exigence d'un style d'ingénieur d'affaires direct, factuel et précis.
* **`fullstack-dev-skills`** :
  * Compétences `fastapi-expert`, `python-pro` et `test-master` pour maintenir et faire évoluer les routes et les tests.

## 4. Règles Métier Strictes Ginger Burgeap
1. **Intitulé de poste (`role_fr` / `role_en`)** : Reprendre strictement le titre réel (ex: Chef de Projets, Ingénieur d'Études). Ne jamais inventer "Directeur de Projets" ni assigner abusivement la mention "Sites et Sols Pollués (SSP)" à des agronomes, écologues ou hydrogéologues.
2. **Expérience globale et ancienneté (`exp_fr` / `exp_en`)** :
   * Format Option 2 : `"X ans d'expérience, dont Y ans chez GINGER BURGEAP"` (ou `"X ans d'expérience chez GINGER BURGEAP"` si 100% de la carrière).
   * Calculée à l'obtention du diplôme qualifiant (Master 2, Ingénieur), sans compter les stages d'études antérieurs.
3. **Compétences clés vs Qualifications** :
   * À gauche (colonne bleue) : 5-6 puces résumant la posture et le pilotage sans citer de noms de clients.
   * À droite : 4 qualifications méthodologiques concrètes.
4. **Références de projets (`refs_fr` / `refs_en`)** :
   * STRICTEMENT des projets réalisés au sein de GINGER BURGEAP (ou Groupe Ginger).
   * Interdiction de lister des chantiers réalisés chez d'anciens employeurs (sauf arrivée récente < 1 an si moins de 3 projets Burgeap).
   * Toujours qualifier la mission en ingénierie conseil (AMO, MOE, Études, Diagnostic) et JAMAIS en travaux physiques de dépollution/terrassement.
5. **Rattachement d'agence (`agency_fr` / `agency_en`)** :
   * Par défaut rattaché à son agence locale (ex: Région Nord-Ouest • Agence de Rouen).
   * Ne basculer vers la "Direction des Métiers" que si mention explicite.

## 5. Agent Skills

### Issue tracker
GitHub Issues via `gh` CLI. Voir [`docs/agents/issue-tracker.md`](file:///home/beelink/projets/burgeap-cv-generator/docs/agents/issue-tracker.md).

### Triage labels
Vocabulaire canonique à 5 états (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). Voir [`docs/agents/triage-labels.md`](file:///home/beelink/projets/burgeap-cv-generator/docs/agents/triage-labels.md).

### Domain docs
Mono-contexte (`GLOSSARY.md` + `docs/adr/`). Voir [`docs/agents/domain.md`](file:///home/beelink/projets/burgeap-cv-generator/docs/agents/domain.md).
