# -*- coding: utf-8 -*-
import json
import asyncio
import tempfile
import os

import shutil

CV_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "trigram": {"type": "string"},
        "initials": {"type": "string"},
        "role_fr": {"type": "string"},
        "role_en": {"type": "string"},
        "exp_fr": {"type": "string"},
        "exp_en": {"type": "string"},
        "agency_fr": {"type": "string"},
        "agency_en": {"type": "string"},
        "formations_fr": {"type": "array", "items": {"type": "string"}},
        "formations_en": {"type": "array", "items": {"type": "string"}},
        "competences_fr": {"type": "array", "items": {"type": "string"}},
        "competences_en": {"type": "array", "items": {"type": "string"}},
        "exp_pros_fr": {"type": "array", "items": {"type": "string"}},
        "exp_pros_en": {"type": "array", "items": {"type": "string"}},
        "langs_fr": {"type": "array", "items": {"type": "string"}},
        "langs_en": {"type": "array", "items": {"type": "string"}},
        "pitch_fr": {"type": "string"},
        "pitch_en": {"type": "string"},
        "qualifs_fr": {"type": "array", "items": {"type": "string"}},
        "qualifs_en": {"type": "array", "items": {"type": "string"}},
        "refs_fr": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "tag": {"type": "string"},
                    "desc": {"type": "string"}
                },
                "required": ["title", "tag", "desc"]
            }
        },
        "refs_en": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "tag": {"type": "string"},
                    "desc": {"type": "string"}
                },
                "required": ["title", "tag", "desc"]
            }
        }
    },
    "required": [
        "name", "trigram", "initials", "role_fr", "role_en", "exp_fr", "exp_en",
        "agency_fr", "agency_en", "formations_fr", "formations_en", "competences_fr",
        "competences_en", "exp_pros_fr", "exp_pros_en", "langs_fr", "langs_en",
        "pitch_fr", "pitch_en", "qualifs_fr", "qualifs_en", "refs_fr", "refs_en"
    ]
}

async def parse_cv_with_agy(raw_text: str, default_agency: str = "RÉGION NORD-OUEST") -> dict:
    prompt = f"""Tu es un expert RH et ingénierie chez GINGER BURGEAP.
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

2. EXPÉRIENCES PROFESSIONNELLES (exp_pros_fr / exp_pros_en) :
- Ne mentionne QUE les véritables employeurs (contrats de travail réels) du collaborateur (2 à 3 lignes max).
- RÈGLE ANTI-CONFUSION PRESTATAIRES : Ne confonds JAMAIS une entreprise de travaux, un sous-traitant, un bureau d'études partenaire ou un client intervenant sur des chantiers (ex: GRS Valtech, Séché, Bouygues, Total...) avec l'employeur du collaborateur !
- Si le collaborateur n'a travaillé que chez Ginger Burgeap, mentionne son évolution interne (ex: "Depuis 2019 : GINGER BURGEAP - Ingénieur puis Chef de projet"). N'INVENTE AUCUN employeur externe pour combler la liste !

3. FORMATIONS ET DIPLÔMES (formations_fr / formations_en) :
- Extrais fidèlement tous les diplômes réels (année, intitulé exact, école/université, ex: "2015 : Diplôme d'Ingénieur Agronome - Montpellier SupAgro").
- N'invente aucun diplôme et ne tronque pas les formations réelles.
- Si le CV mentionne des habilitations professionnelles ou certifications sécurité (AIPR, CATEC, SST, PR1, etc.), intègre-les.

4. LANGUES ET MOBILITÉ (langs_fr / langs_en) :
- Indique fidèlement le niveau réel des langues (ex: "Français, Espagnol : Langues maternelles", "Anglais : Professionnel (B2)"). Ne mets JAMAIS "courant" par défaut si le collaborateur est de langue maternelle ou bilingue.
- Extrais impérativement la Mobilité géographique et les permis (ex: "Mobilité : Permis B - Déplacements régionaux / nationaux") sous forme d'une puce dédiée dans cette liste.

5. PROFIL ET PARCOURS / PITCH (pitch_fr / pitch_en) :
- Rédige un pitch de synthèse sobre, élégant, valorisant et factuel d'environ 45 à 55 mots.
- BANNIR LE JARGON POMPEUX ou les accumulations artificielles d'acronymes (ex: éviter d'empiler "EQRS/ARR" ou des superlatifs excessifs). Reste dans un ton d'ingénieur conseil rigoureux et naturel.
- Entoure de balises <strong> le prénom NOM ainsi que 2 ou 3 domaines ou savoir-faire clés réels.

6. PRINCIPALES QUALIFICATIONS (qualifs_fr / qualifs_en) :
- Génère exactement 4 qualifications clés basées sur l'expérience réelle du collaborateur.
- Chaque point commence par <strong>Domaine clé</strong> : description concrète et précise des compétences réelles (adaptées à sa vraie spécialité).

7. PRINCIPALES RÉFÉRENCES (refs_fr / refs_en) :
- Extrais un MAXIMUM de projets et missions de référence réels mentionnés dans le document source (généralement entre 6 et 12 références selon l'expérience du collaborateur, classées des plus récentes aux plus anciennes).
- Ne te limite surtout pas à 4 références : inclus tous les projets et chantiers majeurs cités dans le CV !
- title : Titre du projet / client / site en MAJUSCULES (ex: "RÉHABILITATION DU SITE INDUSTRIEL X – VALENCIENNES (59)").
- tag : Badge thématique court (2 à 4 mots en MAJUSCULES, fidèle au domaine du projet, ex: "AGRONOMIE & SOLS", "MAÎTRISE D'ŒUVRE", "GESTION DES DÉCHETS", "RISQUE INONDATION", "EPR2").
- desc : Synthèse claire et factuelle de 18 à 28 mots (contexte, missions réalisées par le collaborateur, résultats).

8. TRADUCTION ANGLAISE (role_en, exp_en, pitch_en, refs_en, qualifs_en, etc.) :
- Traduction technique de haute qualité, terminologie d'ingénierie environnementale irréprochable.

9. AGENCE :
- Si l'agence n'est pas spécifiée dans le document : '{default_agency}'.
"""

    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as sf:
        json.dump(CV_SCHEMA, sf, ensure_ascii=False)
        schema_path = sf.name

    agy_bin = shutil.which('agy') or os.path.expanduser('~/.local/bin/agy')

    try:
        cmd = [
            agy_bin,
            '-p', prompt,
            '--output-format', 'json',
            '--json-schema', schema_path,
            '--disable-slash-commands',
            '--effort', 'low',
            '--model', 'gemini-3.8-flash-low'
        ]
        
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd='/tmp',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            err_msg = stderr.decode('utf-8', errors='ignore')
            raise RuntimeError(f"Erreur agy CLI (code {proc.returncode}): {err_msg}")
            
        res_json = json.loads(stdout.decode('utf-8', errors='ignore'))
        structured = res_json.get('structured_output')
        if not structured and 'response' in res_json:
            # Fallback parsing direct
            structured = json.loads(res_json['response'])
            
        return structured
        
    finally:
        if os.path.exists(schema_path):
            os.remove(schema_path)

