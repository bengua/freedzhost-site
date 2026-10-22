# Charte Inari — l'identité du renard, une seule fois, pour toutes les surfaces

Statut : normatif. Toute nouvelle représentation d'Inari (icône, illustration, sprite,
persona, vidéo, print) DOIT dériver des deux sources canoniques définies ici et citer
cette charte dans sa PR. Toute autre proposition est refusée en revue. C'est la règle
anti-dérive actée le 22/10 : on ne refait plus, on dérive.

## 1. Deux incarnations canoniques — jamais de troisième

### La Signature (la marque)
La silhouette géométrique cuivrée, renard assis de profil gauche, neuf queues en
éventail. Contextes : logo, icônes (favicon, APK, GitHub), filigrane, hero du site,
OG images, print, tout ce qui est statique ou doit être lisible en 16 px comme en affiche.
Source de vérité : `site_build.py` (`INARI_TAILS`, `INARI_BODY`, `INARI_EYE`) dans
freedzhost-site, exportée en asset autonome par `tools/export-inari-signature.py`
(→ `assets/inari/signature.svg`). Toute surface qui a besoin de la marque consomme
cet asset, elle ne redessine pas.

### Le Compagnon (l'incarnation vivante)
Le renard sprite rendu (banques webp 512 natif, séquences f_XX sans trou). Contextes :
mascotte de l'APK et de la webapp, tuiles des rooms, campus (habitant des pages),
vidéos et teasers — tout ce qui bouge, réagit et accompagne.
Source de vérité : les banques de sprites dans swarmfox
(`android/app/src/main/assets/fox/sprites/`, miroir `gui/public/foxbot/sprites/`).

### Le lien obligatoire entre les deux
La Signature et le Compagnon sont LE MÊME animal : assis, profil gauche trois-quarts,
museau pointu, œil en fente, neuf queues en éventail. Quand ils apparaissent sur la
même surface (site, campus), le Compagnon ne contredit jamais la pose de la Signature.
La Signature est la forme réduite à l'essentiel ; le Compagnon est la même forme habitée.

## 2. Palette canonique

- Cuivre Inari : dégradé `#f2a35c` (haut) → `#e07a2f` (55 %) → `#7d3f14` (base).
- Fond : charbon `#12100e` (famille `--bg`), lumière radiale `#1d1712`.
- Braises (kitsunebi) : or pâle `rgba(255,224,176)`, cuivre `rgba(224,122,47)`,
  braise profonde `rgba(150,70,20)`.
- En icône (≤ 48 px) : pas de dégradé — cuivre plein `#e07a2f` sur charbon.
- Un seul accent cuivre à la fois par écran (règle UNIVERS, rappelée ici).

## 3. Personas — les règles de variation

Un persona est le renard canonique + UN axe de costume/accessoire + un set d'attitudes.
La silhouette reste reconnaissable au premier coup d'œil — on doit toujours voir
qu'au commandement de cette room, c'est Inari, décliné.

- Actés : original (l'Inari de référence), claudz/merica (américain), zen (oriental),
  ablitered (rebel), les deux militaires (sentinelles), l'artiste, et les personas
  providers (groq, gemini, mistral, nvidia, cohere, openrouter, cerebras, cloudflare).
- Chaque persona déclare : sa banque de séquences (au minimum parle / salue / respire /
  ennui), ses nano-séquences signature, sa voix (pack purrd), sa tuile.
- Un nouveau persona = une fiche dans le backlog personas + dérivation des deux
  sources canoniques. Pas de persona qui ne ressemble plus au renard.

## 4. Matrice d'usage

| Surface | Incarnation | Détail |
|---|---|---|
| Hero accueil site | Signature | + braises kitsunebi, ressorts sur les queues |
| favicon / OG / print | Signature | cuivre plein en petit |
| Icône APK / webapp | Signature | cuivre plein `#e07a2f` sur charbon |
| Mascotte APK / webapp | Compagnon | banque complète + interactions |
| Tuiles des rooms | Compagnon | persona de la room, état de travail |
| Campus | Compagnon | personas habitants des pages |
| Vidéos / teasers | Compagnon | séquences parle/salue, lip-sync |
| README dépôts | Signature | sobre, un seul exemplaire |

## 5. Mouvement — les principes

- Physique douce partout : ressorts (queues), dérive et scintillement (braises),
  transitions fondues. Jamais de saut de pose visible : toute séquence part du
  point zéro et y revient.
- Statique + nano-séquences : le Compagnon respire, il ne gigote pas. Les interactions
  (tap, chatouille, queue) déclenchent des séquences, puis retour au calme.
- `prefers-reduced-motion` : composition figée finie, jamais un squelette cassé.

## 5bis. Déclinaisons de style (le précédent Mario)

Mario, Sonic, les héros de Final Fantasy ne sont pas toujours en 3D ni dans leur forme
originelle — on les reconnaît pourtant, et on joue là-dessus. Pareil pour Inari :
pixel, encre, flat, chibi, peinture… TOUTE réinterprétation de style est légitime tant
que la signature reste lisible au premier coup d'œil : neuf queues, grandes oreilles,
cuivre sur charbon, œil en fente. Ce qui trahit Inari n'est jamais le style, c'est la
perte de la signature (une seule queue, un autre animal). Le style se joue, la signature
ne se négocie pas.

## 6. Anti-dérive (rappel opérationnel)

1. Nouvelle image d'Inari → dérivée des sources canoniques, charte citée dans la PR.
2. Nouvelle surface → elle pioche dans la matrice d'usage, elle n'invente pas une
   troisième incarnation.
3. Un doute en revue → on compare à la Signature et à la banque de référence,
   pas à un souvenir.
