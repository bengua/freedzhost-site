"""Build the site for real and check what a visitor would hit."""

import re
from pathlib import Path

import pytest

import site_build
from site_build import url

# Generic on purpose: this file must not itself name the infrastructure it protects.
LEAK = re.compile(
    r"\b(?:10|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d+\.\d+(?:\.\d+)?\b"  # private IPv4
    r"|\b100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d+\.\d+\b"  # CGNAT, as used by tailnets
    r"|\btail[0-9a-f]{6,}\b"  # a real tailnet name
    r"|/home/[a-z]"  # a home directory
    r"|[\w.+-]+@[\w-]+\.[a-z]{2,6}\b"  # any e-mail address (not a systemd unit like x@y.service)
)


@pytest.fixture(scope="module")
def out(tmp_path_factory):
    return site_build.build(tmp_path_factory.mktemp("public"))


def pages(out):
    return sorted(out.rglob("*.html"))


def test_both_languages_have_the_same_pages(out):
    en = {p.name for p in out.glob("*.html")}
    fr = {p.name for p in (out / "fr").glob("*.html")}
    assert en == fr
    assert {"index.html", "manifesto.html", "first-model.html"} <= en


def test_every_page_declares_its_language(out):
    for page in pages(out):
        lang = "fr" if page.parent.name == "fr" else "en"
        assert f'<html lang="{lang}">' in page.read_text(encoding="utf-8"), page


def test_every_local_link_resolves(out):
    for page in pages(out):
        for ref in re.findall(r'(?:href|src|poster)="(/[^"]*)"', page.read_text(encoding="utf-8")):
            ref = ref.split("#")[0]
            target = out / ref.lstrip("/")
            if ref.endswith("/"):
                target = target / "index.html"
            assert target.exists(), f"{page.relative_to(out)} -> {ref}"


def test_tutos_page_lists_every_article(out):
    for home, folder in ((out / "tutos.html", out), (out / "fr" / "tutos.html", out / "fr")):
        text = home.read_text(encoding="utf-8")
        for article in folder.glob("*.html"):
            if article.name not in ("index.html", "help.html", "tutos.html", "profil.html") and not article.name.startswith("parcours-"):
                assert article.name in text, f"{home} misses {article.name}"


def test_home_has_the_briefing_paths_latest_and_letter(out):
    for home in (out / "index.html", out / "fr" / "index.html"):
        text = home.read_text(encoding="utf-8")
        assert 'class="revue"' in text
        assert 'class="cards learning-paths"' in text
        assert 'class="latest"' in text
        assert 'class="letter"' in text and "letter-form" in text
        assert 'role="search"' in text  # the drawer's search box


def test_nothing_internal_leaks_into_the_public_site(out):
    for path in out.rglob("*"):
        if path.suffix in (".html", ".css"):
            found = LEAK.findall(path.read_text(encoding="utf-8"))
            assert not found, f"{path.relative_to(out)}: {found}"


def test_a_page_without_translation_is_refused(tmp_path, monkeypatch):
    root = tmp_path / "root"
    for lang in ("en", "fr"):
        (root / "content" / lang).mkdir(parents=True)
        (root / "content" / lang / "index.html").write_text(
            '<!-- {"title": "t", "summary": "s", "order": 0} -->\n{{articles}}', encoding="utf-8")
    (root / "content" / "en" / "only.html").write_text(
        '<!-- {"title": "t", "summary": "s", "order": 1, "series": "start"} -->\nx', encoding="utf-8")
    (root / "static").mkdir()
    monkeypatch.setattr(site_build, "ROOT", root)
    with pytest.raises(ValueError, match="without translation"):
        site_build.build(tmp_path / "out")


def test_every_diagram_marker_is_drawn_and_described(out):
    for page in pages(out):
        text = page.read_text(encoding="utf-8")
        assert "{{diagram:" not in text, page
        for svg in re.findall(r"<svg[^>]*>", text):
            if 'aria-hidden="true"' in svg:  # decorative: hidden from the tree by design
                continue
            assert 'role="img"' in svg and 'aria-label="' in svg, page


