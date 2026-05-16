#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime, UTC
from PIL import Image
from PIL.ExifTags import TAGS

HOME = "/data/data/com.termux/files/home"
BATCHES = os.path.join(HOME, "forensic-backend", "batches")
LOG = os.path.join(HOME, "downloads", "exif_engine.log")

def now():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(msg):
    line = f"[EXIF {now()}] {msg}"
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def extract_exif(path):
    try:
        img = Image.open(path)
        info = img._getexif()
        if not info:
            return {}

        exif_data = {}
        for tag, value in info.items():
            name = TAGS.get(tag, str(tag))
            exif_data[name] = value

        return exif_data
    except:
        return {}

def main():
    log("Starting EXIF engine...")

    batches = sorted(os.listdir(BATCHES))
    if not batches:
        log("No batches found.")
        return

    latest = batches[-1]
    batch_path = os.path.join(BATCHES, latest)
    ingest_path = os.path.join(batch_path, "ingested")

    if not os.path.isdir(ingest_path):
        log("No ingested folder.")
        return

    out_path = os.path.join(batch_path, "exif.json")
    results = {}

    for name in sorted(os.listdir(ingest_path)):
        fp = os.path.join(ingest_path, name)
        if not name.lower().endswith((".jpg", ".jpeg", ".png", ".tiff")):
            continue

        exif = extract_exif(fp)
        results[name] = exif
        log(f"EXIF: {name}")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    log("EXIF engine complete.")

if __name__ == "__main__":
    main()
