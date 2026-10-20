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
    r"|[\w.+-]+@[\w-]+\.[\w.]+"  # any e-mail address
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
            target = out / ref.lstrip("/")
            if ref.endswith("/"):
                target = target / "index.html"
            assert target.exists(), f"{page.relative_to(out)} -> {ref}"


def test_home_lists_every_article(out):
    for home, folder in ((out / "index.html", out), (out / "fr" / "index.html", out / "fr")):
        text = home.read_text(encoding="utf-8")
        for article in folder.glob("*.html"):
            if article.name != "index.html":
                assert article.name in text, f"{home} misses {article.name}"


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
