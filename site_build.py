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
import subprocess
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
                     "glossary": "Glossary", "reviewed": "Last reviewed:", "tested": "Tested with:"},
           "about": "About", "learning_paths": "Learning paths", "progress": "done", "step": "Step",
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
           "foot_fox": "Found this useful? Tell us what to measure next.",
           "hero_kicker": "Tutorials · Homelab · Local AI",
           "hero_tag": "Your own swarm of AI agents, at home.",
           "hero_down": "Skip to the content",
           "footer":
           "Content under CC BY-SA 4.0. No trackers, no cookies, no third-party fonts."},
    "fr": {"prefix": "fr/", "name": "Français", "home": "Accueil", "read": "Lire",
           "articles": "Articles", "switch": "English", "help": "Besoin d'aide ?", "support": "Soutenir",
           "banner": ("Ce tuto vous a aidé ? Il est gratuit, sans pub ni traceur, grâce à des gens comme vous.", "Soutenir le projet"),
           "menu": "Menu", "close": "Fermer", "prev": "Précédent", "next": "Suivant", "drawer": "Navigation",
           "quick": {"index": "Accueil", "support": "Soutenir le projet", "findings": "Nos constats", "workshop": "L'atelier", "faq": "FAQ", "inspirations": "Inspirations", "help": "Besoin d'aide ?"},
           "levels": {"read": "Lecture", "beginner": "Débutant", "intermediate": "Intermédiaire", "advanced": "Avancé"},
           "fiche": {"level": "Niveau", "time": "Temps estimé", "before": "À lire avant", "words": "Un mot inconnu ?",
                     "glossary": "Lexique", "reviewed": "Dernière révision :", "tested": "Testé avec :"},
           "about": "À propos", "learning_paths": "Parcours", "progress": "faites", "step": "Étape",
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
           "foot_fox": "Utile ? Dites-nous ce qu'il faut mesurer ensuite.",
           "hero_kicker": "Tutos · Homelab · IA locale",
           "hero_tag": "Votre essaim d'agents IA, à la maison.",
           "hero_down": "Aller au contenu",
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
    proof = revision_html(lang, meta)
    parts = [f'<span><b>{f["level"]}</b> {LANGS[lang]["levels"][meta["level"]]}</span>']
    if meta.get("time"):
        parts.append(f'<span><b>{f["time"]}</b> {html.escape(meta["time"])}</span>')
    before = [r for r in meta.get("requires", []) if r in pages]
    if before:
        links = ", ".join(f'<a href="{url(lang, r)}">{html.escape(pages[r][0]["title"])}</a>' for r in before)
        parts.append(f'<span><b>{f["before"]}</b> {links}</span>')
    parts.append(f'<span>{f["words"]} <a href="{url(lang, "glossary")}">{f["glossary"]}</a></span>')
    return f'<div class="fiche level-{meta["level"]}">' + "".join(parts) + "</div>\n" + proof


def revision_html(lang, meta):
    """Freshness of an article: when it was last reviewed and what it was tested with."""
    f = LANGS[lang]["fiche"]
    parts = []
    if meta.get("modified"):
        parts.append(f'<span>{f["reviewed"]} <time datetime="{html.escape(meta["modified"])}">{html.escape(meta["modified"])}</time></span>')
    if meta.get("tested"):
        parts.append(f'<span>{f["tested"]} {html.escape(meta["tested"])}</span>')
    return f'<p class="proof revision">{" · ".join(parts)}</p>\n' if parts else ""


PROFICIENCY = {"beginner": "Beginner", "intermediate": "Intermediate", "advanced": "Expert"}


def iso_duration(text):
    """ISO 8601 duration from the human "time" field; None when the text is fuzzy."""
    if not text:
        return None
    m = re.fullmatch(r"(\d+)(?:[–-](\d+))?\s*h(?:\s*(\d+))?(?:\s*\+.*)?", text.strip())
    if m:
        hours = int(m.group(2) or m.group(1))  # a range counts by its upper bound
        minutes = int(m.group(3) or 0)
        return f"PT{hours}H" + (f"{minutes}M" if minutes else "")
    m = re.fullmatch(r"(\d+)\s*min(?:\s*\+.*)?", text.strip())
    return f"PT{m.group(1)}M" if m else None


def git_file_dates():
    """For each content file, its (last, first) commit dates in ISO 8601.

    One `git log` pass, newest commit first: the first time a file appears is
    its last modification, and every later appearance pushes its publication
    date back. Empty when git cannot answer (a build outside a checkout)."""
    try:
        log = subprocess.run(["git", "log", "--format=%cI", "--name-only", "--", "content"],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return {}
    dates = {}
    current = None
    for line in log.splitlines():
        if re.match(r"\d{4}-\d{2}-\d{2}T", line):
            current = line
        elif line.strip() and current:
            modified, _ = dates.get(line, (current, current))
            dates[line] = (modified, current)
    return dates


def jsonld_script(data):
    """A JSON-LD block; '<' is escaped so the data can never close the script tag."""
    text = json.dumps(data, ensure_ascii=False, indent=1).replace("<", "\\u003c")
    return f'<script type="application/ld+json">\n{text}\n</script>'


NON_ARTICLE_TYPES = {"about": "AboutPage", "actualites": "CollectionPage"}
ORGANIZATION = {"@type": "Organization", "name": "FreedzHost", "url": "https://freedzhost.cloud"}


def article_jsonld(lang, slug, meta, dates):
    """Structured data for a page; None for pages that are not content pages."""
    if "level" not in meta:
        return None
    kind = NON_ARTICLE_TYPES.get(slug, "TechArticle")
    data = {"@context": "https://schema.org", "@type": kind, "headline": meta["title"],
            "description": meta["summary"], "inLanguage": lang, "url": SITE + url(lang, slug),
            "author": ORGANIZATION, "publisher": ORGANIZATION}
    git_modified, git_published = dates.get(f"content/{lang}/{slug}.html", (None, None))
    if git_published:
        data["datePublished"] = git_published
    modified = git_modified or meta.get("modified") or meta.get("date")
    if modified:
        data["dateModified"] = modified
    if kind == "TechArticle" and meta["level"] in PROFICIENCY:
        data["proficiencyLevel"] = PROFICIENCY[meta["level"]]
    duration = meta.get("duration") or iso_duration(meta.get("time"))
    if duration:
        data["timeRequired"] = duration
    return data


def site_jsonld(lang):
    """Organization and WebSite (with a search action) for the home pages."""
    search = SITE + url(lang, "tutos") + "?q={search_term_string}"
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "name": "FreedzHost", "url": "https://freedzhost.cloud",
         "logo": SITE + "/media/inari-icon.png"},
        {"@type": "WebSite", "name": "FreedzHost", "url": SITE + url(lang, "index"), "inLanguage": lang,
         "potentialAction": {"@type": "SearchAction", "target": {"@type": "EntryPoint", "urlTemplate": search},
                             "query-input": "required name=search_term_string"}}]}


