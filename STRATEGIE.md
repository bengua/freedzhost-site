# STRATÉGIE freedzhost.cloud — feuille de route (actée le 2026-10-21)

Objectif : devenir **la plateforme de référence francophone** homelab / IA locale /
souveraineté numérique — lisible par les humains comme par les agents IA.

Ces 4 piliers priment sur toute autre considération de code, design ou contenu.

## Pilier 1 — UX et parcours d'apprentissage (Learning Maps)

- **Micro-parcours scénarisés** (3 à 7 étapes max) avec objectif clair
  (ex: « Faire tourner un modèle 7B ») — fini les longues listes de tutos génériques.
- **Chaque tuto donne le VRAI mode opératoire** : étapes testées sur l'infra réelle,
  commandes exactes, vérifications (« si tu vois X, c'est bon »), pièges.
- **Suivi de progression déclaratif** via `localStorage` (gamification sans tracking externe).
- UI : accueil = format éditorial dense (manifeste, revue) ; pages catégories
  (ex. `/local-ai/`) = grille de cartes pour l'exploration.

## Pilier 2 — Découvrabilité et référencement agentique (SEO IA)

- **Pagefind** (index statique au build) pour la recherche locale — pas Fuse.js,
  pensé pour >500 pages.
- **Schema.org prioritaire** : chaque article = JSON-LD `TechArticle`
  (`proficiencyLevel`, `timeRequired`, `dateModified`) ; site = schéma `Organization`.

## Pilier 3 — Ligne éditoriale et transparence

- Page « À propos » : architecture du homelab, méthodes de test (mesures
  tokens/s, outils), limites (« ce que nous ne promettons pas »).
- **Obsolescence gérée** : chaque tuto affiche date de dernière révision +
  versions exactes des modèles/logiciels testés.
- Schémas Mermaid.js pour l'architecture, avec **description textuelle
  obligatoire** (`<figcaption>` / alt) pour l'accessibilité.

## Pilier 4 — Accessibilité (WCAG 2.2) et performances

- Core Web Vitals stricts : LCP optimisé (compression images), zéro script
  tiers non essentiel.
- Cibles tactiles ≥ 44×44 px en mobile, contrastes respectés, états de focus
  visibles dans le thème sombre.

## Chantier parallèle — Base de connaissances publiable

Construire une base de connaissances fiable, complète, détaillée pour nourrir
les contenus de formation. Identifier les parcours d'apprentissage gratuits et
bien construits (code, IA, logiciels spécifiques, shell, Linux, PowerShell,
large spectre), les étudier et **transposer leur pédagogie au format
freedzhost.cloud** (micro-parcours, mode opératoire testé, double audience).
Objectif : devenir une bonne adresse — la référence.
