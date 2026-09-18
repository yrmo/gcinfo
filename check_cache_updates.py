#!/usr/bin/env python3
"""Scan notebook code cells for data-file URLs, HEAD-check cache, update if changed."""

import json
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import requests

CACHE_DIR = Path("cache")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; gcinfo-cache-check/1.0)"}
URL_RE = re.compile(r'https?://[^\s\'"]+\.(?:zip|xlsx|xls|csv)(?:\?[^\s\'"]*)?', re.I)


def cell_text(source) -> str:
    text = "".join(source) if isinstance(source, list) else (source or "")
    # "https://open.canada.ca" + "/data/...csv"  →  one URL
    while True:
        nxt = re.sub(
            r'(["\'])(.*?)\1\s*\+\s*(["\'])(.*?)\3',
            lambda m: m.group(1) + m.group(2) + m.group(4) + m.group(1),
            text,
            count=1,
        )
        if nxt == text:
            return text
        text = nxt


def urls_in_notebook(path: Path) -> list[str]:
    nb = json.loads(path.read_text(encoding="utf-8"))
    found = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        for line in cell_text(cell.get("source", "")).splitlines():
            if line.strip().startswith("#"):
                continue
            found.extend(URL_RE.findall(line))
    return found


def filename_of(url: str) -> str:
    return url.split("/")[-1].split("?")[0]


def remote_info(url: str):
    r = requests.head(url, allow_redirects=True, timeout=30, headers=HEADERS)
    r.raise_for_status()
    size = r.headers.get("Content-Length")
    size = int(size) if size and size.isdigit() else None
    try:
        modified = parsedate_to_datetime(r.headers.get("Last-Modified"))
    except (TypeError, ValueError, IndexError):
        modified = None
    return size, modified


def needs_update(cache_path: Path, size, modified) -> bool:
    if not cache_path.exists():
        return True
    if size is not None and size != cache_path.stat().st_size:
        return True
    if modified is not None:
        local = datetime.fromtimestamp(cache_path.stat().st_mtime, tz=timezone.utc)
        if modified.tzinfo is None:
            modified = modified.replace(tzinfo=timezone.utc)
        if modified > local:
            return True
    return False


def download(url: str, cache_path: Path) -> int:
    r = requests.get(url, allow_redirects=True, timeout=120, headers=HEADERS)
    r.raise_for_status()
    cache_path.write_bytes(r.content)
    return len(r.content)


def main():
    CACHE_DIR.mkdir(exist_ok=True)
    by_url = {}
    for nb in sorted(Path(".").glob("*.ipynb")):
        for url in urls_in_notebook(nb):
            names = by_url.setdefault(url, [])
            if nb.name not in names:
                names.append(nb.name)

    if not by_url:
        return

    for url, notebooks in by_url.items():
        name = filename_of(url)
        used = ", ".join(notebooks)
        cache_path = CACHE_DIR / name
        try:
            size, modified = remote_info(url)
            if not needs_update(cache_path, size, modified):
                print(f"ok       {name}  ({used})")
                continue
            n = download(url, cache_path)
            print(f"updated  {name}  {n} bytes  ({used})")
        except Exception as e:
            print(f"error    {name}  {e}  ({used})")


if __name__ == "__main__":
    main()