def parcours_html(lang, meta, pages):
    """A learning path: a numbered track of step cards, each with a progress checkbox (see progress.js)."""
    t = LANGS[lang]
    missing = [s for s in meta["steps"] if s not in pages]
    if missing or not 3 <= len(meta["steps"]) <= 7:
        raise ValueError(f"path {meta['title']!r}: 3 to 7 existing steps required, got {meta['steps']} (missing {missing})")
    items = "\n".join(
        f'<li data-step="{html.escape(s)}"><span class="num">{i}</span>'
        f'<a href="{url(lang, s)}"><strong>{html.escape(pages[s][0]["title"])}</strong>'
        f'<span>{html.escape(pages[s][0]["summary"])}</span></a>'
        f'<input type="checkbox" aria-label="{html.escape(t["progress"])}: {html.escape(pages[s][0]["title"])}"></li>'
        for i, s in enumerate(meta["steps"], 1))
    return (f'<div class="parcours" data-total="{len(meta["steps"])}">\n'
            f'<p class="progress-line"><progress value="0" max="{len(meta["steps"])}" hidden></progress> '
            f'<span class="count" hidden></span></p>\n<ol class="track">\n{items}\n</ol>\n</div>\n'
            f'<script defer src="/progress.js"></script>\n')


def sprite(name, size, cls="sprite"):
    """A persona sprite frame (decorative): faded into the page background by CSS."""
    return (f'<img class="{cls}" src="/media/{name}.webp" alt="" width="{size}" height="{size}" '
            f'loading="lazy" decoding="async">')


def foot_fox(lang):
    """The fox waves at the end of an article."""
    return f'<p class="foot-fox">{sprite("fox-salue", 112)}<span>{LANGS[lang]["foot_fox"]}</span></p>\n'


def frieze():
    """Three breathing frames, stepped by CSS on the about page."""
    return '<div class="frieze" aria-hidden="true">' + "".join(sprite(f"fox-respire-{i}", 224) for i in range(3)) + "</div>\n"


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


