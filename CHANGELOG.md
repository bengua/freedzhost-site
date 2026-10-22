# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Newest first. An entry says what changed for someone using the thing, not what
was edited — "the follower no longer truncates the agent's reasoning" rather
than "modified fh-suivre".

## [Unreleased]

### Added
- Every article now carries a Schema.org JSON-LD block: TechArticle with the
  level as proficiencyLevel, the estimated time as an ISO 8601 timeRequired,
  and datePublished/dateModified taken from the file's git history; the About
  page carries AboutPage and the news archive CollectionPage, each naming
  FreedzHost as author and publisher. `tools/validate-jsonld.py` checks every
  built page against its source header.

### Changed
- The Android console is now called Inari (FreedzHost Inari): articles say
  "Inari" where they said "SwarmFox", in both languages. Slugs and links do
  not move.
- Pages carry the Inari favicon: the seven-tailed kitsune silhouette, copper
  on charcoal, same mark as the app's launcher icon.

- English and French site: home with teaser and FoxBot app, manifesto, hardware guide, NVIDIA driver, Docker with GPU, first local model.
