"""Build the static site of freedzhost.cloud into public/.

Every page is an HTML fragment in content/<lang>/<slug>.html whose first line is
a JSON comment: <!-- {"title": ..., "summary": ..., "order": N} -->. The same
slug in both languages is the same page; each page links to its translation.
Standard library only: the site must build on any machine with Python.
"""

import datetime
import html
import json
import pathlib
import re
import shutil
import sys

import diagrams

ROOT = pathlib.Path(__file__).parent
SITE = "https://freedzhost.cloud"
REVUE_DIR = ROOT / "content" / "revue"
TODAY = datetime.datetime.now(datetime.timezone.utc).date()
LANGS = {
    "en": {"prefix": "", "name": "English", "home": "Home", "read": "Read",
           "articles": "Articles", "switch": "Français", "help": "Need help?", "support": "Support",
           "banner": ("This tutorial helped you? It is free, with no ads and no trackers, thanks to people like you.", "Support the project"),
           "menu": "Menu", "close": "Close", "prev": "Previous", "next": "Next", "drawer": "Navigation",
           "quick": {"index": "Home", "support": "Support the project", "findings": "Our findings", "workshop": "The workshop", "faq": "FAQ", "inspirations": "Inspirations", "help": "Need help?"},
           "levels": {"read": "Reading", "beginner": "Beginner", "intermediate": "Intermediate", "advanced": "Advanced"},
           "fiche": {"level": "Level", "time": "Estimated time", "before": "Read first", "words": "A word you don't know?",
                     "glossary": "Glossary"},
           "series": {"start": "Start here", "ai": "Local AI", "n8n": "Local agentic automation with n8n", "agents": "Your agent stack", "create": "Create with local AI", "desk": "Your Linux workstation", "homelab": "Homelab: replace the subscriptions"},
           "description": "Free tutorials to run your own AI agent swarm and homelab at home: hardware, local models, and the services that replace your subscriptions.",
           "locale": "en_US", "feed": "New articles",
           "revue_title": "Today's briefing", "revue_empty": "The briefing is on its way — the swarm is preparing it.",
           "revue_source": "source", "revue_archive": "All news", "badge_new": "new",
           "tutos": "Tutorials",
           "path_tutos": ("Tutorials", "Free step-by-step guides: hardware, local AI, agents, homelab."),
           "path_training": ("Training", "Go further with a structured course and a community of members."),
           "path_open": "Open", "all_series": "All series", "series_count": "articles",
           "search_label": "Search the tutorials", "search_placeholder": "Search by keyword…",
           "search_none": "No result.",
           "news": "News", "training": "Training", "hardware_label": "Hardware", "favorites": "Favorites",
           "members": "Members", "soon": "soon",
           "footer":
           "Content under CC BY-SA 4.0. No trackers, no cookies, no third-party fonts."},
    "fr": {"prefix": "fr/", "name": "Français", "home": "Accueil", "read": "Lire",
           "articles": "Articles", "switch": "English", "help": "Besoin d'aide ?", "support": "Soutenir",
           "banner": ("Ce tuto vous a aidé ? Il est gratuit, sans pub ni traceur, grâce à des gens comme vous.", "Soutenir le projet"),
           "menu": "Menu", "close": "Fermer", "prev": "Précédent", "next": "Suivant", "drawer": "Navigation",
           "quick": {"index": "Accueil", "support": "Soutenir le projet", "findings": "Nos constats", "workshop": "L'atelier", "faq": "FAQ", "inspirations": "Inspirations", "help": "Besoin d'aide ?"},
           "levels": {"read": "Lecture", "beginner": "Débutant", "intermediate": "Intermédiaire", "advanced": "Avancé"},
           "fiche": {"level": "Niveau", "time": "Temps estimé", "before": "À lire avant", "words": "Un mot inconnu ?",
                     "glossary": "Lexique"},
           "series": {"start": "Commencer ici", "ai": "IA locale", "n8n": "L'agentique locale avec n8n", "agents": "Votre pile d'agents", "create": "Créer avec l'IA locale", "desk": "Votre poste Linux", "homelab": "Homelab : remplacer les abonnements"},
           "description": "Tutos gratuits pour monter votre essaim d'agents IA et votre homelab à la maison : matériel, modèles locaux, et les services qui remplacent vos abonnements.",
           "locale": "fr_FR", "feed": "Nouveaux articles",
           "revue_title": "La revue du jour", "revue_empty": "La revue arrive — le swarm la prépare.",
           "revue_source": "source", "revue_archive": "Toutes les actualités", "badge_new": "nouveau",
           "tutos": "Tutos",
           "path_tutos": ("Tutos", "Des guides gratuits pas à pas : matériel, IA locale, agents, homelab."),
           "path_training": ("Formation", "Allez plus loin avec un parcours structuré et une communauté de membres."),
           "path_open": "Ouvrir", "all_series": "Toutes les séries", "series_count": "articles",
           "search_label": "Rechercher dans les tutos", "search_placeholder": "Rechercher par mot-clé…",
           "search_none": "Aucun résultat.",
           "news": "Actualités", "training": "Formation", "hardware_label": "Matériel", "favorites": "Coups de cœur",
           "members": "Membres", "soon": "bientôt",
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


def read_revue(path):
    first, _, _ = path.read_text(encoding="utf-8").partition("\n")
    if not (first.startswith("<!--") and first.endswith("-->")):
        raise ValueError(f"{path}: first line must be a JSON comment")
    meta = json.loads(first[4:-3])
    for key in ("date", "items"):
        if key not in meta:
            raise ValueError(f"{path}: missing {key!r}")
    return meta


def load_revue():
    if not REVUE_DIR.exists():
        return []
    revues = [read_revue(p) for p in sorted(REVUE_DIR.glob("*.md"))]
    revues.sort(key=lambda m: m["date"], reverse=True)
    return revues


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


FOXES = {"start", "ai", "n8n", "agents", "create", "desk", "homelab"}


def fox(series, size, cls="fox"):
    """FoxBot, the mascot, in the pose of a series: decorative, so an empty alt."""
    if series not in FOXES:
        return ""
    return (f'<img class="{cls}" src="/media/fox/{series}.webp" alt="" width="{size}" height="{size}" '
            f'loading="lazy" decoding="async">')



def banner(lang, slug):
    """A quiet donation banner at the end of each tutorial (not on the support page itself)."""
    if slug == "support":
        return ""
    text, action = LANGS[lang]["banner"]
    return (f'<aside class="give-banner"><p>{html.escape(text)}</p>'
            f'<a class="give" href="{url(lang, "support")}">{html.escape(action)}</a></aside>\n')


MATERIEL_SLUGS = {
    "hardware", "gpu-for-ai", "gpu-grid", "second-gpu-oculink", "big-moe-two-cards",
    "kvmem-long-context", "kv-cache-trap", "speculative-decoding", "pcie-link-width",
    "ram-zram-swap", "strata-flash-next", "model-bench",
}


def revue_item_html(lang, item):
    source = item.get("source", "")
    source_html = f'<span class="source">{html.escape(source)}</span>' if source else ""
    return (f'<li class="revue-item">'
            f'<a class="title" href="{html.escape(item["url"])}">{html.escape(item["title"])}</a>'
            f'{source_html}'
            f'<p>{html.escape(item.get("resume", ""))}</p>'
            f'</li>')


def revue_section_html(lang, revue):
    t = LANGS[lang]
    if not revue:
        return f'<section class="revue"><h2>{html.escape(t["revue_title"])}</h2><p class="empty">{html.escape(t["revue_empty"])}</p></section>'
    date = revue["date"]
    items = "".join(revue_item_html(lang, it) for it in revue["items"])
    return (f'<section class="revue">'
            f'<header><h2>{html.escape(t["revue_title"])}</h2><time datetime="{html.escape(date)}">{html.escape(date)}</time></header>'
            f'<ul class="revue-items">{items}</ul>'
            f'<p class="more"><a href="{url(lang, "actualites")}">{html.escape(t["revue_archive"])} →</a></p>'
            f'</section>')


def revue_archive_html(lang, revues):
    t = LANGS[lang]
    if not revues:
        return f'<p class="empty">{html.escape(t["revue_empty"])}</p>'
    parts = []
    for revue in revues:
        date = revue["date"]
        items = "".join(revue_item_html(lang, it) for it in revue["items"])
        parts.append(f'<section class="revue-archive-day"><h3><time datetime="{html.escape(date)}">{html.escape(date)}</time></h3>'
                     f'<ul class="revue-items">{items}</ul></section>')
    return "\n".join(parts)


def materiel_list_html(lang, pages):
    slugs = sorted((s for s in pages if s in MATERIEL_SLUGS), key=lambda s: pages[s][0]["order"])
    items = "".join(
        f'<li><a href="{url(lang, s)}"><strong>{html.escape(pages[s][0]["title"])}</strong>'
        f'<span>{html.escape(pages[s][0]["summary"])}</span></a></li>'
        for s in slugs)
    return f'<ul class="cards materiel-cards">\n{items}\n</ul>'


def coups_de_coeur_html(lang, meta):
    links = meta.get("links", [])
    items = "".join(
        f'<li><a href="{html.escape(lk["url"])}"><strong>{html.escape(lk["title"])}</strong>'
        f'<span>{html.escape(lk.get("source", ""))}</span>'
        f'<p>{html.escape(lk.get("description", ""))}</p></a></li>'
        for lk in links)
    return f'<ul class="cards favorite-cards">\n{items}\n</ul>'


def search_form(lang, where):
    """Keyword search box; works with search.js, inert (but harmless) without."""
    t = LANGS[lang]
    return (f'<form class="search" role="search" action="{url(lang, "tutos")}" '
            f'data-index="/{t["prefix"]}search-index.json" data-none="{html.escape(t["search_none"])}">'
            f'<label for="q-{where}">{html.escape(t["search_label"])}</label>'
            f'<input type="search" id="q-{where}" name="q" autocomplete="off" '
            f'placeholder="{html.escape(t["search_placeholder"])}">'
            f'<ul class="results" hidden></ul></form>')


def paths_html(lang):
    """The two entry paths of the site: tutorials and training."""
    t = LANGS[lang]
    items = "\n".join(
        f'<li><a href="{url(lang, slug)}"><strong>{html.escape(t[key][0])}</strong>'
        f'<span>{html.escape(t[key][1])}</span><em>{html.escape(t["path_open"])} →</em></a></li>'
        for key, slug in (("path_tutos", "tutos"), ("path_training", "formation")))
    return f'<ul class="cards paths">\n{items}\n</ul>'


def series_cards_html(lang, series_members):
    """One card per series, linking to its section of the tutorials page."""
    t = LANGS[lang]
    items = "\n".join(
        f'<li><a href="{url(lang, "tutos")}#series-{html.escape(key)}">{fox(key, 56)}'
        f'<strong>{html.escape(heading)}</strong>'
        f'<span>{len(series_members[key])} {html.escape(t["series_count"])}</span></a></li>'
        for key, heading in t["series"].items() if series_members.get(key))
    return f'<ul class="cards series-cards">\n{items}\n</ul>'


def search_index(lang, pages, articles):
    """Flat keyword index of every article, for search.js."""
    t = LANGS[lang]
    return json.dumps([
        {"slug": a, "url": url(lang, a), "title": pages[a][0]["title"], "summary": pages[a][0]["summary"],
         "series": t["series"].get(pages[a][0].get("series"), "")}
        for a in articles], ensure_ascii=False)


QUICK = ("index", "support", "findings", "workshop", "faq", "inspirations", "help")
CURRENT = ' aria-current="page"'


def drawer(lang, slug, pages, series_members, revue_date=None):
    """The side drawer: brand, news, tutorials, new pages, and utility links."""
    t = LANGS[lang]
    is_new = revue_date == TODAY.isoformat()
    badge = f'<span class="badge">{html.escape(t["badge_new"])}</span>' if is_new else ""
    series_links = "".join(
        f'<li><a href="{url(lang, "tutos")}#series-{html.escape(key)}">{html.escape(heading)}</a></li>'
        for key, heading in t["series"].items())
    return (f'<nav id="menu" class="drawer" aria-label="{html.escape(t["drawer"])}">'
            f'<a class="close" href="#">{t["close"]} ✕</a>'
            f'<a class="brand" href="{url(lang, "index")}">freedzhost<span>.cloud</span></a>'
            f'{search_form(lang, "drawer")}'
            f'<div class="tree">'
            f'<a href="{url(lang, "actualites")}"{CURRENT if slug == "actualites" else ""}>'
            f'{html.escape(t["news"])}{badge}</a>'
            f'<a href="{url(lang, "tutos")}"{CURRENT if slug == "tutos" else ""}>{html.escape(t["tutos"])}</a>'
            f'<details><summary>{html.escape(t["all_series"])}</summary><ul>{series_links}</ul></details>'
            f'<a href="{url(lang, "formation")}"{CURRENT if slug == "formation" else ""}>{html.escape(t["training"])}</a>'
            f'<a href="{url(lang, "formation")}#membres"{CURRENT if slug == "formation" else ""}>{html.escape(t["members"])}<span class="badge-soon">{html.escape(t["soon"])}</span></a>'
            f'<a href="{url(lang, "materiel")}"{CURRENT if slug == "materiel" else ""}>{html.escape(t["hardware_label"])}</a>'
            f'<a href="{url(lang, "coups-de-coeur")}"{CURRENT if slug == "coups-de-coeur" else ""}>{html.escape(t["favorites"])}</a>'
            f'</div>'
            f'<div class="bottom">'
            f'<a class="lang" href="{url(OTHER[lang], slug)}" hreflang="{OTHER[lang]}">{LANGS[OTHER[lang]]["name"]}</a>'
            f'<a href="{url(lang, "support")}">{html.escape(t["support"])}</a>'
            f'<a href="{url(lang, "faq")}">{html.escape(t["quick"]["faq"])}</a>'
            f'</div>'
            f'</nav>')


def pager(lang, slug, pages, members):
    """Previous and next article within the same series."""
    if slug not in members:
        return ""
    i = members.index(slug)
    t = LANGS[lang]
    links = []
    if i > 0:
        links.append(f'<a class="prev" href="{url(lang, members[i - 1])}"><small>← {t["prev"]}</small>'
                     f'{html.escape(pages[members[i - 1]][0]["title"])}</a>')
    if i + 1 < len(members):
        links.append(f'<a class="next" href="{url(lang, members[i + 1])}"><small>{t["next"]} →</small>'
                     f'{html.escape(pages[members[i + 1]][0]["title"])}</a>')
    return f'<nav class="pager">{"".join(links)}</nav>\n' if links else ""


def url(lang, slug):
    """Site-absolute URL of a page."""
    page = "" if slug == "index" else f"{slug}.html"
    return "/" + LANGS[lang]["prefix"] + page


def layout(lang, slug, title, body, description, side=""):
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
<link rel="icon" type="image/png" href="/media/inari-icon.png">
<link rel="apple-touch-icon" href="/media/inari-icon-180.png">
<link rel="stylesheet" href="/style.css">
<script defer src="https://analytics.freedzhost.cloud/script.js" data-website-id="23badf50-b8d2-4487-b2ae-f67ab9fd172d"></script>
</head>
<body>
<header class="top">
  <a class="brand" href="{url(lang, 'index')}">freedzhost<span>.cloud</span></a>
  <nav><a class="menu-btn" href="#menu">☰ {t['menu']}</a>
  <a class="lang" href="{url(other, slug)}" hreflang="{other}">{LANGS[other]['name']}</a></nav>
</header>
{side}
<main>
{body}
</main>
<footer><video class="mascot" src="/media/foxbot-coucou.mp4" autoplay loop muted playsinline aria-hidden="true"></video>
<p>{t['footer']}</p></footer>
<script defer src="/search.js"></script>
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
    revues = load_revue()
    latest_revue = revues[0] if revues else None
    latest_revue_date = latest_revue["date"] if latest_revue else None
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
            groups.append(f'<h3 class="series" id="series-{html.escape(key)}">{fox(key, 56)}{html.escape(heading)}</h3>\n<ul class="cards">\n{items}\n</ul>')
        orphans = [a for a in articles if "series" in pages[a][0] and pages[a][0]["series"] not in LANGS[lang]["series"]]
        if orphans:
            raise ValueError(f"{lang}: pages without a known series: {orphans}")
        cards = "\n".join(groups)
        (out / LANGS[lang]["prefix"]).mkdir(parents=True, exist_ok=True)
        (out / LANGS[lang]["prefix"] / "search-index.json").write_text(search_index(lang, pages, articles), encoding="utf-8")
        series_members = {key: [a for a in articles if pages[a][0].get("series") == key] for key in LANGS[lang]["series"]}
        for slug, (meta, body) in pages.items():
            body = re.sub(r"\{\{diagram:([a-z0-9]+)\}\}", lambda m, lang=lang: diagrams.render(m.group(1), lang), body)
            body = body.replace("{{revue}}", revue_section_html(lang, latest_revue))
            body = body.replace("{{revue-archive}}", revue_archive_html(lang, revues))
            body = body.replace("{{materiel-list}}", materiel_list_html(lang, pages))
            body = body.replace("{{coups-de-coeur}}", coups_de_coeur_html(lang, meta))
            body = body.replace("{{paths}}", paths_html(lang))
            body = body.replace("{{series-cards}}", series_cards_html(lang, series_members))
            body = body.replace("{{search}}", search_form(lang, "page"))
            body = body.replace("{{articles}}", cards)
            if slug != "index" and not meta.get("nav"):  # a nav page brings its own layout
                members = series_members.get(meta.get("series"), [])
                body = (f'<article>\n{fox(meta.get("series", ""), 88, "guide")}<h1>{html.escape(meta["title"])}</h1>\n{fiche(lang, meta, pages)}{body}'
                        f'{banner(lang, slug)}{pager(lang, slug, pages, members)}</article>')
            target = out / LANGS[lang]["prefix"] / ("index.html" if slug == "index" else f"{slug}.html")
            target.parent.mkdir(parents=True, exist_ok=True)
            description = LANGS[lang]["description"] if slug == "index" else meta["summary"]
            target.write_text(layout(lang, slug, meta["title"], body, description, drawer(lang, slug, pages, series_members, latest_revue_date)),
                              encoding="utf-8")
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