def learning_paths_html(lang, pages):
    """Cards for the learning paths (pages with layout=parcours), in order."""
    t = LANGS[lang]
    slugs = sorted((s for s, (m, _) in pages.items() if m.get("layout") == "parcours"), key=lambda s: pages[s][0]["order"])
    items = "\n".join(
        f'<li><a href="{url(lang, s)}"><strong>{html.escape(pages[s][0]["title"])}</strong>'
        f'<span>{html.escape(pages[s][0]["summary"])}</span>'
        f'<em>{len(pages[s][0]["steps"])} {html.escape(t["step"].lower())}s</em></a></li>' for s in slugs)
    return f'<h2>{html.escape(t["learning_paths"])}</h2>\n<ul class="cards learning-paths">\n{items}\n</ul>' if items else ""


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
            f'<a href="{url(lang, "about")}"{CURRENT if slug == "about" else ""}>{html.escape(t["about"])}</a>'
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


INARI_TAILS = (
    '<path pathLength="1" class="inari-tail t0" d="M403.8,572.3L402.9,547.7L398.4,523.7L391.0,500.5L381.2,478.5L369.5,457.8L356.5,438.4L342.5,420.2L328.0,403.2L313.4,387.2L298.9,372.0L284.7,357.3L270.6,342.8L258.4,327.2L253.2,309.1L253.2,309.1L258.4,327.2L261.0,347.4L265.7,368.3L273.2,388.8L282.6,408.9L293.4,428.4L305.1,447.4L317.3,465.8L329.6,483.9L341.8,501.6L353.5,519.3L364.7,537.2L374.9,555.8L384.2,575.7Z"/>'
    '<path pathLength="1" class="inari-tail t1" d="M407.6,568.0L400.5,544.3L394.9,520.7L390.4,497.0L386.6,473.1L383.0,448.8L379.5,424.3L375.5,399.6L370.8,375.0L365.1,350.7L358.0,326.9L349.2,304.2L338.1,283.2L326.0,264.0L317.2,244.8L317.2,244.8L326.0,264.0L327.9,286.1L327.8,308.9L327.7,332.0L327.8,355.7L328.3,380.2L329.6,405.2L332.0,430.8L336.0,456.6L341.9,482.5L350.0,508.1L360.6,532.9L374.0,556.4L390.4,578.0Z"/>'
    '<path pathLength="1" class="inari-tail t2" d="M413.6,574.6L424.3,547.2L431.6,518.8L435.9,489.9L437.5,460.8L437.0,431.9L434.6,403.5L430.8,375.7L426.0,348.7L420.5,322.5L414.8,297.0L409.2,272.3L403.6,248.1L400.1,224.1L404.0,201.3L404.0,201.3L400.1,224.1L393.0,247.7L387.3,272.9L384.2,299.2L383.1,326.2L383.4,353.5L384.9,380.9L387.0,408.2L389.4,435.4L391.9,462.3L394.0,489.0L395.3,515.6L395.6,542.3L394.4,569.4Z"/>'
    '<path pathLength="1" class="inari-tail t3" d="M418.9,570.9L424.7,542.8L431.8,515.4L440.0,488.3L448.9,461.2L458.2,434.0L467.5,406.7L476.6,379.1L485.0,351.3L492.3,323.4L498.1,295.5L501.8,267.8L502.7,240.6L501.9,214.6L503.9,190.3L503.9,190.3L501.9,214.6L492.3,238.4L480.7,262.0L468.9,286.1L456.8,310.9L444.8,336.6L433.2,363.2L422.4,390.8L412.8,419.3L404.9,448.8L399.1,478.9L395.9,509.5L395.7,540.4L399.1,571.1Z"/>'
    '<path pathLength="1" class="inari-tail t4" d="M421.4,576.7L444.7,555.6L465.4,532.1L483.8,506.7L499.9,479.9L514.0,452.3L526.2,424.2L536.9,395.9L546.4,367.9L554.9,340.3L562.8,313.3L570.4,287.0L577.8,261.2L586.8,236.7L601.8,216.8L601.8,216.8L586.8,236.7L568.5,255.9L550.8,277.2L534.8,300.7L520.2,325.8L506.7,351.9L494.1,378.6L482.1,405.7L470.5,432.8L458.9,459.7L447.1,486.3L434.8,512.4L421.4,538.1L406.6,563.3Z"/>'
    '<path pathLength="1" class="inari-tail t5" d="M427.8,575.6L446.1,553.5L465.2,532.6L485.2,512.5L505.8,492.8L526.7,473.1L547.8,453.4L568.8,433.3L589.2,412.7L608.8,391.5L627.0,369.6L643.3,346.9L656.9,323.3L668.3,299.9L681.6,279.4L681.6,279.4L668.3,299.9L648.7,316.5L627.4,331.8L605.6,347.5L583.3,363.8L560.6,380.8L537.9,398.9L515.4,418.2L493.6,438.9L472.8,461.1L453.5,485.0L436.3,510.6L421.6,537.7L410.2,566.4Z"/>'
    '<path pathLength="1" class="inari-tail t6" d="M427.2,581.4L455.9,575.0L483.5,565.1L509.9,552.5L535.0,537.6L558.6,521.0L580.8,503.1L601.7,484.4L621.4,465.3L640.1,446.2L658.0,427.2L675.3,408.7L692.3,390.5L710.2,374.2L731.3,364.7L731.3,364.7L710.2,374.2L686.7,381.5L662.6,390.9L639.1,403.1L616.1,417.2L593.7,432.8L571.7,449.3L550.3,466.3L529.1,483.5L508.2,500.6L487.2,517.3L465.9,533.3L443.9,548.5L420.8,562.6Z"/>'
    '<path pathLength="1" class="inari-tail t7" d="M434.9,581.0L457.7,571.4L480.6,563.4L503.7,556.5L527.1,550.2L550.8,544.2L574.8,538.0L599.0,531.5L623.0,524.2L646.6,516.0L669.5,506.5L691.1,495.4L710.9,482.1L728.7,468.1L746.9,457.3L746.9,457.3L728.7,468.1L706.8,472.3L684.2,474.6L661.3,476.9L637.6,479.5L613.4,482.5L588.6,486.4L563.4,491.5L538.1,498.2L513.0,506.7L488.5,517.4L464.9,530.6L442.9,546.4L423.1,565.0Z"/>'
    '<path pathLength="1" class="inari-tail t8" d="M432.2,583.8L455.7,591.3L479.8,595.4L504.1,596.3L528.1,594.6L551.6,590.7L574.3,585.1L596.1,578.2L617.0,570.4L637.1,562.1L656.3,553.7L675.0,545.4L693.4,537.1L712.3,530.9L731.1,532.2L731.1,532.2L712.3,530.9L692.4,526.5L671.2,523.8L649.4,523.8L627.3,525.8L605.2,529.2L583.4,533.7L561.9,538.9L540.7,544.3L519.9,549.7L499.3,554.7L478.6,559.0L457.6,562.3L435.8,564.2Z"/>'
)

