# Univers FreedzHost Inari — constitution transversale

Un seul univers visuel et éditorial pour les trois surfaces : **site**
(freedzhost.cloud), **webapp foxroom**, **APK Inari**. Toute évolution de
l'une se mesure à cette constitution. Nom de code : « le terrier ».

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
  déclinée en monochrome cream ou copper. Nom public : **FreedzHost Inari**.

## 7. Application par surface

| Surface | État | Écart à résorber |
|---|---|---|
| Site | refonte en cours (piliers + art) | appliquer cette constitution (spec art) |
| Webapp foxroom | gui à refondre | mêmes tokens CSS, tiroir, tuiles-personas |
| APK Inari | 0.33.0 alpha | thème Material dérivé des tokens, Fraunces, mascotte plein-écran sans bandeau |

Toute nouvelle surface (montre, dashboard ntfy…) hérite de ces tokens.
