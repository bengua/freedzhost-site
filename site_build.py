"""Build the static site of freedzhost.cloud into public/.

Every page is an HTML fragment in content/<lang>/<slug>.html whose first line is
a JSON comment: <!-- {"title": ..., "summary": ..., "order": N} -->. The same
slug in both languages is the same page; each page links to its translation.
Standard library only: the site must build on any machine with Python.
"""

import html
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).parent
LANGS = {
    "en": {"prefix": "", "name": "English", "home": "Home", "read": "Read",
           "articles": "Articles", "switch": "Français", "footer":
           "Content under CC BY-SA 4.0. No trackers, no cookies, no third-party fonts."},
    "fr": {"prefix": "fr/", "name": "Français", "home": "Accueil", "read": "Lire",
           "articles": "Articles", "switch": "English", "footer":
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


def url(lang, slug):
    """Site-absolute URL of a page."""
    page = "" if slug == "index" else f"{slug}.html"
    return "/" + LANGS[lang]["prefix"] + page


def layout(lang, slug, title, body):
    t = LANGS[lang]
    other = OTHER[lang]
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · freedzhost.cloud</title>
<link rel="stylesheet" href="/style.css">
<link rel="alternate" hreflang="{other}" href="{url(other, slug)}">
</head>
<body>
<header class="top">
  <a class="brand" href="{url(lang, 'index')}">freedzhost<span>.cloud</span></a>
  <nav><a href="{url(lang, 'index')}">{t['home']}</a>
  <a class="lang" href="{url(other, slug)}" hreflang="{other}">{LANGS[other]['name']}</a></nav>
</header>
<main>
{body}
</main>
<footer>{t['footer']}</footer>
</body>
</html>
"""


def build(out):
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(ROOT / "static", out)
    slugs = {}
    for lang in LANGS:
        pages = {p.stem: read_page(p) for p in sorted((ROOT / "content" / lang).glob("*.html"))}
        slugs[lang] = set(pages)
        articles = sorted((s for s in pages if s != "index"), key=lambda s: pages[s][0]["order"])
        cards = "\n".join(
            f'<li><a href="{url(lang, s)}"><strong>{html.escape(pages[s][0]["title"])}</strong>'
            f'<span>{html.escape(pages[s][0]["summary"])}</span></a></li>'
            for s in articles
        )
        for slug, (meta, body) in pages.items():
            if slug == "index":
                body = body.replace("{{articles}}", f'<ul class="cards">\n{cards}\n</ul>')
            else:
                body = f'<article>\n<h1>{html.escape(meta["title"])}</h1>\n{body}</article>'
            target = out / LANGS[lang]["prefix"] / ("index.html" if slug == "index" else f"{slug}.html")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(layout(lang, slug, meta["title"], body), encoding="utf-8")
    if slugs["en"] != slugs["fr"]:
        raise ValueError(f"pages without translation: {sorted(slugs['en'] ^ slugs['fr'])}")
    return out


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    out = build(pathlib.Path(argv[0]) if argv else ROOT / "public")
    print(f"built {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