INARI_BODY = "M136,324C141,316 147,308 156,301C166,293 176,286 184,279C188,275 190,271 191,266C192,258 194,248 199,238C206,225 216,214 228,206C231,204 234,202 237,200C229,180 222,160 216,142C214,135 220,133 224,140C236,160 248,182 260,201C265,199 271,198 277,198C285,177 293,155 301,136C303,129 309,129 311,136C315,160 319,186 323,210C336,220 347,233 355,249C360,261 363,271 365,281C364,293 365,303 368,313C377,341 387,377 399,420C411,460 422,490 430,520C437,548 433,568 419,582C405,596 383,601 356,600L344,596C340,590 343,584 350,581C328,586 306,590 287,596C275,600 264,600 258,594C253,589 253,582 255,574L259,480C260,448 258,420 252,396C247,377 240,362 228,352C219,346 211,343 203,341C187,338 169,335 154,332C146,331 139,328 136,326C135,325 135,325 136,324 Z"

INARI_EYE = "M197,258 Q214,249 232,258 Q214,266 197,258 Z"



def hero(lang):
    """The home-page show: a full-viewport kitsunebi hero. The H1, the tagline and
    the Inari silhouette are plain DOM; hero.js only enhances (embers, springs,
    entrance, parallax), so the hero is complete without script or motion."""
    t = LANGS[lang]
    return (f'<section class="hero">'
            f'<canvas class="hero-embers" aria-hidden="true"></canvas>'
            f'<div class="hero-stage"><div class="hero-copy">'
            f'<p class="hero-kicker">{html.escape(t["hero_kicker"])}</p>'
            f'<h1 class="hero-title">FreedzHost</h1>'
            f'<p class="hero-tag">{html.escape(t["hero_tag"])}</p>'
            f'</div>'
            f'<svg class="hero-ink" viewBox="0 0 720 720" aria-hidden="true" focusable="false">'
            f'<path d="M60,560 C180,470 300,455 430,505 C540,547 620,540 690,480 '
            f'C640,560 540,600 420,585 C290,569 160,600 60,560 Z"/></svg>'
            f'<svg class="hero-inari" viewBox="0 0 720 720" preserveAspectRatio="xMidYMax meet" '
            f'aria-hidden="true" focusable="false">'
            f'<defs><linearGradient id="inari-copper" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="#f2a35c"/><stop offset=".55" stop-color="#e07a2f"/>'
            f'<stop offset="1" stop-color="#7d3f14"/></linearGradient></defs>'
            f'<g fill="url(#inari-copper)">{INARI_TAILS}'
            f'<path pathLength="1" class="inari-body" d="{INARI_BODY}"/></g>'
            f'<path class="inari-eye" d="{INARI_EYE}"/>'
            f'</svg></div>'
            f'<a class="hero-down" href="#hero-end" aria-label="{html.escape(t["hero_down"])}">'
            f'<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">'
            f'<path d="M4 9l8 8 8-8" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round"/></svg></a>'
            f'</section>\n'
            f'<div id="hero-end"></div>\n'
            f'<script defer src="/hero.js"></script>\n')


