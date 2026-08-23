#!/usr/bin/env python3
"""
Extract all image outputs from Jupyter notebooks into a flat folder.
"""

import json
import base64
from pathlib import Path

# ---------- config ----------
NOTEBOOKS_DIR = Path(".")          # folder that contains the .ipynb files
OUTPUT_DIR    = Path("plots")
# ----------------------------

OUTPUT_DIR.mkdir(exist_ok=True)

def save_image(data, out_path: Path):
    """data can be a string or a list of strings (rare but happens)."""
    if isinstance(data, list):
        data = "".join(data)
    img_bytes = base64.b64decode(data)
    out_path.write_bytes(img_bytes)

count = 0
for nb_path in sorted(NOTEBOOKS_DIR.glob("*.ipynb")):
    print(f"Scanning {nb_path}")
    with open(nb_path, encoding="utf-8") as f:
        nb = json.load(f)

    for cell_idx, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue

        for out_idx, output in enumerate(cell.get("outputs", [])):
            data = output.get("data", {})
            # matplotlib usually produces image/png; sometimes jpeg
            for mime in ("image/png", "image/jpeg"):
                if mime in data:
                    ext = "png" if "png" in mime else "jpg"
                    filename = f"{nb_path.stem}__cell{cell_idx:03d}_out{out_idx:02d}.{ext}"
                    save_image(data[mime], OUTPUT_DIR / filename)
                    print(f"Saved: {filename}")
                    count += 1
                    break   # one image per output is enough

print(f"Extracted {count} images → {OUTPUT_DIR.resolve()}")