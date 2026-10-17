# -*- coding: utf-8 -*-
import json
import asyncio
import tempfile
import os
import re
from typing import Dict, Any, Optional, List

from app.core import settings, get_logger
from app.models.cv import get_cv_extraction_json_schema

logger = get_logger(__name__)

def _clean_json_response(raw_text: str) -> Dict[str, Any]:
    """
    Strips potential markdown code blocks (```json ... ```) and parses JSON.
    """
    text = raw_text.strip()
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)
    return json.loads(text)

def _build_prompt(raw_text: str, default_agency: str) -> str:
    return f"""Tu es un expert RH et ingénierie chez GINGER BURGEAP.
IMPORTANT : Tu dois répondre DIRECTEMENT avec le JSON structuré sans utiliser d'outils, sans chercher de fichiers sur le disque et sans exécuter de commande shell. Toutes les informations nécessaires sont déjà fournies ci-dessous.

Voici le texte brut extrait du CV d'un collaborateur :
---
{raw_text}
---

MISSION :
Tu dois extraire fidèlement les informations du collaborateur et les structurer au format officiel Ginger Burgeap 2026 en Français et en Anglais.

RÈGLES STRICTES ET NON NÉGOCIABLES :

1. INTITULÉ DU POSTE (role_fr / role_en) :
- Reprends STRICTEMENT l'intitulé de poste officiel indiqué dans le document source (ex: "Cheffe de Projets en Sites et Sols Pollués", "Ingénieur Agronome", "Directrice adjointe", "Responsable d'Agence", "Ingénieur d'Études", etc.).
- INTERDICTION FORMELLE d'inventer un titre de poste non mentionné (ex: ne jamais inventer "Directrice de Projet" ou "DP SSP" si ce n'est pas le titre réel).
- INTERDICTION de transformer une sous-spécialité technique (ex: "Risque sanitaire", "EQRS") en intitulé de poste.
- INTERDICTION d'attribuer la mention "Sites et Sols Pollués (SSP)" si le collaborateur est dans un autre métier de Burgeap (ex: Agronomie, Écologie, Biodiversité, Eau / Hydrogéologie, Déchets, Bâtiment durable, Énergie, etc.). Respecte scrupuleusement la spécialité réelle du collaborateur !

2. EXPÉRIENCE GLOBALE ET ANCIENNETÉ (exp_fr / exp_en) :
- FORMAT OBLIGATOIRE (Option 2) :
  * Si le collaborateur a des expériences antérieures hors Burgeap :
    FR : "X ans d'expérience, dont Y ans chez GINGER BURGEAP"
    EN : "X years of experience, including Y years at GINGER BURGEAP"
  * Si 100% de sa carrière s'est faite chez Ginger Burgeap (X == Y) :
    FR : "X ans d'expérience chez GINGER BURGEAP"
    EN : "X years of experience at GINGER BURGEAP"
  * Si le collaborateur a rejoint Ginger Burgeap très récemment (< 1 an) :
    FR : "X ans d'expérience, chez GINGER BURGEAP depuis [Année]"
    EN : "X years of experience, at GINGER BURGEAP since [Year]"
- RÈGLE DE CALCUL DE L'EXPÉRIENCE GLOBALE (X ans) :
  * Calculée rigoureusement à partir de l'obtention du diplôme de fin d'études qualifiant (Master 2, Diplôme d'Ingénieur, Licence Pro, etc.) jusqu'à aujourd'hui, OU d'après la mention explicite du CV si elle est indiquée textuellement.
  * INTERDICTION FORMELLE de compter les années d'études ou de stages antérieurs à une reprise d'études comme de l'expérience professionnelle d'ingénieur continue (ex: si un collaborateur a été technicien en 2014 puis a repris des études de Master entre 2015 et 2018, l'expérience d'ingénieur débute à l'obtention du Master en 2018).
- RÈGLE DE CALCUL DE L'ANCIENNETÉ BURGEAP (Y ans) :
  * Calculer l'ancienneté cumulée effective au sein de GINGER BURGEAP (ou entités du Groupe Ginger) jusqu'à aujourd'hui.

3. EXPÉRIENCES PROFESSIONNELLES (exp_pros_fr / exp_pros_en) :
- Ne mentionne QUE les véritables employeurs (contrats de travail réels) du collaborateur (2 à 3 lignes max).
- RÈGLE ANTI-CONFUSION PRESTATAIRES : Ne confonds JAMAIS une entreprise de travaux, un sous-traitant, un bureau d'études partenaire ou un client intervenant sur des chantiers (ex: GRS Valtech, Séché, Bouygues, Total...) avec l'employeur du collaborateur !
- Si le collaborateur n'a travaillé que chez Ginger Burgeap, mentionne son évolution interne (ex: "Depuis 2019 : GINGER BURGEAP - Ingénieur puis Chef de projet"). N'INVENTE AUCUN employeur externe pour combler la liste !
- RÔLES ET RÉSEAUX INTERNES : Si le collaborateur participe à un réseau national d'experts ou à des responsabilités transverses récentes (ex: "Équipe nationale EDF depuis 2024", "Référent technique national"), mentionne expressément ce rôle dans sa ligne d'expérience Ginger Burgeap.

4. COMPÉTENCES CLÉS (competences_fr / competences_en) :
- Les compétences clés (dans la colonne latérale bleue) doivent refléter des postures, rôles d'action et domaines d'intervention généraux (5 à 6 puces concises, 4 à 8 mots par puce).
- RÈGLE ANTI-REDONDANCE QUALIFICATIONS : INTERDICTION FORMELLE de paraphraser ou recopier à l'identique les intitulés des 4 paragraphes de "PRINCIPALES QUALIFICATIONS" !
  * Les "Compétences clés" (à gauche) résument la posture, le pilotage et les types de missions (ex: "Direction technique & pilotage de projets complexes", "Expertise contradictoire & tiers-expertise", "Audits de conformité réglementaire (ICPE/ALUR)", "Essais de traitabilité & bioremédiation in-situ", "Assistance technique stratégique").
  * Les "Principales qualifications" (à droite) détaillent les 4 domaines méthodologiques concrets du collaborateur.
- NEUTRALITÉ DES CLIENTS : INTERDICTION FORMELLE de mentionner des noms de clients ou donneurs d'ordres spécifiques entre parenthèses dans la liste des compétences (ex: NE PAS écrire "Suivi piézométrique... (EDF/ORANO)", écris simplement "Suivi piézométrique et surveillance de la qualité des eaux sur sites industriels et nucléaires"). Les noms de clients appartiennent EXCLUSIVEMENT aux titres des références de projets !

5. DIPLÔMES ET ENSEIGNEMENT SUPÉRIEUR (diplomes_fr / diplomes_en) :
- Extrais fidèlement tous les diplômes académiques réels (année, intitulé exact, école/université, ex: "2018 : Master 2 Géologie – BRGM Campus (45)", "2015 : Diplôme d'Ingénieur – ENSG Nancy").
- Ne mentionne ici QUE les diplômes de l'enseignement supérieur (Doctorat, Master 2, Diplôme d'Ingénieur, Master 1, Licence, BTS, DUT, DTSP...).
- Traduction anglaise valorisante et académique (ex: "Master's Degree (M2)", "Engineering Degree", "Bachelor of Science"). Ne JAMAIS utiliser "Training" pour désigner un diplôme académique !

6. FORMATIONS PROFESSIONNELLES & CERTIFICATIONS (formations_fr / formations_en) :
- EXHAUSTIVITÉ ABSOLUE ET OBLIGATOIRE : Extrais impérativement TOUTES les formations professionnelles continues, habilitations réglementaires de sécurité, certifications et formations techniques mentionnées dans le CV.
- Exemples fréquents chez Burgeap : AIPR (Concepteur / Encadrant / Opérateur), SST (Sauveteur Secouriste du Travail), CATEC (Espaces confinés), Risque chimique N1/N2, Habilitations électriques (H0B0...), Formations logicielles ou méthodologiques (Surfer, SIG, modélisation hydrogéologique, etc.).
- INTERDICTION FORMELLE d'omettre ou de tronquer des formations réelles ! Si le CV en liste 4, 5 ou plus, inclus-les TOUTES sans exception.
- Traduction technique anglaise irréprochable (bannir le mot "Training" seul) :
  * SST -> "SST – Occupational First Aid Certification"
  * AIPR -> "AIPR – Network Safety & Damage Prevention Accreditation (Designer / Supervisor)"
  * CATEC -> "CATEC – Confined Space Entry Safety Certification"
  * Risque chimique -> "Chemical Risk Safety Certification (N1 / N2)"
  * Habilitation électrique -> "Electrical Safety Accreditation (H0B0)"
  * Formations techniques -> "Professional Training in [Domaine] / [Logiciel]"

7. LANGUES ET MOBILITÉ (langs_fr / langs_en) :
- Indique fidèlement le niveau réel des langues (ex: "Français, Espagnol : Langues maternelles").
- CALIBRAGE ANGLAIS RÉALISTE : Si le CV indique "Anglais : courant" sans mention explicite de bilinguisme natif, de niveau C1/C2 ou de score officiel (TOEIC > 900), calibre sobrement et professionnellement :
  FR : "Anglais : Niveau professionnel (B2)"
  EN : "English: Professional working proficiency (B2)"
- Extrais impérativement la Mobilité géographique et les permis (ex: "Mobilité : Permis B - Déplacements régionaux / nationaux") sous forme d'une puce dédiée dans cette liste.

8. PROFIL ET PARCOURS / PITCH (pitch_fr / pitch_en) :
- Rédige un pitch de synthèse sobre, élégant, valorisant et factuel d'environ 45 à 55 mots.
- RÈGLE STRICTE ANTI-CLICHÉS IA (AVOID-AI-WRITING) :
  * BANNIR FORMELLEMENT les tournures générées par IA et l'empilement de buzzwords creux :
    - INTERDIT en français : "Fort de ses X années...", "Passionné par...", "Dynamique et polyvalent...", "Acteur clé...", "Dans un monde en pleine mutation...", "Au cœur des enjeux de...", "Véritable moteur...", "Mettant à profit...", "Un atout majeur...".
    - INTERDIT en anglais : "delve", "pivotal", "spearheaded", "beacon", "testament to", "fostering", "tapestry", "game-changer", "dynamic professional", "harnessing", "unwavering commitment".
  * Adopter un style d'ingénieur conseil direct, rigoureux, factuel et précis (rôle, responsabilités clés, savoir-faire éprouvés, secteurs d'intervention).
- BANNIR LE JARGON POMPEUX ou les accumulations artificielles d'acronymes (ex: éviter d'empiler "EQRS/ARR" ou des superlatifs excessifs). Reste dans un ton d'ingénieur conseil rigoureux et naturel.
- FIDÉLITÉ AU PÉRIMÈTRE RÉEL : Reste strictement fidèle aux périmètres réels sans sur-spécialisation restrictive abusive (ex: si le collaborateur est responsable des dossiers EDF, n'écris pas "nucléaire" s'il intervient également sur le thermique ou les friches).
- Entoure de balises <strong> le prénom NOM ainsi que 2 ou 3 domaines ou savoir-faire clés réels.

9. PRINCIPALES QUALIFICATIONS (qualifs_fr / qualifs_en) :
- Génère exactement 4 qualifications clés basées sur l'expérience réelle du collaborateur.
- Chaque point commence par <strong>Domaine clé</strong> : description concrète et précise des compétences réelles (adaptées à sa vraie spécialité).

10. PRINCIPALES RÉFÉRENCES (refs_fr / refs_en) :
- RÈGLE D'OR DES RÉFÉRENCES GINGER BURGEAP :
  * Les références de projets et missions extraites doivent être STRICTEMENT des projets réalisés au sein de GINGER BURGEAP (ou entités du Groupe Ginger).
  * INTERDICTION FORMELLE d'extraire des projets ou chantiers réalisés pour le compte d'EMPLOYEURS PRÉCÉDENTS (ex: projets chez Envisol, Antea, etc.). Dans une réponse d'appel d'offres pour Ginger Burgeap, seuls les projets portés par l'entreprise doivent figurer ici !
  * Exception unique : Si le collaborateur a rejoint Ginger Burgeap très récemment (< 1 an) et que le CV source ne contient pas assez de projets Burgeap (moins de 3 références), tu peux alors intégrer ses projets antérieurs les plus significatifs en indiquant clairement l'employeur d'origine dans la description.
- DISTINCTION RIGOUREUSE INGÉNIERIE CONSEIL vs TRAVAUX DE CHANTIER :
  * Ginger Burgeap est une société d'ingénierie et de conseil environnemental (études, diagnostics, plans de gestion, essais de faisabilité, maîtrise d'œuvre MOE, assistance à maîtrise d'ouvrage AMO). Ginger Burgeap ne réalise JAMAIS directement de travaux physiques de dépollution ou de terrassement.
  * INTERDICTION FORMELLE de titrer une mission par un raccourci de travaux (ex: titrer "RÉHABILITATION DE..." ou "TRAVAUX DE DÉPOLLUTION...") si la mission portait sur des études, un diagnostic ou des essais !
  * Précise SYSTÉMATIQUEMENT la nature réelle de la mission dans le titre et le tag :
    - "ÉTUDES ET ESSAIS DE FAISABILITÉ / TRAITABILITÉ..." (si études/essais)
    - "DIAGNOSTIC ENVIRONNEMENTAL ET PLAN DE GESTION..." (si diagnostic)
    - "MAÎTRISE D'ŒUVRE (MOE) DE DÉPOLLUTION..." (si supervision de travaux)
    - "ASSISTANCE À MAÎTRISE D'OUVRAGE (AMO)..." (si accompagnement du maître d'ouvrage)
- Extrais un MAXIMUM de projets et missions de référence réels (généralement entre 6 et 12 références selon l'expérience du collaborateur, classées des plus récentes aux plus anciennes).
- title : Titre du projet / client / site en MAJUSCULES (ex: "MAÎTRISE D'ŒUVRE DE DÉPOLLUTION DU SITE INDUSTRIEL X – VALENCIENNES (59)").
- tag : Badge thématique court (2 à 4 mots en MAJUSCULES, fidèle au domaine du projet, ex: "AGRONOMIE & SOLS", "MAÎTRISE D'ŒUVRE", "GESTION DES DÉCHETS", "RISQUE INONDATION", "EPR2").
- desc : Synthèse claire et factuelle de 18 à 28 mots (contexte, missions réalisées par le collaborateur, résultats).

11. TRADUCTION ANGLAISE STRICTE (role_en, exp_en, pitch_en, refs_en, qualifs_en, etc.) :
- Traduction technique de haute qualité, terminologie d'ingénierie environnementale irréprochable.
- INTERDICTION ABSOLUE DU COPIER-COLLER FRANÇAIS : Les champs suffixés par '_en' (notamment 'pitch_en' et 'qualifs_en') DOIVENT ÊTRE INTÉGRALEMENT EN ANGLAIS.
- INTERDICTION FORMELLE de recopier le texte français de 'pitch_fr' dans 'pitch_en'. 'pitch_en' doit être une rédaction autonome et fluide en langue anglaise ("Executive Profile Summary").

12. AGENCE ET RATTACHEMENT (agency_fr / agency_en) :
- DISTINCTION TITRE DE POSTE vs ENTITÉ DE RATTACHEMENT :
  * Le titre de poste (ex: "Directeur de projets", "Chef de projets", "Ingénieur") NE DÉTERMINE PAS l'entité de rattachement organisationnelle !
  * Un "Directeur de projets" peut parfaitement être rattaché à son agence locale (ex: Nicolas HUBERT est Directeur de projets rattaché à l'Agence de Rouen / Région Nord-Ouest).
  * Par défaut, le collaborateur reste rattaché à son agence locale : '{default_agency}' (ex: "RÉGION NORD-OUEST • AGENCE DE ROUEN" / "NORTH-WEST REGION • ROUEN BRANCH").
  * EXCEPTION FORMELLE : Ne bascule vers une direction transverse ou nationale que si le document ou le profil mentionne EXPLICITEMENT ce rattachement hiérarchique/organisationnel (ex: "Direction des Métiers", "Pôle Métier Sites et Sols Pollués", "Direction QSE & Métrologie", comme pour Hervé HOGIE qui est rattaché au Pôle Métier national) :
    FR : "DIRECTION DES MÉTIERS • PÔLE MÉTIER SITES ET SOLS POLLUÉS" (ou direction correspondante)
    EN : "TECHNICAL EXPERTISE DIRECTORATE • CONTAMINATED SITES & SOILS EXPERTISE CENTER"
"""

