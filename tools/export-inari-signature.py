#!/usr/bin/env python3
"""Export the canonical Inari signature (the nine-tailed silhouette) as a
standalone SVG asset, from the single source of truth in site_build.py.
Every surface that needs the mark consumes assets/inari/signature.svg —
nothing redraws it (docs/INARI.md, the anti-drift charter)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from site_build import INARI_BODY, INARI_EYE, INARI_TAILS

OUT = Path(__file__).resolve().parent.parent / "assets" / "inari" / "signature.svg"

SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 720">\n'
    '  <defs><linearGradient id="inari-copper" x1="0" y1="0" x2="0" y2="1">\n'
    '    <stop offset="0" stop-color="#f2a35c"/>\n'
    '    <stop offset=".55" stop-color="#e07a2f"/>\n'
    '    <stop offset="1" stop-color="#7d3f14"/>\n'
    '  </linearGradient></defs>\n'
    f'  <g fill="url(#inari-copper)">{INARI_TAILS}\n'
    f'  <path d="{INARI_BODY}"/></g>\n'
    f'  <path fill="#12100e" d="{INARI_EYE}"/>\n'
    '</svg>\n'
)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(SVG)
print(f"written {OUT} ({len(SVG)} bytes)")
