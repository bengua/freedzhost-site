"""Build the static site of freedzhost.cloud into public/.

Every page is an HTML fragment in content/<lang>/<slug>.html whose first line is
a JSON comment: <!-- {"title": ..., "summary": ..., "order": N} -->. The same
slug in both languages is the same page; each page links to its translation.
Standard library only: the site must build on any machine with Python.
"""

import html
import json
import pathlib
import re
import shutil
import sys

import diagrams

ROOT = pathlib.Path(__file__).parent
SITE = "https://freedzhost.cloud"
LANGS = {
    "en": {"prefix": "", "name": "English", "home": "Home", "read": "Read",
           "articles": "Articles", "switch": "Français", "help": "Need help?",
           "levels": {"read": "Reading", "beginner": "Beginner", "intermediate": "Intermediate", "advanced": "Advanced"},
           "fiche": {"level": "Level", "time": "Estimated time", "before": "Read first", "words": "A word you don't know?",
                     "glossary": "Glossary"},
           "series": {"start": "Start here", "ai": "Local AI", "n8n": "Local agentic automation with n8n", "agents": "Your agent stack", "create": "Create with local AI", "desk": "Your Linux workstation", "homelab": "Homelab: replace the subscriptions"},
           "description": "Free tutorials to run your own AI agent swarm and homelab at home: hardware, local models, and the services that replace your subscriptions.",
           "locale": "en_US", "feed": "New articles",
           "footer":
           "Content under CC BY-SA 4.0. No trackers, no cookies, no third-party fonts."},
    "fr": {"prefix": "fr/", "name": "Français", "home": "Accueil", "read": "Lire",
           "articles": "Articles", "switch": "English", "help": "Besoin d'aide ?",
           "levels": {"read": "Lecture", "beginner": "Débutant", "intermediate": "Intermédiaire", "advanced": "Avancé"},
           "fiche": {"level": "Niveau", "time": "Temps estimé", "before": "À lire avant", "words": "Un mot inconnu ?",
                     "glossary": "Lexique"},
           "series": {"start": "Commencer ici", "ai": "IA locale", "n8n": "L'agentique locale avec n8n", "agents": "Votre pile d'agents", "create": "Créer avec l'IA locale", "desk": "Votre poste Linux", "homelab": "Homelab : remplacer les abonnements"},
           "description": "Tutos gratuits pour monter votre essaim d'agents IA et votre homelab à la maison : matériel, modèles locaux, et les services qui remplacent vos abonnements.",
           "locale": "fr_FR", "feed": "Nouveaux articles",
           "footer":
           "Contenu sous licence CC BY-SA 4.0. Ni traceur, ni cookie, ni police externe."},
}
OTHER = {"en": "fr", "fr": "en"}


def read_page(path):
    first, _, body = path.read_text(encoding="utf-8").partition("\n")
    if not (first.startswith("<!--") and first.endswith("-->")):
        raise ValueError(f"{path}: first line must be a JSON comment")
    meta = json.loads(first[4:-3])
    for key in ("title", "summary", "order"):
        if key not in meta:
            raise ValueError(f"{path}: missing {key!r}")
    return meta, body


def fiche(lang, meta, pages):
    """The card at the top of an article: level, time, what to read first, the glossary."""
    if "level" not in meta:
        return ""
    f = LANGS[lang]["fiche"]
    parts = [f'<span><b>{f["level"]}</b> {LANGS[lang]["levels"][meta["level"]]}</span>']
    if meta.get("time"):
        parts.append(f'<span><b>{f["time"]}</b> {html.escape(meta["time"])}</span>')
    before = [r for r in meta.get("requires", []) if r in pages]
    if before:
        links = ", ".join(f'<a href="{url(lang, r)}">{html.escape(pages[r][0]["title"])}</a>' for r in before)
        parts.append(f'<span><b>{f["before"]}</b> {links}</span>')
    parts.append(f'<span>{f["words"]} <a href="{url(lang, "glossary")}">{f["glossary"]}</a></span>')
    return f'<div class="fiche level-{meta["level"]}">' + "".join(parts) + "</div>\n"


def url(lang, slug):
    """Site-absolute URL of a page."""
    page = "" if slug == "index" else f"{slug}.html"
    return "/" + LANGS[lang]["prefix"] + page