def layout(lang, slug, title, body, description, side="", jsonld=None):
    t = LANGS[lang]
    other = OTHER[lang]
    here = SITE + url(lang, slug)
    desc = html.escape(description)
    full = html.escape(title) + " · freedzhost.cloud"
    ld = jsonld_script(jsonld) + "\n" if jsonld else ""
    page_class = {"index": "home", "about": "about"}.get(slug, "")
    body_class = f' class="{page_class}"' if page_class else ""
    peek = '<img class="sprite peek" src="/media/fox-respire-0.webp" alt="" width="120" height="120" loading="lazy" decoding="async">\n' if slug == "index" else ""
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
<link rel="preload" href="/fonts/fraunces-600.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/style.css">
{ld}<script defer src="https://analytics.freedzhost.cloud/script.js" data-website-id="23badf50-b8d2-4487-b2ae-f67ab9fd172d"></script>
</head>
<body{body_class}>
<div class="den" aria-hidden="true"></div>
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
{peek}<script defer src="/search.js"></script>
<script defer src="/den.js"></script>
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
        newest = sorted((s for s in pages if s != "index" and not pages[s].get("nav") and pages[s].get("layout") != "parcours"), key=lambda s: -pages[s]["order"])
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
    dates = git_file_dates()
    revues = load_revue()
    latest_revue = revues[0] if revues else None
    latest_revue_date = latest_revue["date"] if latest_revue else None
    slugs = {}
    catalogue = {}
    for lang in LANGS:
        pages = {p.stem: read_page(p) for p in sorted((ROOT / "content" / lang).glob("*.html"))}
        slugs[lang] = set(pages)
        catalogue[lang] = {slug: meta for slug, (meta, _) in pages.items()}
        articles = sorted((s for s in pages if s != "index" and not pages[s][0].get("nav") and pages[s][0].get("layout") != "parcours"), key=lambda s: pages[s][0]["order"])
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
            body = body.replace("{{learning-paths}}", learning_paths_html(lang, pages))
            body = body.replace("{{series-cards}}", series_cards_html(lang, series_members))
            body = body.replace("{{search}}", search_form(lang, "page"))
            body = body.replace("{{articles}}", cards)
            if slug == "index":
                body = hero(lang) + body
            if meta.get("layout") == "parcours":
                body = (f'<article class="path-page">\n<h1>{html.escape(meta["title"])}</h1>\n{body}'
                        f'{parcours_html(lang, meta, pages)}</article>')
            elif slug != "index" and not meta.get("nav"):  # a nav page brings its own layout
                members = series_members.get(meta.get("series"), [])
                body = (f'<article>\n{fox(meta.get("series", ""), 88, "guide")}<h1>{html.escape(meta["title"])}</h1>\n{fiche(lang, meta, pages)}{body}'
                        f'{frieze() if slug == "about" else ""}{foot_fox(lang)}{banner(lang, slug)}{pager(lang, slug, pages, members)}</article>')
            target = out / LANGS[lang]["prefix"] / ("index.html" if slug == "index" else f"{slug}.html")
            target.parent.mkdir(parents=True, exist_ok=True)
            description = LANGS[lang]["description"] if slug == "index" else meta["summary"]
            target.write_text(layout(lang, slug, meta["title"], body, description, drawer(lang, slug, pages, series_members, latest_revue_date),
                                     site_jsonld(lang) if slug == "index" else article_jsonld(lang, slug, meta, dates)),
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
