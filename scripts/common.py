"""CRICKCAST public-playlist updater helpers.

Only fetches explicitly configured public HTTP(S) sources. No cookies,
private tokens, browser sessions, or access-control bypassing are used.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "sources.json"
OUT = ROOT


def load_sources() -> dict:
    if not CONFIG.exists():
        return {}
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": "CRICKCAST-Playlist-Updater/1.0"})
    with urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def update_playlist(name: str, filename: str) -> bool:
    sources = load_sources()
    url = sources.get(name)
    if not url:
        print(f"{name}: no public source configured; skipped")
        return False
    if not url.startswith(("https://", "http://")):
        raise ValueError(f"{name}: source must be an HTTP(S) URL")
    data = fetch(url)
    if not data.strip():
        raise RuntimeError(f"{name}: source returned empty data")
    target = OUT / filename
    old = target.read_text(encoding="utf-8") if target.exists() else None
    if old == data:
        print(f"{name}: unchanged")
        return False
    target.write_text(data, encoding="utf-8")
    print(f"{name}: updated {filename}")
    return True