def layout(lang, slug, title, body, description):
    t = LANGS[lang]
    other = OTHER[lang]
    here = SITE + url(lang, slug)
    desc = html.escape(description)
    full = html.escape(title) + " · freedzhost.cloud"
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{here}">
<link rel="alternate" hreflang="{lang}" href="{here}">
<link rel="alternate" hreflang="{other}" href="{SITE}{url(other, slug)}">
<link rel="alternate" hreflang="x-default" href="{SITE}{url("en", slug)}">
<link rel="alternate" type="application/rss+xml" title="{html.escape(t['feed'])}" href="/{t['prefix']}feed.xml">
<meta property="og:type" content="{'website' if slug == 'index' else 'article'}">
<meta property="og:title" content="{full}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{here}">
<meta property="og:image" content="{SITE}/media/teaser-poster.jpg">
<meta property="og:locale" content="{t['locale']}">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/style.css">
</head>
<body>
<header class="top">
  <a class="brand" href="{url(lang, 'index')}">freedzhost<span>.cloud</span></a>
  <nav><a href="{url(lang, 'index')}">{t['home']}</a>
  <a class="help" href="{url(lang, 'help')}">{t['help']}</a>
  <a class="lang" href="{url(other, slug)}" hreflang="{other}">{LANGS[other]['name']}</a></nav>
</header>
<main>
{body}
</main>
<footer>{t['footer']}</footer>
</body>
</html>
"""


def write_feeds_and_sitemap(out, catalogue):
    """sitemap.xml with language alternates, one RSS feed per language, robots.txt."""
    urls = []
    for slug in sorted(catalogue["en"]):
        for lang in LANGS:
            alts = "".join(
                f'<xhtml:link rel="alternate" hreflang="{other}" href="{SITE}{url(other, slug)}"/>'
                for other in LANGS
            )
            urls.append(f"<url><loc>{SITE}{url(lang, slug)}</loc>{alts}</url>")
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(urls) + "\n</urlset>\n",
        encoding="utf-8")
    for lang, pages in catalogue.items():
        t = LANGS[lang]
        newest = sorted((s for s in pages if s != "index" and not pages[s].get("nav")), key=lambda s: -pages[s]["order"])
        items = "".join(
            f"<item><title>{html.escape(pages[s]['title'])}</title>"
            f"<link>{SITE}{url(lang, s)}</link><guid>{SITE}{url(lang, s)}</guid>"
            f"<description>{html.escape(pages[s]['summary'])}</description></item>"
            for s in newest
        )
        (out / t["prefix"] / "feed.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
            f"<title>freedzhost.cloud · {html.escape(t['feed'])}</title><link>{SITE}{url(lang, 'index')}</link>"
            f"<description>{html.escape(t['description'])}</description><language>{lang}</language>"
            f"{items}</channel></rss>\n",
            encoding="utf-8")
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")


def build(out):
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(ROOT / "static", out)
    slugs = {}
    catalogue = {}
    for lang in LANGS:
        pages = {p.stem: read_page(p) for p in sorted((ROOT / "content" / lang).glob("*.html"))}
        slugs[lang] = set(pages)
        catalogue[lang] = {slug: meta for slug, (meta, _) in pages.items()}
        articles = sorted((s for s in pages if s != "index" and not pages[s][0].get("nav")), key=lambda s: pages[s][0]["order"])
        groups = []
        for key, heading in LANGS[lang]["series"].items():
            members = [a for a in articles if pages[a][0].get("series") == key]
            if not members:
                continue
            items = "\n".join(
                f'<li><a href="{url(lang, a)}"><strong>{html.escape(pages[a][0]["title"])}</strong>'
                f'<span>{html.escape(pages[a][0]["summary"])}</span></a></li>'
                for a in members
            )
            groups.append(f'<h3 class="series">{html.escape(heading)}</h3>\n<ul class="cards">\n{items}\n</ul>')
        orphans = [a for a in articles if pages[a][0].get("series") not in LANGS[lang]["series"]]
        if orphans:
            raise ValueError(f"{lang}: pages without a known series: {orphans}")
        cards = "\n".join(groups)
        for slug, (meta, body) in pages.items():
            body = re.sub(r"\{\{diagram:([a-z0-9]+)\}\}", lambda m, lang=lang: diagrams.render(m.group(1), lang), body)
            if slug == "index":
                body = body.replace("{{articles}}", cards)
            elif not meta.get("nav"):  # a nav page brings its own layout
                body = f'<article>\n<h1>{html.escape(meta["title"])}</h1>\n{fiche(lang, meta, pages)}{body}</article>'
            target = out / LANGS[lang]["prefix"] / ("index.html" if slug == "index" else f"{slug}.html")
            target.parent.mkdir(parents=True, exist_ok=True)
            description = LANGS[lang]["description"] if slug == "index" else meta["summary"]
            target.write_text(layout(lang, slug, meta["title"], body, description), encoding="utf-8")
    if slugs["en"] != slugs["fr"]:
        raise ValueError(f"pages without translation: {sorted(slugs['en'] ^ slugs['fr'])}")
    write_feeds_and_sitemap(out, catalogue)
    return out


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    out = build(pathlib.Path(argv[0]) if argv else ROOT / "public")
    print(f"built {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