def _is_french_text(text: str) -> bool:
    """Detects whether an ostensibly English string is actually in French."""
    if not text or len(text.strip()) < 10:
        return False
    sample = f" {text.lower()} "
    markers = [
        " est ", " dispose ", " avec ", " ingénieur ", " cheffe ",
        " chef de ", " années ", " expérience ", " spécialisé ", " dans ", " projets "
    ]
    match_count = sum(1 for m in markers if m in sample)
    return match_count >= 2

async def _quick_translate_to_english(text_to_translate: str, context: str = "") -> Optional[str]:
    """Translates a French snippet into professional engineering English using agy CLI."""
    prompt = (
        f"Tu es un traducteur technique bilingue chez GINGER BURGEAP.\n"
        f"Traduis fidèlement le texte suivant du Français vers l'Anglais professionnel ({context}).\n"
        f"IMPORTANT : Conserve les balises HTML éventuelles (ex: <strong>...</strong>).\n"
        f"Retourne DIRECTEMENT le texte traduit sans explications ni politesses :\n\n{text_to_translate}"
    )
    cmd = [
        settings.AGY_BIN_PATH,
        "-p", prompt,
        "--effort", "low",
        "--model", settings.AGY_MODEL,
        "--print-timeout", "30s"
    ]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd="/tmp",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=35)
        if proc.returncode == 0:
            res = json.loads(stdout.decode("utf-8", errors="ignore"))
            out = res.get("response", "").strip()
            match = re.search(r"```(?:json)?\s*(.*?)\s*```", out, re.DOTALL)
            if match:
                out = match.group(1).strip()
            return out
    except Exception as e:
        logger.error(f"Auto-repair quick translation failed: {e}")
    return None