def test_diagrams_exist_in_both_languages():
    import diagrams

    for name in diagrams.DIAGRAMS:
        en, fr = diagrams.render(name, "en"), diagrams.render(name, "fr")
        assert en != fr and "<figcaption>" in en and "<figcaption>" in fr


def test_sitemap_and_feeds_list_every_page(out):
    import xml.etree.ElementTree as ET

    sitemap = ET.parse(out / "sitemap.xml").getroot()
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = {e.text for e in sitemap.findall("s:url/s:loc", ns)}
    for page in pages(out):
        rel = page.relative_to(out).as_posix()
        path = "/" + ("" if rel == "index.html" else rel.replace("index.html", ""))
        assert site_build.SITE + path in locs, path
    for feed, folder in ((out / "feed.xml", out), (out / "fr" / "feed.xml", out / "fr")):
        links = {e.text for e in ET.parse(feed).getroot().iter("link")}
        for article in folder.glob("*.html"):
            if article.name not in ("index.html", "help.html", "tutos.html", "profil.html") and not article.name.startswith("parcours-"):
                assert any(link.endswith("/" + article.name) for link in links), (feed, article.name)


def test_every_page_has_canonical_and_description(out):
    for page in pages(out):
        text = page.read_text(encoding="utf-8")
        assert '<link rel="canonical" href="https://freedzhost.cloud/' in text, page
        assert '<meta name="description" content="' in text, page


def test_every_article_has_a_level_and_reaches_the_glossary(out):
    for page in pages(out):
        if page.name in ("index.html", "glossary.html", "help.html", "tutos.html", "profil.html") or page.name.startswith("parcours-"):
            continue
        text = page.read_text(encoding="utf-8")
        assert 'class="fiche level-' in text, page
        assert "glossary.html" in text, page


def test_new_pages_exist_in_both_languages(out):
    for slug in ("actualites.html", "formation.html", "materiel.html", "coups-de-coeur.html"):
        assert (out / slug).exists(), slug
        assert (out / "fr" / slug).exists(), f"fr/{slug}"


def test_home_has_the_daily_briefing(out):
    for home in (out / "index.html", out / "fr" / "index.html"):
        text = home.read_text(encoding="utf-8")
        assert 'class="revue"' in text, home
        assert "actualites.html" in text, home


def test_news_archive_lists_revue_items(out):
    archive = out / "fr" / "actualites.html"
    text = archive.read_text(encoding="utf-8")
    assert "Sipeed MaixStation" in text, archive
    assert "freedzhost.cloud passe à Inari" in text, archive


def test_drawer_has_the_new_navigation_tree(out):
    for home in (out / "index.html", out / "fr" / "index.html"):
        text = home.read_text(encoding="utf-8")
        assert 'class="drawer"' in text, home
        assert "formation.html" in text, home
        assert "materiel.html" in text, home
        assert "coups-de-coeur.html" in text, home


def test_drawer_stays_hidden_until_opened_on_desktop(out):
    style = (out / "style.css").read_text(encoding="utf-8")
    for hook in (
        "@media (min-width: 1024px)",
        ".drawer:target { transform: none; }",
    ):
        assert hook in style
    desktop = style.split("@media (min-width: 1024px)")[1]
    drawer = desktop[desktop.index(".drawer"):]
    assert ".drawer .close { display: none; }" not in drawer  # the overlay keeps its explicit close link on desktop
    assert "nav a.menu-btn { display: none" not in drawer  # the menu button stays on desktop
    top = style.split(".top-link { display: none; }")[1].split("/* ---- Typography")[0]
    assert ".brand { display: none" not in top  # the brand stays visible on desktop
    assert ".top > .brand { display: none" not in style  # the bar carries the brand again


def test_top_link_stays_compact_on_mobile_and_restores_on_desktop(out):
    style = (out / "style.css").read_text(encoding="utf-8")
    # The base hide rule must out-specificity `header.top nav a` (which forces
    # inline-flex on every nav anchor), or the mobile bar would not stay compact.
    base_rule = "header.top nav a.top-link { display: none"
    assert base_rule in style, "the base .top-link rule must win the specificity over `header.top nav a`"
    # The matching selector restores the links inside the desktop media query.
    desktop = style.split("@media (min-width: 1024px)")[1]
    assert "header.top nav a.top-link { display: inline-flex" in desktop  # same selector, back on desktop


