#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
from datetime import datetime, UTC

HOME = "/data/data/com.termux/files/home"
BATCHES = os.path.join(HOME, "forensic-backend", "batches")
MEDIA = os.path.join(HOME, "forensic_media")
LOG = os.path.join(HOME, "downloads", "ingest_files.log")

RAW_NAME = "raw"

os.makedirs(BATCHES, exist_ok=True)
os.makedirs(MEDIA, exist_ok=True)

def now():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(msg):
    line = f"[INGEST {now()}] {msg}"
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def main():
    log("Starting ingestion...")

    batches = sorted(os.listdir(BATCHES))
    if not batches:
        log("No batches found.")
        return

    latest = batches[-1]
    batch_path = os.path.join(BATCHES, latest)
    raw_path = os.path.join(batch_path, RAW_NAME)

    if not os.path.isdir(raw_path):
        log("No raw folder found.")
        return

    ingest_path = os.path.join(batch_path, "ingested")
    os.makedirs(ingest_path, exist_ok=True)

    for name in sorted(os.listdir(raw_path)):
        src = os.path.join(raw_path, name)
        dst = os.path.join(ingest_path, name)
        try:
            shutil.copy2(src, dst)
            log(f"Ingested: {name}")
        except Exception as e:
            log(f"ERROR ingesting {name}: {e}")

    log("Ingestion complete.")

if __name__ == "__main__":
    main()