async def _ensure_english_integrity(structured: Dict[str, Any]) -> Dict[str, Any]:
    """
    Self-healing guard: validates that English fields are indeed in English.
    If pitch_en or qualifs_en accidentally remained in French, auto-repairs them.
    """
    pitch_fr = structured.get("pitch_fr", "")
    pitch_en = structured.get("pitch_en", "")

    # 1. Validate pitch_en
    needs_pitch_fix = False
    if pitch_en and pitch_fr and (pitch_en.strip() == pitch_fr.strip()):
        needs_pitch_fix = True
    elif _is_french_text(pitch_en):
        needs_pitch_fix = True

    if needs_pitch_fix and pitch_fr:
        logger.warning("pitch_en detected as untranslated French! Triggering auto-repair...")
        fixed_pitch = await _quick_translate_to_english(pitch_fr, context="Executive profile summary")
        if fixed_pitch:
            structured["pitch_en"] = fixed_pitch
            logger.info("pitch_en successfully auto-repaired to English.")

    # 2. Validate qualifs_en
    qualifs_fr = structured.get("qualifs_fr", [])
    qualifs_en = structured.get("qualifs_en", [])
    if qualifs_en and any(_is_french_text(q) for q in qualifs_en) and qualifs_fr:
        logger.warning("qualifs_en detected as untranslated French! Triggering auto-repair...")
        fixed_qualifs = await _quick_translate_to_english(
            json.dumps(qualifs_fr, ensure_ascii=False),
            context="JSON array of 4 key qualifications"
        )
        if fixed_qualifs:
            try:
                parsed_q = json.loads(fixed_qualifs)
                if isinstance(parsed_q, list) and len(parsed_q) == len(qualifs_fr):
                    structured["qualifs_en"] = parsed_q
                    logger.info("qualifs_en successfully auto-repaired to English.")
            except Exception:
                pass

    return structured