def jsonld_blocks(path):
    import json
    text = path.read_text(encoding="utf-8")
    return [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">\n(.*?)\n</script>', text, re.DOTALL)]


def test_articles_carry_techarticle_jsonld(out):
    import subprocess

    def git_date(args, path):
        return subprocess.run(["git", "log", *args, "--format=%cI", "--", path],
                              capture_output=True, text=True, check=True).stdout.splitlines()[0]

    data = jsonld_blocks(out / "fr" / "docker-gpu.html")[0]
    assert data["@type"] == "TechArticle" and data["inLanguage"] == "fr"
    assert data["proficiencyLevel"] == "Beginner" and data["timeRequired"] == "PT30M"
    assert data["dateModified"] == git_date(["-1"], "content/fr/docker-gpu.html")
    assert data["datePublished"] == git_date(["--reverse"], "content/fr/docker-gpu.html")
    assert data["author"]["@type"] == "Organization" and data["author"]["name"] == "FreedzHost"
    assert data["publisher"]["name"] == "FreedzHost"
    assert jsonld_blocks(out / "first-model.html")[0]["@type"] == "TechArticle"


def test_non_article_pages_carry_their_own_type(out):
    assert jsonld_blocks(out / "fr" / "about.html")[0]["@type"] == "AboutPage"
    assert jsonld_blocks(out / "actualites.html")[0]["@type"] == "CollectionPage"
    assert jsonld_blocks(out / "tutos.html") == []


def test_human_durations_become_iso8601():
    assert site_build.iso_duration("30 min") == "PT30M"
    assert site_build.iso_duration("1 h") == "PT1H"
    assert site_build.iso_duration("1 h 30") == "PT1H30M"
    assert site_build.iso_duration("1–2 h") == "PT2H"  # a range counts by its upper bound
    assert site_build.iso_duration("1 h + compilation") == "PT1H"
    assert site_build.iso_duration("an evening") is None  # fuzzy text carries no duration


def test_home_pages_carry_organization_and_website(out):
    for page in (out / "index.html", out / "fr" / "index.html"):
        types = {n["@type"] for n in jsonld_blocks(page)[0]["@graph"]}
        assert types == {"Organization", "WebSite"}


def test_revision_line_is_visible(out):
    assert "Dernière révision :" in (out / "fr" / "turnstile.html").read_text(encoding="utf-8")
    assert "Last reviewed:" in (out / "turnstile.html").read_text(encoding="utf-8")


def test_learning_paths_render_steps_and_are_linked(out):
    for page, link in ((out / "parcours-model-7b.html", "/docker-gpu.html"),
                       (out / "fr" / "parcours-model-7b.html", "/fr/docker-gpu.html")):
        text = page.read_text(encoding="utf-8")
        assert text.count('<input type="checkbox"') == 4 and f'href="{link}"' in text
    assert "/parcours-cloud-exit.html" in (out / "index.html").read_text(encoding="utf-8")
    assert "/fr/parcours-cloud-exit.html" in (out / "fr" / "index.html").read_text(encoding="utf-8")


def test_home_hero_carries_the_localized_h1_and_both_cta_destinations(out):
    import html

    for lang, home in (("en", out / "index.html"), ("fr", out / "fr" / "index.html")):
        text = home.read_text(encoding="utf-8")
        tag = html.escape(site_build.LANGS[lang]["hero_tag"])
        assert f'<h1 class="hero-title">{tag}</h1>' in text, home
        assert f'href="{url(lang, "tutos")}"' in text, home
        assert f'href="{url(lang, "parcours-model-7b")}"' in text, home


def test_hero_ships_the_default_mascot_image(out):
    # The mascot is a still image now: the default src is in the DOM (so the
    # hero is complete without script) and the built WebP it points to ships.
    default_src = re.search(r'<img class="hero-mascot" src="([^"]+)"', (out / "index.html").read_text(encoding="utf-8"))
    assert default_src, "the home hero must carry the mascot img"
    assert (out / default_src.group(1).lstrip("/")).is_file(), default_src.group(1)


def test_every_hero_mascot_still_keeps_its_webp_alpha(out):
    # The hero mascots are stills with transparent backgrounds; an opaque
    # regression (e.g. a re-export without the VP8X alpha flag) would leave a
    # dark rectangle behind every mascot, so every localized hero_team still
    # must ship with the VP8X alpha bit set.
    import struct

    def vp8x_alpha(webp: Path) -> bool:
        assert webp.is_file(), webp
        data = webp.read_bytes()
        assert data[:4] == b"RIFF" and data[8:12] == b"WEBP", webp
        offset = 12
        while offset + 8 <= len(data):
            chunk = data[offset : offset + 4]
            size = struct.unpack("<I", data[offset + 4 : offset + 8])[0]
            if chunk == b"VP8X":
                return bool(data[offset + 12] & 0x10)
            offset += 8 + size + (size % 2)
        return False

    for lang, home in (("en", out / "index.html"), ("fr", out / "fr" / "index.html")):
        for name, _ in site_build.LANGS[lang]["hero_team"]:
            still = out / "media" / "personas" / f"{name}.webp"
            assert vp8x_alpha(still), still


def test_every_hero_mascot_entry_has_a_source_webp(out):
    # Only frame-zero-clean personas may anchor the hero, and each localized
    # entry must resolve to a WebP that is actually shipped in the build. The
    # entry's name (not the path) is what the DOM carries; the still is derived
    # from it, so we check both the shipped file and the localized entry itself.
    for lang, home in (("en", out / "index.html"), ("fr", out / "fr" / "index.html")):
        text = home.read_text(encoding="utf-8")
        for name, label in site_build.LANGS[lang]["hero_team"]:
            still = f"/media/personas/{name}.webp"
            assert (out / still.lstrip("/")).is_file(), (name, still)
        # The localized entries themselves are the source: names must be unique
        # and each localized hero_team must render into the hero-team block.
        rendered = re.search(r'<script type="application/json" class="hero-team">(.*?)</script>', text, re.DOTALL)
        assert rendered, home
        import json as _json
        names = [entry[0] for entry in _json.loads(rendered.group(1))]
        assert names == [name for name, _ in site_build.LANGS[lang]["hero_team"]], home
    # The two localized lists name the same personas, so the build has no orphan.
    assert [n for n, _ in site_build.LANGS["en"]["hero_team"]] == [n for n, _ in site_build.LANGS["fr"]["hero_team"]]


STATIC = Path(__file__).resolve().parent.parent / "static"


def test_hero_mascot_layout_reserves_its_band_and_keeps_the_grid():
    # The hero's layout must stay what it is: the desktop .hero-stage is the
    # two-column grid the key art composes against, mobile collapses to one
    # column, and on mobile the in-flow hero reserves a real bottom band with
    # padding (no viewport or fixed heights) so the still mascot and its tag
    # sit below every copy/CTA without covering them.
    css = (STATIC / "style.css").read_text(encoding="utf-8")

    def media_blocks(css_text, query):
        """Return the bodies of every `@media <query> { ... }` block."""
        bodies = []
        for m in re.finditer(re.escape("@media " + query) + r"\s*\{", css_text):
            depth, start = 0, m.end() - 1
            for i in range(start, len(css_text)):
                if css_text[i] == "{":
                    depth += 1
                elif css_text[i] == "}":
                    depth -= 1
                    if depth == 0:
                        bodies.append(css_text[start + 1 : i])
                        break
        assert bodies, "style.css must keep an @media " + query + " block"
        return bodies

    def rules_in(block):
        """Map selector -> declarations for the rules of one CSS block."""
        by_sel = {}
        for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", block):
            sel = re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.DOTALL)
            sel = re.sub(r"\s+", " ", sel).strip().lower()
            decls = re.sub(r"\s+", " ", m.group(2).strip()).lower()
            by_sel.setdefault(sel, []).append(decls)
        return by_sel

    mobile = {}
    for body in media_blocks(css, "(max-width: 760px)"):
        for sel, decls in rules_in(body).items():
            mobile.setdefault(sel, []).extend(decls)

    # The mobile one-column hero-stage rule, restored.
    hero_stage_decls = " ".join(mobile.get(".hero-stage", []))
    assert "grid-template-columns: 1fr;" in hero_stage_decls, (
        "the mobile hero-stage must collapse to one column"
    )

    # The mobile reservation is real padding on the hero, not a fake height:
    # no viewport-unit height may stand in for the band. The home hero is the
    # first section of main, so the padding must live on the exact
    # higher-specificity selector `body.home main > section.hero` — the bare
    # `.hero` rule would lose to the later `body.home main > section` padding.
    hero_decls = " ".join(mobile.get("body.home main > section.hero", []))
    assert "padding-bottom: 200px;" in hero_decls, (
        "the mobile home hero must reserve the mascot band with padding-bottom"
    )

    # The still mascot is a 512x512 image: height auto keeps its square aspect
    # at every responsive width, so the width rules above never squish it.
    base_mascot = re.search(r"^\.hero-mascot \{[^}]*\}", css, re.MULTILINE)
    assert base_mascot, "style.css must keep the base .hero-mascot rule"
    assert "height: auto;" in re.sub(r"\s+", " ", base_mascot.group(0)).lower(), (
        "the base hero-mascot rule must keep the image square with height auto"
    )

    # Desktop keeps the two-column hero-stage grid, restored.
    desktop = re.search(r"^\.hero-stage \{[^}]*\}", css, re.MULTILINE)
    assert desktop, "style.css must keep the desktop .hero-stage rule"
    desktop_decls = re.sub(r"\s+", " ", desktop.group(0))
    assert "display: grid;" in desktop_decls and "grid-template-columns:" in desktop_decls, (
        "the desktop hero-stage must stay a grid"
    )


