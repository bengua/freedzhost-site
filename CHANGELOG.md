# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Newest first. An entry says what changed for someone using the thing, not what
was edited — "the follower no longer truncates the agent's reasoning" rather
than "modified fh-suivre".

## [Unreleased]

### Added
- The home page ends with the den letter: one e-mail per new tutorial, through
  the site's own contact API (nothing at a third party), with the RSS feed as
  the no-inbox alternative.
- The home page features the latest tutorial between the learning paths and
  the letter.
- The design system is written down as tokens in style.css: one copper accent,
  three neutrals, the text color in three opacity steps, the 12-to-64 px type
  scale (Fraunces for display, Inter for text, both bundled and subsetted),
  the 4 px grid with 96/48 px section rhythm, 8 px cards and pill radius, one
  shadow, and the motion rules (transform + opacity only, 150-250 ms micro,
  400-600 ms transitions, IntersectionObserver reveals staggered 60 ms).
- FoxBot idles with a breathing loop and switches to typing while the daily
  briefing — the swarm's work — is on screen. Everything stops under
  prefers-reduced-motion.
- A skip link opens every page.
- Every article now carries a Schema.org JSON-LD block: TechArticle with the
  level as proficiencyLevel, the estimated time as an ISO 8601 timeRequired,
  and datePublished/dateModified taken from the file's git history; the About
  page carries AboutPage and the news archive CollectionPage, each naming
  FreedzHost as author and publisher. `tools/validate-jsonld.py` checks every
  built page against its source header.

### Changed
- The home page is now: sticky blurred nav, the hero (one sentence, one call
  to action, the persona team), the daily briefing capped at three items, the
  learning paths, the latest tutorial, the letter, the footer. The welcome
  manifesto, the two-entry paths block, the series cards, the Inari app
  screenshots and the cost/promise/scale essays move out of the home page.
- The top bar is sticky with a blurred backdrop on every page; on wide screens
  it carries quick links (news, tutorials, training) and leaves the brand to
  the drawer.
- The Android console is now called Inari (FreedzHost Inari): articles say
  "Inari" where they said "SwarmFox", in both languages. Slugs and links do
  not move.
- Pages carry the Inari favicon: the seven-tailed kitsune silhouette, copper
  on charcoal, same mark as the app's launcher icon.

- English and French site: home with teaser and FoxBot app, manifesto, hardware guide, NVIDIA driver, Docker with GPU, first local model.
