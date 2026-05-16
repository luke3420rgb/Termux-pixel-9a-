#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime, UTC
from pathlib import Path

HOME = "/data/data/com.termux/files/home"
BATCHES = os.path.join(HOME, "forensic-backend", "batches")
LOG = os.path.join(HOME, "downloads", "metadata_engine.log")

def now():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(msg):
    line = f"[META {now()}] {msg}"
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def file_metadata(path: Path):
    try:
        stat = path.stat()
        return {
            "name": path.name,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
            "created": datetime.fromtimestamp(stat.st_ctime, UTC).isoformat(),
            "type": path.suffix.lower(),
        }
    except:
        return None

def main():
    log("Starting metadata engine...")

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

    out_path = os.path.join(batch_path, "metadata.json")
    results = []

    for name in sorted(os.listdir(ingest_path)):
        fp = Path(os.path.join(ingest_path, name))
        meta = file_metadata(fp)
        if meta:
            results.append(meta)
            log(f"Metadata: {name}")
        else:
            log(f"ERROR metadata: {name}")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    log("Metadata engine complete.")

if __name__ == "__main__":
    main()
