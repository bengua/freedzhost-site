# Univers FreedzHost — constitution transversale

Un seul univers visuel et éditorial pour toutes les surfaces et tous les
projets de l'enseigne **FreedzHost** (freedzhost.cloud). Toute évolution se
mesure à cette constitution. Nom de code : « le terrier ».

## 0. Architecture de marque

**FreedzHost** est l'enseigne parapluie — le nom du site, de l'activité et
de la communauté. Elle porte plusieurs projets, dont :

- **Inari** — l'essaim agentique (webapp foxroom, APK, personas). Un projet
  parmi d'autres, pas le nom du site.
- **Les tutos** — contenus gratuits en chapitres.
- **Le campus** — formations en ligne (espace membres).
- **Les services** — mise en place d'IA en entreprise ou chez les
  particuliers, selon besoins et ressources matérielles ; conseil.
- **Les briques open source** — les dépôts publics (turnstile, fh-bench,
  fh-probes, inframagotchi, purrd, et Inari à sa publication) : on offre
  toutes les briques, pas le mur. Chaque dépôt renvoie à son tuto et vit
  sous la même enseigne.

Tous partagent la même constitution visuelle et éditoriale. Inari le renard
reste la mascotte de l'enseigne entière, pas seulement du projet éponyme.

## 0bis. Principe directeur : accessible à tout le monde

L'objectif de l'enseigne est de rendre la chose accessible à **tout le
monde**, au double sens du terme :

- **Pédagogique** : aucun prérequis supposé. Le curieux non technique comme
  l'entrepreneur pressé doivent pouvoir suivre chaque chapitre sans jargon
  gratuit, avec des phénomènes du quotidien pour expliquer les concepts
  complexes. Coder avec l'IA est bien ; comprendre ce qu'on fait est mieux.
- **Matérielle et physique** : WCAG 2.2 (contrastes, cibles 44 px, focus
  visible, `prefers-reduced-motion`), contenus lisibles sur petit écran et
  vieux matériel, poids de page contenu, et toujours un chemin pour les
  configurations modestes (free tiers, petits modèles, nocode quand c'est
  le bon outil).

Toute décision — design, contenu, code — se juge à cette question : est-ce
que ça rapproche quelqu'un de plus de la chose, ou est-ce que ça l'en
écarte ?

## 0ter. Posture : tuteurs, pas gourous

Nous sommes leurs **tuteurs**, le temps qu'ils se renforcent sur le sujet.
Cela implique :

- **Donner du sens à chaque étape** : on n'empile pas des commandes, on
  explique pourquoi avant comment — chaque geste doit pouvoir être refait
  seul, sans nous, plus tard.
- **Révéler la progression** : le lecteur voit où il en est (parcours,
  chapitres, étapes cochées) et ce qu'il saura faire ensuite.
- **Rendre autonome, puis s'effacer** : la réussite c'est quand il n'a plus
  besoin de nous — les formations payantes approfondissent, elles ne
  retiennent pas en otage.
- **L'aboutissement : des users sachant.** Pas des consommateurs d'outils
  magiques, pas des copieurs de commandes — des utilisateurs qui savent ce
  qu'ils font, pourquoi ils le font, et ce que ça implique (coût, vie
  privée, limites). Un user sachant choisit souverainement.
- **Respecter le rythme de chacun** : escalader par paliers, jamais
  humilier un débutant, jamais ennuyer un confirmé (les approfondissements
  sont signalés, pas imposés).

## 1. Couleurs

| Token | Valeur | Rôle |
|---|---|---|
| `den-bg` | `#12100e` | fond principal (charbon chaud) |
| `den-bg-2` | `#1c1814` | fond surélevé (cartes, tiroirs) |
| `copper` | `#e07a2f` | accent unique : liens, focus, repères |
| `cream` | `#efe9e0` | texte principal |
| `cream-dim` | `#a89f93` | texte secondaire |
| `sage` | `#7ba05b` | succès / validation uniquement |
| `line` | `#2b251f` | filets et bordures |

Règles : un seul accent (copper). Pas de dégradé criard ; halos cuivrés à
opacité ≤ 0.08. Le fond de la mascotte est toujours le fond de la surface
(sprites détourés, jamais de cadre ni de vignette).

## 2. Typographie

- **Display** : Fraunces (OFL), auto-hébergée woff2 subsetté latin — titres,
  chapitres, chiffres héroïques. Graisse 600, `font-display: swap`.
- **Texte** : stack système (`system-ui, -apple-system, Segoe UI, Roboto`),
  17-18 px, interligne 1.6.
- **Code** : stack mono système.
- APK : Fraunces embarquée dans les assets, même hiérarchie.
- Confiance Moonshot : les titres peuvent être très grands, l'espace vide
  est un matériau, pas un manque.

## 3. Mascotte et personnages

- **Inari** (renard original, esprit des sept queues) = maître de maison :
  accueil de l'app, pied d'articles, écrans vides, erreurs.
- **Personas** = incarnation de chaque harness/provider (zen, merica,
  artiste, militaires…) : tuile de room, page de série, teaser.
- Banque unique : `swarmfox/fox-sprites-persona/` — sprites détourés
  (alpha propre via `key_sprites.py`), partagée par les trois surfaces.
- Comportement : discret mais vivant. Micro-animations (respire, salue,
  nano-séquences), jamais de boucle agressive. Burger & cie = ennui seul.

## 4. Motion

- Courbes : `sine.inOut` (respiration), `power2.out` (entrées),
  `power2.in` (sorties).
- Durées : 150 ms (micro), 300 ms (standard), 600 ms (transitions de vue).
- `prefers-reduced-motion` respecté partout : tout devient statique.
- Site : animations CSS pures (scroll-timeline), zéro JS d'animation.

## 5. Voix et éditorial

- Voix « nous », honnêteté totale (mesures réelles, limites affichées),
  zéro marketing. Tutoiement possible dans les vidéos, vouvoiement sobre
  dans les tutos écrits.
- Contenu en **chapitres numérotés** (01., 02.…) avec titres qui racontent
  (ADN ponpon-mania) — la table des chapitres donne envie de dévorer.
- FR d'abord, jumeau EN systématique (parité stricte).
- Chaque série est incarnée par son persona (ADN ribbit.dk).

## 6. Iconographie et logo

- Logo : silhouette d'Inari (renard aux sept queues), une seule forme,
  déclinée en monochrome cream ou copper. Nom public de l'enseigne :
  **FreedzHost**. « Inari » désigne le projet agentique et la mascotte.

## 7. Application par surface

| Surface | État | Écart à résorber |
|---|---|---|
| Site | refonte en cours (piliers + art) | appliquer cette constitution (spec art) |
| Webapp foxroom | gui à refondre | mêmes tokens CSS, tiroir, tuiles-personas |
| APK Inari | 0.33.0 alpha | thème Material dérivé des tokens, Fraunces, mascotte plein-écran sans bandeau |

Toute nouvelle surface (montre, dashboard ntfy…) hérite de ces tokens.
