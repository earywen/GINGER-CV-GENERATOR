# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Collaborateurs, ingénieurs d'études, chefs de projets et équipes RH / commerciales de Ginger Burgeap ayant besoin de moderniser, traduire (FR/EN) et standardiser rapidement des CVs d'ingénierie conseil au format officiel 2026 (1 à 2 pages A4).

## Product Purpose

Fournir une application web locale fluide, moderne et élégante permettant :
1. De déposer un CV existant (PDF, DOCX, PPTX) et une photo portrait.
2. D'extraire, restructurer et traduire automatiquement le profil via l'intelligence artificielle (Gemini 3.8 Flash via agy OAuth Google Pro, sans frais d'API).
3. D'ajuster et centrer la photo dans un médaillon studio officiel ou de générer des initiales corporate.
4. D'éditer en direct les informations techniques dans une interface en double volet réactive.
5. De prévisualiser le rendu A4 WeasyPrint en temps réel et de télécharger le PDF ou le pack bilingue ZIP.

## Positioning

Générateur de CV dédié exclusivement aux standards d'ingénierie de Ginger Burgeap, combinant la puissance de l'IA générative avec la précision chirurgicale de mise en page CSS Paged Media. Aucune dépendance à des clés d'API tierces payantes.

## Operating Context

- Application web à double panneau (*dual-pane viewport*) : volet formulaire scrollable à gauche, volet prévisualisation PDF sticky avec zoom à droite.
- Utilisée aussi bien sur des écrans portables (13-14 pouces) que sur des stations de travail avec grands écrans (1080p, 1440p, 4K).
- Support natif d'un **Light Mode** et d'un **Dark Mode** complet sélectionnable manuellement ou selon les préférences de l'OS.

## Capabilities and Constraints

- **Thèmes** : Light mode et Dark mode avec bascule instantanée (icône soleil/lune) et mémorisation dans `localStorage`.
- **Fidélité A4** : La page de CV elle-même reste blanche (fond d'impression officiel `#ffffff`), tandis que l'application hôte adopte des teintes sombres raffinées (Slate-900 / Slate-800 avec accents Burgeap Blue `#13375f` et Burgeap Green `#96C63E`).
- **Pas de build lourd** : L'interface repose sur Tailwind CSS et JavaScript moderne sans étape de compilation webpack/vite, garantissant une exécution immédiate.
- **Accessibilité (a11y)** : Respect strict des ratios de contraste WCAG AA (4.5:1), suppression des cartes imbriquées superflues, et typographie claire.

## Brand Commitments

- **Couleurs officielles Ginger Burgeap** :
  - Bleu Principal : `#13375f`
  - Bleu Nuit : `#0e2846`
  - Vert Ginger : `#96C63E`
  - Vert Forêt : `#60ab56`
  - Bleu Ciel Clair : `#eef4fa`
- Logo officiel haute résolution.
- Courbe graphique Ginger dans le footer.

## Product Principles

1. **Clarté Opérationnelle** : La mise en page doit privilégier la lisibilité des données techniques et la rapidité de validation.
2. **Double Thème Élégant** : Le Dark Mode doit offrir un confort visuel reposant sans dénaturer l'identité corporate Ginger Burgeap.
3. **Zéro Friction** : Feedback visuel immédiat (états de chargement soignés, transitions fluides, validation en direct).
4. **Fidélité Absolue** : Ce que l'utilisateur voit dans l'aperçu correspond exactement au document PDF imprimé.
