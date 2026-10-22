# Contributing

## The one rule that matters

**A change is verified by running it.** Before a pull request is opened, the
site has been built and the result looked at in a browser: a page that was
written but never rendered is not done.

```sh
python3 site_build.py
python3 -m http.server -d public
python3 -m pytest
```

## How work reaches `main`

Nobody pushes to `main`. Fork the repository, work on a branch, and open a pull
request. The CI (`.github/workflows/ci.yml`) builds the site, runs the tests and
`ruff`; a pull request is merged only when it is green.

## Adding or editing a page

- Every page exists in both languages: `content/en/<slug>.html` and
  `content/fr/<slug>.html`. A missing translation stops the build on purpose.
- The first line of each fragment is its header:
  `<!-- {"title": "…", "summary": "…", "order": 6} -->`.
- Media go in `static/media/`. Keep them small: the site is meant to load fast
  on a modest connection.
- Never paste a private address, a home directory or a personal e-mail into a
  page: `tests/test_site.py` refuses them, and it is right to.

## Before you open a pull request

- The site builds and the changed pages have been viewed.
- `python3 -m pytest` and `ruff check .` pass.
- `README.md` still describes what the repository does, including its limits.
- `CHANGELOG.md` has an entry under `Unreleased`.
- Code, comments and commit messages are in English; editorial content lives in
  both English and French.

## What CI checks, and what it does not

CI checks that the site builds, that internal links resolve, that both languages
are complete, that nothing internal leaks into the output, and that the code is
clean. It does not check that an article is right. Green means the checks
passed; it does not mean the tutorial works on a fresh machine — replay it if
you change its steps.

## Licensing of contributions

By contributing, you agree that your contribution is published under the
license of the part you touch: CC BY-SA 4.0 for content (`content/`, `static/`),
MIT for the generator code (`site_build.py`, `diagrams.py`, `tests/`).
