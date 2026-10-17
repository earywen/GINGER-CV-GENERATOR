#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Generation Script - Ginger Burgeap Rouen 2026.
Automates the end-to-end extraction, AI parsing (Gemini 3.8 Flash via agy CLI),
studio bust photo cropping, JSON data persistence, and WeasyPrint PDF generation
for all collaborators of the Rouen agency.
"""

import os
import sys
import time
import json
import zipfile
import argparse
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core import get_logger, settings
from app.services.cv_pipeline import ingest_cv, attach_photo_or_initials
from app.services.pdf_engine import generate_pdf_bytes
from app.utils.formatters import sanitize_filename

logger = get_logger("batch_rouen")

DEFAULT_ROUEN_DIR = PROJECT_ROOT / "CV GINGER BURGEAP 2026" / "ROUEN"
DEFAULT_AGENCY = "RÉGION NORD-OUEST • AGENCE DE ROUEN"

# Collaborators explicitly excluded (e.g. left company)
EXCLUDED_CODES = {"RMDG"}


class CollaboratorTask:
    def __init__(
        self,
        code: str,
        folder_name: str,
        cv_dir: Path,
        source_cv_file: Path,
        photo_file: Optional[Path]
    ):
        self.code = code.upper()
        self.folder_name = folder_name
        self.cv_dir = cv_dir
        self.source_cv_file = source_cv_file
        self.photo_file = photo_file
        self.cached = False
        self.success = False
        self.error_msg: Optional[str] = None
        self.collab_name: Optional[str] = None
        self.fr_pdf_path: Optional[Path] = None
        self.en_pdf_path: Optional[Path] = None
        self.json_path: Optional[Path] = None


def discover_collaborators(base_dir: Path, only_codes: Optional[List[str]] = None) -> List[CollaboratorTask]:
    """
    Scans the Rouen folder structure and matches source CVs with their studio photos.
    """
    cv_base = base_dir / "CV Rouen"
    photo_base = base_dir / "Photos Rouen"

    if not cv_base.exists():
        raise FileNotFoundError(f"Dossier source introuvable: {cv_base}")

    tasks: List[CollaboratorTask] = []

    for item in sorted(cv_base.iterdir(), key=lambda p: p.name):
        if not item.is_dir():
            continue

        # Extract code from folder name (e.g., Arthur_MENIER_ARME -> ARME)
        parts = item.name.split("_")
        code = parts[-1].strip().upper()

        if code in EXCLUDED_CODES:
            logger.info(f"Ignoré (exclu de l'entreprise) : {item.name} ({code})")
            continue

        if only_codes and code not in [c.upper() for c in only_codes]:
            continue

        # Find source CV file (.pdf or .docx not starting with CV_)
        source_candidates = [
            f for f in item.iterdir()
            if f.is_file()
            and f.suffix.lower() in [".pdf", ".docx"]
            and not f.name.startswith("CV_")
        ]

        if not source_candidates:
            logger.warning(f"Aucun CV source trouvé dans {item.name}")
            continue

        source_cv = source_candidates[0]

        # Find matching photo in Photos Rouen/<code>/
        photo_dir = photo_base / code
        photo_file = None
        if photo_dir.exists() and photo_dir.is_dir():
            photo_candidates = [
                f for f in photo_dir.iterdir()
                if f.is_file()
                and f.suffix.lower() in [".jpg", ".jpeg", ".png"]
                and f.name.lower() != "thumbs.db"
            ]
            if photo_candidates:
                photo_file = photo_candidates[0]

        tasks.append(
            CollaboratorTask(
                code=code,
                folder_name=item.name,
                cv_dir=item,
                source_cv_file=source_cv,
                photo_file=photo_file
            )
        )

    return tasks


async def process_collaborator(
    task: CollaboratorTask,
    agency: str,
    force_parse: bool,
    deliverables_dir: Path,
    delay_after_llm: float
) -> bool:
    """
    Runs extraction, parsing, photo attachment, and PDF generation for a single collaborator.
    """
    print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"▶ Traitement de [{task.code}] {task.folder_name}")
    print(f"  • Source CV : {task.source_cv_file.name}")
    print(f"  • Photo     : {task.photo_file.name if task.photo_file else 'Aucune (initiales automatiques)'}")

    try:
        # 1. Vérification d'un JSON local déjà ajusté ou appel au pipeline unifié
        json_filename = f"{task.code.lower()}_data_multirefs.json"
        task_json_path = task.cv_dir / json_filename

        if task_json_path.exists() and not force_parse:
            print(f"  📄 Données locales trouvées (ajustements conservés) : {json_filename}")
            structured_data = json.loads(task_json_path.read_text(encoding="utf-8"))
            task.cached = True
            if task.photo_file and task.photo_file.exists():
                photo_bytes = task.photo_file.read_bytes()
                attach_photo_or_initials(structured_data, photo_bytes=photo_bytes)
            else:
                attach_photo_or_initials(structured_data, photo_bytes=None)
        else:
            photo_bytes = task.photo_file.read_bytes() if (task.photo_file and task.photo_file.exists()) else None
            print(f"  ⚡ Exécution via le pipeline unifié ingest_cv (cache & IA)...")
            cv_bytes = task.source_cv_file.read_bytes()
            structured_data = await ingest_cv(
                cv_filename=task.source_cv_file.name,
                cv_bytes=cv_bytes,
                photo_bytes=photo_bytes,
                agency=agency
            )
            task.cached = False

        # 4. Sauvegarde du fichier JSON multiréférences
        task_json_path.write_text(json.dumps(structured_data, ensure_ascii=False, indent=2), encoding="utf-8")
        task.json_path = task_json_path
        print(f"  💾 Données JSON sauvegardées : {json_filename}")

        # 5. Rendu des PDF officiels (FR et EN)
        print(f"  🖨 Génération des PDF WeasyPrint (FR & EN)...")
        start_pdf = time.time()
        pdf_fr_bytes = await asyncio.to_thread(generate_pdf_bytes, structured_data, "fr")
        pdf_en_bytes = await asyncio.to_thread(generate_pdf_bytes, structured_data, "en")
        elapsed_pdf = time.time() - start_pdf
        print(f"  ✓ PDF générés en {elapsed_pdf:.1f}s")

        # Noms de fichiers standardisés
        fn_fr = sanitize_filename(collab_name, lang="FR", ext="pdf")
        fn_en = sanitize_filename(collab_name, lang="EN", ext="pdf")

        # Écriture dans le dossier individuel
        local_fr = task.cv_dir / fn_fr
        local_en = task.cv_dir / fn_en
        local_fr.write_bytes(pdf_fr_bytes)
        local_en.write_bytes(pdf_en_bytes)
        task.fr_pdf_path = local_fr
        task.en_pdf_path = local_en

        # Écriture dans le dossier global LIVRABLES/PDF/
        pdf_deliverables = deliverables_dir / "PDF"
        pdf_deliverables.mkdir(parents=True, exist_ok=True)
        (pdf_deliverables / fn_fr).write_bytes(pdf_fr_bytes)
        (pdf_deliverables / fn_en).write_bytes(pdf_en_bytes)

        print(f"  ✅ Succès : {fn_fr} & {fn_en}")
        task.success = True
        return True

    except Exception as e:
        logger.error(f"Échec sur {task.code}: {e}", exc_info=True)
        print(f"  ❌ ERREUR sur [{task.code}] : {e}")
        task.success = False
        task.error_msg = str(e)
        return False


def build_consolidated_zip(tasks: List[CollaboratorTask], zip_path: Path):
    """
    Builds a single consolidated ZIP deliverable organized by collaborator folder.
    Ex: Arthur_MENIER_ARME/CV_Arthur_MENIER_FR.pdf
    """
    print(f"\n📦 Création de l'archive consolidée (1 dossier par collaborateur) : {zip_path.name}...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for task in tasks:
            if not task.success:
                continue
            folder = task.folder_name
            if task.fr_pdf_path and task.fr_pdf_path.exists():
                zf.write(task.fr_pdf_path, arcname=f"{folder}/{task.fr_pdf_path.name}")
            if task.en_pdf_path and task.en_pdf_path.exists():
                zf.write(task.en_pdf_path, arcname=f"{folder}/{task.en_pdf_path.name}")
            if task.json_path and task.json_path.exists():
                zf.write(task.json_path, arcname=f"{folder}/{task.json_path.name}")

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"✓ Archive prête ({size_mb:.2f} MB) : {zip_path}")


def print_summary(tasks: List[CollaboratorTask], total_elapsed: float):
    """
    Prints a formatted summary table of the batch operation.
    """
    success_count = sum(1 for t in tasks if t.success)
    cached_count = sum(1 for t in tasks if t.cached)
    llm_count = sum(1 for t in tasks if t.success and not t.cached)
    failed_count = sum(1 for t in tasks if not t.success)

    print("\n" + "=" * 65)
    print("           RÉCAPITULATIF DU BATCH GINGER BURGEAP ROUEN")
    print("=" * 65)
    print(f" Collaborateurs traités  : {len(tasks)}")
    print(f"   • Succès               : {success_count} / {len(tasks)}")
    print(f"   • Depuis le cache (0$) : {cached_count}")
    print(f"   • Parsés avec Gemini   : {llm_count}")
    print(f"   • Échecs               : {failed_count}")
    print(f" Temps total d'exécution : {total_elapsed:.1f} secondes")
    print("-" * 65)

    if failed_count > 0:
        print("\n❌ Détails des échecs :")
        for t in tasks:
            if not t.success:
                print(f"  - [{t.code}] {t.folder_name} : {t.error_msg}")

    print("=" * 65 + "\n")


async def main():
    parser = argparse.ArgumentParser(
        description="Batch CV Generation for Ginger Burgeap Rouen 2026."
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=DEFAULT_ROUEN_DIR,
        help="Chemin vers le dossier racine Rouen (contenant 'CV Rouen' et 'Photos Rouen')"
    )
    parser.add_argument(
        "--agency",
        type=str,
        default=DEFAULT_AGENCY,
        help=f"Libellé de l'agence (défaut: '{DEFAULT_AGENCY}')"
    )
    parser.add_argument(
        "--only",
        nargs="+",
        help="Traiter uniquement un ou plusieurs codes (ex: --only ARME TSA EL)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Vérifie les fichiers et les correspondances sans rien générer"
    )
    parser.add_argument(
        "--force-parse",
        action="store_true",
        help="Ignore le cache et force un nouvel appel à Gemini 3.8 Flash"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.5,
        help="Délai en secondes après chaque appel LLM (défaut: 3.5s)"
    )
    parser.add_argument(
        "--repack",
        action="store_true",
        help="Reconstitue uniquement le ZIP consolidé à partir des fichiers existants sur disque"
    )

    args = parser.parse_args()

    base_dir = args.dir.resolve()
    print(f"📁 Répertoire de travail : {base_dir}")

    tasks = discover_collaborators(base_dir, only_codes=args.only)
    if not tasks:
        print("Aucun collaborateur trouvé à traiter.")
        return

    print(f"🔍 {len(tasks)} collaborateur(s) identifié(s) :")
    for t in tasks:
        has_photo = "✓ Photo" if t.photo_file else "✗ Pas de photo"
        print(f"  [{t.code}] {t.folder_name} ({has_photo})")

    if args.dry_run:
        print("\n[DRY RUN] Mode simulation actif. Aucune modification apportée.")
        return

    deliverables_dir = base_dir / "LIVRABLES"
    deliverables_dir.mkdir(parents=True, exist_ok=True)
    zip_path = deliverables_dir / "CV_GINGER_BURGEAP_ROUEN_2026.zip"

    if args.repack:
        print("\n📦 Mode --repack actif : association des fichiers existants sur disque...")
        for task in tasks:
            fr_candidates = list(task.cv_dir.glob("CV_*_FR.pdf"))
            en_candidates = list(task.cv_dir.glob("CV_*_EN.pdf"))
            json_candidates = list(task.cv_dir.glob("*_data_multirefs.json"))

            if fr_candidates and en_candidates:
                task.success = True
                task.fr_pdf_path = fr_candidates[0]
                task.en_pdf_path = en_candidates[0]
                if json_candidates:
                    task.json_path = json_candidates[0]
            else:
                task.success = False
                task.error_msg = "Fichiers PDF non trouvés dans le dossier"

        build_consolidated_zip(tasks, zip_path)
        print("✓ Reconditionnement terminé avec succès !")
        return

    start_total = time.time()

    for task in tasks:
        await process_collaborator(
            task=task,
            agency=args.agency,
            force_parse=args.force_parse,
            deliverables_dir=deliverables_dir,
            delay_after_llm=args.delay
        )

    total_elapsed = time.time() - start_total

    # Build final deliverable ZIP
    build_consolidated_zip(tasks, zip_path)

    print_summary(tasks, total_elapsed)


if __name__ == "__main__":
    asyncio.run(main())