def test_paths_stay_out_of_search_index(out):
    assert "parcours" not in (out / "search-index.json").read_text(encoding="utf-8")


def test_every_diagram_figure_has_a_caption(out):
    for page in pages(out):
        for fig in re.findall(r'<figure class="diagram".*?</figure>', page.read_text(encoding="utf-8"), re.DOTALL):
            assert "<figcaption>" in fig, page


def test_campus_data_and_xp_chip(out):
    import json
    for lang, home in (("en", out / "index.html"), ("fr", out / "fr" / "index.html")):
        text = home.read_text(encoding="utf-8")
        assert 'class="xp-chip"' in text and "profil.html" in text, home
        assert '<script defer src="/progress.js"></script>' in text, home
        data = json.loads((out / f"campus-{lang}.json").read_text(encoding="utf-8"))
        assert [lv["xp"] for lv in data["levels"]] == sorted(lv["xp"] for lv in data["levels"])
        assert data["levels"][0]["xp"] == 0
        for badge in data["badges"]:
            assert badge["step"] is None or badge["step"] in data["steps"], badge
        for slug, step in data["steps"].items():
            assert step["xp"] > 0, slug
            if step["pattern"]:
                assert step["hint"], slug


def test_learning_paths_carry_quest_and_proofs(out):
    for page in (out / "parcours-model-7b.html", out / "fr" / "parcours-cloud-exit.html"):
        text = page.read_text(encoding="utf-8")
        assert 'class="quest"' in text and "data-quest-xp" in text, page
        assert text.count('<details class="proof"') == text.count('<input type="checkbox"'), page
        assert "data-check" in text and 'role="status"' in text, page


def test_profile_page_renders_in_both_languages(out):
    for page in (out / "profil.html", out / "fr" / "profil.html"):
        text = page.read_text(encoding="utf-8")
        for hook in ("data-score", "data-xp", "data-badge=", "data-tips-step=", "data-export", "data-import", "<noscript>"):
            assert hook in text, (page, hook)
        assert text.count("data-level=") == 8, page
