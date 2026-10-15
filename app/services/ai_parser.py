# -*- coding: utf-8 -*-
import json
import asyncio
import tempfile
import os
import re
from typing import Dict, Any

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

4. DIPLÔMES ET ENSEIGNEMENT SUPÉRIEUR (diplomes_fr / diplomes_en) :
- Extrais fidèlement tous les diplômes académiques réels (année, intitulé exact, école/université, ex: "2018 : Master 2 Géologie – BRGM Campus (45)", "2015 : Diplôme d'Ingénieur – ENSG Nancy").
- Ne mentionne ici QUE les diplômes de l'enseignement supérieur (Doctorat, Master 2, Diplôme d'Ingénieur, Master 1, Licence, BTS, DUT, DTSP...).
- Traduction anglaise valorisante et académique (ex: "Master's Degree (M2)", "Engineering Degree", "Bachelor of Science"). Ne JAMAIS utiliser "Training" pour désigner un diplôme académique !

5. FORMATIONS PROFESSIONNELLES & CERTIFICATIONS (formations_fr / formations_en) :
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

6. LANGUES ET MOBILITÉ (langs_fr / langs_en) :
- Indique fidèlement le niveau réel des langues (ex: "Français, Espagnol : Langues maternelles", "Anglais : Professionnel (B2)"). Ne mets JAMAIS "courant" par défaut si le collaborateur est de langue maternelle ou bilingue.
- Extrais impérativement la Mobilité géographique et les permis (ex: "Mobilité : Permis B - Déplacements régionaux / nationaux") sous forme d'une puce dédiée dans cette liste.

7. PROFIL ET PARCOURS / PITCH (pitch_fr / pitch_en) :
- Rédige un pitch de synthèse sobre, élégant, valorisant et factuel d'environ 45 à 55 mots.
- BANNIR LE JARGON POMPEUX ou les accumulations artificielles d'acronymes (ex: éviter d'empiler "EQRS/ARR" ou des superlatifs excessifs). Reste dans un ton d'ingénieur conseil rigoureux et naturel.
- Entoure de balises <strong> le prénom NOM ainsi que 2 ou 3 domaines ou savoir-faire clés réels.

8. PRINCIPALES QUALIFICATIONS (qualifs_fr / qualifs_en) :
- Génère exactement 4 qualifications clés basées sur l'expérience réelle du collaborateur.
- Chaque point commence par <strong>Domaine clé</strong> : description concrète et précise des compétences réelles (adaptées à sa vraie spécialité).

9. PRINCIPALES RÉFÉRENCES (refs_fr / refs_en) :
- Extrais un MAXIMUM de projets et missions de référence réels mentionnés dans le document source (généralement entre 6 et 12 références selon l'expérience du collaborateur, classées des plus récentes aux plus anciennes).
- Ne te limite surtout pas à 4 références : inclus tous les projets et chantiers majeurs cités dans le CV !
- title : Titre du projet / client / site en MAJUSCULES (ex: "RÉHABILITATION DU SITE INDUSTRIEL X – VALENCIENNES (59)").
- tag : Badge thématique court (2 à 4 mots en MAJUSCULES, fidèle au domaine du projet, ex: "AGRONOMIE & SOLS", "MAÎTRISE D'ŒUVRE", "GESTION DES DÉCHETS", "RISQUE INONDATION", "EPR2").
- desc : Synthèse claire et factuelle de 18 à 28 mots (contexte, missions réalisées par le collaborateur, résultats).

10. TRADUCTION ANGLAISE (role_en, exp_en, pitch_en, refs_en, qualifs_en, etc.) :
- Traduction technique de haute qualité, terminologie d'ingénierie environnementale irréprochable.

11. AGENCE :
- Si l'agence n'est pas spécifiée dans le document : '{default_agency}'.
"""

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

        return structured

    finally:
        if os.path.exists(schema_path):
            os.remove(schema_path)
