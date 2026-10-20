# freedzhost-site

The public website of [freedzhost.cloud](https://freedzhost.cloud): a manifesto
and free tutorials on running your own AI agent node, in English and French.

## Install

Python 3.10 or newer, nothing else: the generator uses the standard library only.

## Use

    python3 site_build.py            # writes public/
    python3 -m http.server -d public # preview on http://127.0.0.1:8000

Add a page by writing the same slug twice, `content/en/<slug>.html` and
`content/fr/<slug>.html`. Its first line is a JSON comment:

    <!-- {"title": "…", "summary": "…", "order": 6} -->

The home page lists articles by `order`. Images and videos go in `static/media/`.

## How it works

`site_build.py` copies `static/` into `public/`, wraps each content fragment in
one layout (header, language switch, footer) and writes English at the root and
French under `/fr/`. A page that exists in one language only stops the build.

The tests build the site for real, then check every local link and image, that
both languages hold the same pages, and that no internal address, host name or
home path reaches a public page.

## Limits

- The tutorials were checked against the upstream documentation and against the
  fleet's own running configuration, not replayed on a fresh machine yet.
- The teaser is in French only.
- The site is static: no search, no comments, no analytics, on purpose.
- Content is CC BY-SA 4.0; the generator ships under the same licence.
