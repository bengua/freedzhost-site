# freedzhost-site

Le site [freedzhost.cloud](https://freedzhost.cloud) : un générateur statique en Python pur et plus d'une centaine de tutoriels sur la souveraineté numérique, l'IA locale et le homelab, en français et en anglais.

[![Licence contenu : CC BY-SA 4.0](https://img.shields.io/badge/contenu-CC%20BY--SA%204.0-lightgrey.svg)](LICENSE)
[![Licence code : MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE-CODE)
[![CI](https://github.com/OWNERTEST/freedzhost-site/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNERTEST/freedzhost-site/actions/workflows/ci.yml)

## Présentation

Ce dépôt contient tout ce qui produit freedzhost.cloud : les articles (fragments HTML dans `content/en` et `content/fr`), les médias (`static/`), et un générateur de quelques centaines de lignes qui assemble le tout en un dossier `public/` de pages statiques. Aucun framework, aucune dépendance, aucun JavaScript côté serveur : un `python3 site_build.py` et c'est en ligne.

## Fonctionnalités

- **Bilingue par construction** : l'anglais à la racine, le français sous `/fr/` ; une traduction manquante arrête le build.
- **Tutoriels pas à pas** : carte graphique et pilotes NVIDIA, Docker avec GPU, premier modèle local, Proxmox, forge de code et CI auto-hébergées, agents de code locaux, sauvegardes, poste de travail Linux…
- **Schémas générés** : `diagrams.py` dessine les diagrammes SVG des articles, avec leurs libellés dans les deux langues.
- **Tout ce qu'un site sérieux attend** : plan du site (`sitemap.xml`), flux RSS par langue, liens canoniques, balises `hreflang`.
- **Tests qui protègent le public** : liens internes vérifiés, langues complètes, et refus de toute adresse privée, nom de tailnet ou répertoire personnel dans le site produit.

## Installation depuis zéro

Prérequis : Python 3.10 ou plus récent. Rien d'autre pour construire le site.

```sh
git clone https://github.com/OWNERTEST/freedzhost-site
cd freedzhost-site
python3 site_build.py            # écrit le site dans public/
```

Pour lancer les tests et le linter :

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
python3 -m pytest
ruff check .
```

## Utilisation

Prévisualiser en local :

```sh
python3 site_build.py
python3 -m http.server -d public    # puis http://localhost:8000
```

Ajouter une page : créez `content/en/<slug>.html` **et** `content/fr/<slug>.html`, dont la première ligne est l'en-tête JSON :

```html
<!-- {"title": "…", "summary": "…", "order": 6} -->
```

L'accueil liste les articles selon `order`. Les médias vont dans `static/media/`. Le build copie `static/`, enveloppe chaque fragment dans la mise en page et produit plan du site et flux.

### Déployer

Le résultat est un simple dossier de fichiers statiques : il se publie sur n'importe quel hébergeur statique.

1. `python3 site_build.py` (ou `freedzhost-site-build` une fois le paquet installé) produit `public/`.
2. Copiez le contenu de `public/` vers votre hébergeur : un serveur web quelconque (nginx, Caddy, Apache) via `rsync -a --delete public/ user@serveur:/var/www/site/`, ou GitHub Pages, Codeberg Pages, Netlify, Cloudflare Pages… en indiquant `python3 site_build.py` comme commande de build et `public` comme dossier publié.

## Configuration

Il n'y a pas de variable d'environnement. Deux réglages seulement :

- **Dossier de sortie** : argument optionnel, `python3 site_build.py /chemin/vers/sortie` (par défaut `public/`).
- **Adresse du site** : la constante `SITE` en tête de `site_build.py` (`https://freedzhost.cloud`), utilisée pour les liens canoniques, le plan du site et les flux. Changez-la si vous publiez une copie ailleurs.

## Limites

- Les tutoriels ont été vérifiés contre la documentation officielle et une installation réelle, pas encore rejoués sur une machine vierge.
- Le teaser vidéo n'existe qu'en français.
- Le site est statique : pas de recherche, pas de commentaires, pas de mesure d'audience, et c'est voulu.

## Pourquoi ce projet

Parce qu'on comprend mieux son ordinateur quand on le reprend en main, et qu'une IA qui tourne chez soi ne revend rien à personne.
Chaque tutoriel est né d'une vraie panne ou d'une vraie installation, écrit pour qu'un débutant curieux arrive au bout.
Et le site lui-même prêche par l'exemple : quelques centaines de lignes de Python, zéro dépendance, hébergeable partout.

## Licence

Double licence :

- **Contenu** (`content/`, `static/` : textes, images, vidéos) : [CC BY-SA 4.0](LICENSE). Vous pouvez reprendre et adapter les tutoriels en citant la source et en partageant dans les mêmes conditions.
- **Code** (`site_build.py`, `diagrams.py`, `tests/`) : [MIT](LICENSE-CODE). Réutilisez le générateur librement, y compris pour un tout autre site.

## English

**freedzhost-site** is the source of [freedzhost.cloud](https://freedzhost.cloud): a dependency-free Python static site generator and 100+ tutorials on digital sovereignty, local AI and homelabs, in English and French.

- **Build**: `python3 site_build.py` (Python 3.10+, standard library only) writes the site to `public/`; preview with `python3 -m http.server -d public`.
- **Add a page**: create `content/en/<slug>.html` and `content/fr/<slug>.html`, first line `<!-- {"title": "…", "summary": "…", "order": 6} -->`. A missing translation stops the build.
- **Test**: `pip install -e '.[dev]'`, then `python3 -m pytest` and `ruff check .`. The tests check links, both languages, sitemap, feeds, and that no private address or home directory leaks into the output.
- **Configure**: no environment variables; optional output directory as first argument, and the `SITE` constant in `site_build.py` for canonical URLs.
- **Deploy**: copy `public/` to any static host (nginx, Caddy, GitHub Pages, Codeberg Pages, Netlify, Cloudflare Pages…), with `python3 site_build.py` as build command and `public` as output directory.
- **License**: content (`content/`, `static/`) under [CC BY-SA 4.0](LICENSE); generator code (`site_build.py`, `diagrams.py`, `tests/`) under [MIT](LICENSE-CODE).

---

Un projet [FreedzHost](https://freedzhost.cloud) — souveraineté numérique, IA locale, homelab.
A [FreedzHost](https://freedzhost.cloud) project.
