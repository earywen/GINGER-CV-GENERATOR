---
name: Ginger Burgeap Design System
description: Système de design officiel 2026 pour le générateur de CV d'ingénierie conseil Ginger Burgeap
colors:
  primary: "#13375f"
  primary-dark: "#0e2846"
  accent-green: "#96C63E"
  accent-green-dark: "#60ab56"
  accent-blue-soft: "#eef4fa"
  surface-light: "#ffffff"
  background-light: "#f8fafc"
  surface-dark: "#1e293b"
  background-dark: "#0f172a"
  background-darker: "#020617"
  border-light: "#e2e8f0"
  border-dark: "#334155"
  text-light: "#0f172a"
  text-dark: "#f8fafc"
  text-muted-light: "#64748b"
  text-muted-dark: "#94a3b8"
  slate-300: "#cbd5e1"
  slate-600: "#475569"
rounded:
  xs: "4px"
  sm: "6px"
  md: "10px"
  lg: "14px"
  full: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
---

# Design System

<!-- impeccable:design-schema 1 -->

## Overview

Interface métier d'ingénierie conseil à double volet (*Dual-Pane fixed viewport*) pour la génération, l'édition et l'exportation haute fidélité de CVs officiels Ginger Burgeap. Conçue pour une concentration maximale et une vitesse d'édition sans fatigue oculaire, avec prise en charge native du **Mode Sombre** et du **Mode Clair**.

## Colors

### Palette Principale (Corporate Ginger Burgeap)
- **Bleu Burgeap Principal** (`#13375f`) : Identité institutionnelle, en-tête, titres de sections, boutons d'action primaire.
- **Vert Ginger** (`#96C63E`) : Accent corporate, badges, puces d'expertise, barre de progression et état actif.
- **Vert Forêt** (`#60ab56`) : Badges thématiques secondaires et hover states sur le vert.
- **Bleu Nuit** (`#0e2846`) : États de survol sombres et renforts contrastés.

### Thème Clair (Light Mode)
- **Fond de page** : `slate-100` (`#f1f5f9`) pour séparer clairement les surfaces de travail.
- **Surfaces conteneurs** : `white` (`#ffffff`) avec bordure discrète `slate-200` (`#e2e8f0`).
- **Texte courant** : `slate-800` (`#1e293b`) avec sous-titres en `slate-500` (`#64748b`).

### Thème Sombre (Dark Mode)
- **Fond de page** : `slate-950` (`#020617`), créant une immersion studio feutrée.
- **Surfaces conteneurs** : `slate-900` (`#0f172a`) avec bordures subtiles `slate-800` (`#1e293b`).
- **Texte courant** : `slate-100` (`#f8fafc`) avec sous-titres en `slate-400` (`#94a3b8`).
- **Éléments interactifs** : Contrastes amplifiés respectant WCAG AA (≥ 4.5:1).

## Typography

- **Police principale** : `Segoe UI, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`.
- **Hiérarchie d'échelle** :
  - `h1` : 1.5rem (24px), font-weight: 800, tracking: -0.025em.
  - `h2` : 1.25rem (20px), font-weight: 700.
  - `h3` : 1rem (16px), font-weight: 700.
  - Body : 0.875rem (14px) et 0.75rem (12px) pour les labels de formulaires techniques.
- **Chiffres et Trigrammes** : Tabular nums avec police mono pour les trigrammes et codes (`MARI`, `JGR`).

## Layout

- **Header fixe** : 56px de hauteur, intégrant le logo officiel, le titre, le switch de langue/collaborateur et le basculeur Dark/Light mode.
- **Double volet (Dual-Pane)** :
  - **Volet Gauche (Éditeur)** : Défilement vertical indépendant, champs organisés par zones logiques sans empilement de cartes imbriquées.
  - **Volet Droit (Studio Visualiseur)** : Fixe, centré, avec barre d'outils de zoom, bascule rapide FR/EN, boutons d'export et prévisualisation instantanée.
  - **Viewport PDF** : Simule une table lumineuse d'architecte/ingénieur avec centrage géométrique parfait de la page A4.

## Elevation & Depth

- Ombres douces multidirectionnelles (`box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05)`).
- En Dark Mode, la profondeur est exprimée par la nuance des surfaces (`slate-950` vs `slate-900` vs `slate-800`) et de fins liserés lumineux (`border-slate-800`).

## Shapes & Radii

- Conteneurs principaux : `rounded-2xl` (16px).
- Boutons et inputs : `rounded-xl` (12px) et `rounded-lg` (8px).
- Médaillons photos et avatars : Parfaitement circulaires (`rounded-full`).

## Components

- **Theme Toggle** : Bouton pillule compact avec icônes Soleil / Lune, transition fluide 150ms.
- **Dropzone** : Zone en pointillés avec fond réactif au glisser-déposer et feedback instantané.
- **Avatars d'initiales** : Fond bleu corporate `#13375f` avec typographie grasse blanche contrastée.
- **Boutons d'action** : Bouton primaire bleu Ginger avec texte blanc contrasté, bouton ZIP vert Ginger avec texte foncé lisible.

## Do's and Don'ts

### Do
- Conserver impérativement la page A4 intérieure en blanc papier réel (`#ffffff`) dans le viewer PDF, qu'on soit en Dark Mode ou en Light Mode (le document physique ne change pas de couleur !).
- Soigner les contrastes sur tous les labels de formulaire en mode sombre.
- Utiliser le vert `#96C63E` comme touche d'accentuation précise.

### Don't
- Ne jamais imbriquer de cartes blanches dans des cartes blanches (*nested cards*). Préférer de discrets séparateurs ou du spacing structuré.
- Ne pas utiliser de texte en gradient criard.
- Ne pas laisser de balises `<img>` vides sans source.