async def parse_cv_with_agy(raw_text: str, default_agency: str = "RÉGION NORD-OUEST") -> Dict[str, Any]:
    """
    Orchestrates the agy CLI (authenticated via Google OAuth / Google Pro) to parse and structure
    the resume text against the official Pydantic schema.
    """
    prompt = _build_prompt(raw_text, default_agency)
    schema = get_cv_extraction_json_schema()

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as sf:
        json.dump(schema, sf, ensure_ascii=False)
        schema_path = sf.name

    agy_bin = settings.AGY_BIN_PATH

    cmd = [
        agy_bin,
        "-p", prompt,
        "--output-format", "json",
        "--json-schema", schema_path,
        "--disable-slash-commands",
        "--effort", settings.AGY_EFFORT,
        "--model", settings.AGY_MODEL,
        "--print-timeout", f"{settings.AGY_TIMEOUT_SECONDS}s"
    ]

    logger.info(f"Starting agy CLI parser process (model: {settings.AGY_MODEL}, effort: {settings.AGY_EFFORT})")

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd="/tmp",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=settings.AGY_TIMEOUT_SECONDS + 15
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise TimeoutError(f"Le processus agy a dépassé le délai imparti de {settings.AGY_TIMEOUT_SECONDS}s.")

        if proc.returncode != 0:
            err_msg = stderr.decode("utf-8", errors="ignore")
            logger.error(f"agy CLI failed (code {proc.returncode}): {err_msg}")
            raise RuntimeError(f"Erreur agy CLI (code {proc.returncode}): {err_msg}")

        output_str = stdout.decode("utf-8", errors="ignore")
        res_json = json.loads(output_str)

        structured = res_json.get("structured_output")
        if not structured and "response" in res_json:
            structured = _clean_json_response(res_json["response"])

        if not structured:
            raise ValueError("Le modèle n'a pas retourné de structure de données valide.")

        # Self-healing translation check: ensures all English fields are genuinely in English
        structured = await _ensure_english_integrity(structured)

        return structured

    finally:
        if os.path.exists(schema_path):
            os.remove(schema_path)
