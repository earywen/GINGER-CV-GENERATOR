# Ginger Burgeap CV Generator

Official CV generation system for Ginger Burgeap engineering collaborators conforming to the 2026 corporate guidelines.

## Language

**Ingestion Pipeline**:
The orchestrator transforming raw collaborator document files (PDF, Word DOCX, PowerPoint PPTX) and portrait images into a validated bilingual profile.
_Avoid_: CV parser, document converter, upload handler

**Structured CV**:
The canonical bilingual mirror data model (`BurgeapCVData`) containing validated French and English profile fields, professional qualifications, and project references.
_Avoid_: CV json, parsed output, profile dict

**Parse Cache**:
A disk-backed content-addressed store indexed by the SHA-256 fingerprint of the normalized source text and agency, preventing redundant LLM inference calls.
_Avoid_: Local cache, response cache, temp store

**Studio Bust**:
An officially cropped 3:4 portrait photo centered on the face and upper chest, or the corporate monogram fallback with employee initials.
_Avoid_: Avatar, user photo, headshot

**Document Engine**:
The unified rendering engine transforming a Structured CV into an official 1-2 page A4 print PDF (WeasyPrint) or vector HTML preview with strict typographical budgeting.
_Avoid_: PDF exporter, template renderer, print service

**Bilingual Bundle**:
A standardized ZIP package containing twin French and English official PDF resumes with corporate file naming conventions.
_Avoid_: Zip export, download archive, pdf pack

**Feedback Dispatcher**:
The ingestion and routing service saving user-submitted feedback to durable disk storage and synchronizing with GitHub Issues.
_Avoid_: Contact form, feedback handler, bug logger

**Diagnostic Snapshot**:
Sanitized client environment telemetry (browser user-agent, OS, viewport, active UI view) optionally attached to bug reports.
_Avoid_: Telemetry payload, debug dump, client info
