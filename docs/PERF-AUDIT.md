# Performance audit (2026-10-22, report only, nothing changed)

- Files over 200 KB: `static/media/shot-rooms.jpg` (216 KB) and `static/media/teaser-fr.mp4` (5.2 MB, the French teaser).
- Third-party scripts: none. The only external script is our own analytics (`analytics.freedzhost.cloud/script.js`, `defer`). No external fonts, no external CSS.
- What can delay LCP: one render-blocking stylesheet (`/style.css`, same origin). Scripts are `defer`. The footer mascot is a `<video autoplay>`; check it does not preload eagerly. Fox images are small, lazy and sized.
- Candidates for later: recompress `shot-rooms.jpg` to WebP, check the `preload` attribute of the footer video, inline the critical CSS only if measurements justify it.
