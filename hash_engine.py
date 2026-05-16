#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import hashlib
import json
from datetime import datetime, UTC

HOME = "/data/data/com.termux/files/home"
BATCHES = os.path.join(HOME, "forensic-backend", "batches")
LOG = os.path.join(HOME, "downloads", "hash_engine.log")

def now():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(msg):
    line = f"[HASH {now()}] {msg}"
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def sha256_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except:
        return None

def main():
    log("Starting hash engine...")

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

    out_path = os.path.join(batch_path, "hashes.json")
    results = {}

    for name in sorted(os.listdir(ingest_path)):
        fp = os.path.join(ingest_path, name)
        digest = sha256_file(fp)
        if digest:
            results[name] = digest
            log(f"Hashed: {name}")
        else:
            log(f"ERROR hashing: {name}")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    log("Hash engine complete.")

if __name__ == "__main__":
    main()
