#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import math
from datetime import datetime, UTC
from pathlib import Path

HOME = "/data/data/com.termux/files/home"
BATCHES = os.path.join(HOME, "forensic-backend", "batches")
LOG = os.path.join(HOME, "downloads", "stego_engine.log")

def now():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(msg):
    line = f"[STEGO {now()}] {msg}"
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def file_entropy(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        if not data:
            return 0.0
        freq = [0] * 256
        for b in data:
            freq[b] += 1
        entropy = 0.0
        for count in freq:
            if count == 0:
                continue
            p = count / len(data)
            entropy -= p * math.log2(p)
        return entropy
    except:
        return 0.0

def detect_lsb(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        if not data:
            return False
        lsb_bits = [b & 1 for b in data[:4096]]
        ones = sum(lsb_bits)
        ratio = ones / len(lsb_bits)
        return 0.45 < ratio < 0.55
    except:
        return False

def main():
    log("Starting stego engine...")

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

    out_path = os.path.join(batch_path, "stego.json")
    results = {}

    for name in sorted(os.listdir(ingest_path)):
        fp = os.path.join(ingest_path, name)
        ent = file_entropy(fp)
        lsb = detect_lsb(fp)

        results[name] = {
            "entropy": ent,
            "lsb_suspicious": lsb,
            "risk": "high" if ent > 7.5 or lsb else "low"
        }

        log(f"Stego scan: {name} (entropy={ent:.2f}, lsb={lsb})")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    log("Stego engine complete.")

if __name__ == "__main__":
    main()
