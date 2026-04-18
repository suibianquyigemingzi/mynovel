#!/usr/bin/env python3
"""Stub: Astro now uses the raw tracker HTML directly (replaced in workflow)."""
from pathlib import Path
Path("src/pages/index.astro").write_text(
    "<!-- tracker HTML is injected by workflow: cp data/site/index.html dist/index.html -->\n",
    encoding="utf-8"
)
print("Done (workflow does the injection)")