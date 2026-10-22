#!/usr/bin/env python3
"""Validate the JSON-LD of every built page against its source header.

Reads the build output (public/ by default), parses each application/ld+json
block, and checks: valid JSON, the required keys for the page kind, an
ISO 8601 timeRequired, and consistency with the JSON comment header of the
source page in content/ — headline, description, language, proficiency, and
the git commit dates. Home pages are only checked for valid JSON: another
workstream owns them. Exit 1 on any failure.
"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import site_build

BLOCK = re.compile(r'<script type="application/ld\+json">\n(.*?)\n</script>', re.DOTALL)
DURATION = re.compile(r"PT(\d+H)?(\d+M)?$")
ARTICLE_TYPES = {"TechArticle", "AboutPage", "CollectionPage"}


def validate_page(page, out, dates, errors):
    lang = "fr" if page.parent.name == "fr" else "en"
    slug = page.stem
    text = page.read_text(encoding="utf-8")
    blocks = []
    for raw in BLOCK.findall(text):
        try:
            blocks.append(json.loads(raw))
        except json.JSONDecodeError as exc:
            errors.append(f"{lang}/{slug}: invalid JSON-LD: {exc}")
    if slug == "index":
        return bool(blocks)  # home: valid JSON is all this validator asserts
    source = ROOT / "content" / lang / f"{slug}.html"
    if not source.exists():
        errors.append(f"{lang}/{slug}: no source page")
        return False
    meta, _ = site_build.read_page(source)
    if "level" not in meta:  # nav and path pages carry no JSON-LD
        if blocks:
            errors.append(f"{lang}/{slug}: nav page carries JSON-LD")
            return False
        return True
    if len(blocks) != 1:
        errors.append(f"{lang}/{slug}: expected one JSON-LD block, got {len(blocks)}")
        return False
    data = blocks[0]
    kind = site_build.NON_ARTICLE_TYPES.get(slug, "TechArticle")
    checks = {
        "@type": kind,
        "headline": meta["title"],
        "description": meta["summary"],
        "inLanguage": lang,
        "url": site_build.SITE + site_build.url(lang, slug),
    }
    for key, want in checks.items():
        if data.get(key) != want:
            errors.append(f"{lang}/{slug}: {key} is {data.get(key)!r}, expected {want!r}")
    for key in ("datePublished", "dateModified"):
        if key not in data:
            errors.append(f"{lang}/{slug}: missing {key}")
    git = dates.get(f"content/{lang}/{slug}.html")
    if git and data.get("dateModified") != git[0]:
        errors.append(f"{lang}/{slug}: dateModified {data.get('dateModified')!r} != git {git[0]!r}")
    if git and data.get("datePublished") != git[1]:
        errors.append(f"{lang}/{slug}: datePublished {data.get('datePublished')!r} != git {git[1]!r}")
    if (kind == "TechArticle" and meta["level"] in site_build.PROFICIENCY
            and data.get("proficiencyLevel") != site_build.PROFICIENCY[meta["level"]]):
        errors.append(f"{lang}/{slug}: wrong proficiencyLevel {data.get('proficiencyLevel')!r}")
    duration = meta.get("duration") or site_build.iso_duration(meta.get("time"))
    if duration and data.get("timeRequired") != duration:
        errors.append(f"{lang}/{slug}: timeRequired {data.get('timeRequired')!r}, expected {duration!r}")
    if "timeRequired" in data and not DURATION.fullmatch(data["timeRequired"]):
        errors.append(f"{lang}/{slug}: timeRequired {data['timeRequired']!r} is not ISO 8601")
    return not any(e.startswith(f"{lang}/{slug}:") for e in errors)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    out = pathlib.Path(argv[0]) if argv else ROOT / "public"
    dates = site_build.git_file_dates()
    errors = []
    pages = sorted(out.rglob("*.html"))
    validated = sum(validate_page(p, out, dates, errors) for p in pages)
    for error in errors:
        print(f"FAIL {error}")
    print(f"JSON-LD: {validated}/{len(pages)} pages valid, {len(errors)} error(s)")
    return 0 if not errors and validated == len(pages) else 1


if __name__ == "__main__":
    sys.exit(main())
