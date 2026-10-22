"""Build the site for real and check what a visitor would hit."""

import re

import pytest

import site_build

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
            if article.name not in ("index.html", "help.html", "tutos.html") and not article.name.startswith("parcours-"):
                assert article.name in text, f"{home} misses {article.name}"


def test_home_has_both_paths_and_search(out):
    for home in (out / "index.html", out / "fr" / "index.html"):
        text = home.read_text(encoding="utf-8")
        assert 'class="cards paths"' in text and "tutos.html" in text and "formation.html" in text
        assert 'role="search"' in text


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
            if article.name not in ("index.html", "help.html", "tutos.html") and not article.name.startswith("parcours-"):
                assert any(link.endswith("/" + article.name) for link in links), (feed, article.name)


def test_every_page_has_canonical_and_description(out):
    for page in pages(out):
        text = page.read_text(encoding="utf-8")
        assert '<link rel="canonical" href="https://freedzhost.cloud/' in text, page
        assert '<meta name="description" content="' in text, page


def test_every_article_has_a_level_and_reaches_the_glossary(out):
    for page in pages(out):
        if page.name in ("index.html", "glossary.html", "help.html", "tutos.html") or page.name.startswith("parcours-"):
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


def jsonld_blocks(path):
    import json
    text = path.read_text(encoding="utf-8")
    return [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">\n(.*?)\n</script>', text, re.DOTALL)]


def test_articles_carry_techarticle_jsonld(out):
    data = jsonld_blocks(out / "fr" / "docker-gpu.html")[0]
    assert data["@type"] == "TechArticle" and data["inLanguage"] == "fr"
    assert data["proficiencyLevel"] == "Beginner" and data["dateModified"] == "2026-10-22"
    assert data["author"]["name"] == "freedzhost"
    assert jsonld_blocks(out / "first-model.html")[0]["@type"] == "TechArticle"


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


def test_paths_stay_out_of_search_index(out):
    assert "parcours" not in (out / "search-index.json").read_text(encoding="utf-8")


def test_every_diagram_figure_has_a_caption(out):
    for page in pages(out):
        for fig in re.findall(r'<figure class="diagram".*?</figure>', page.read_text(encoding="utf-8"), re.DOTALL):
            assert "<figcaption>" in fig, page
