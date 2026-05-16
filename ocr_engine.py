#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import subprocess
from datetime import datetime, UTC

HOME = "/data/data/com.termux/files/home"
BATCHES = os.path.join(HOME, "forensic-backend", "batches")
LOG = os.path.join(HOME, "downloads", "ocr_engine.log")

def now():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(msg):
    line = f"[OCR {now()}] {msg}"
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def run_tesseract(src, dst):
    try:
        subprocess.run(["tesseract", src, dst], check=False)
        txt_file = dst + ".txt"
        if os.path.exists(txt_file):
            with open(txt_file, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    except:
        pass
    return ""

def main():
    log("Starting OCR engine...")

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

    out_path = os.path.join(batch_path, "ocr.json")
    results = {}

    for name in sorted(os.listdir(ingest_path)):
        fp = os.path.join(ingest_path, name)
        if not name.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        tmp_out = os.path.join(batch_path, f"ocr_{name}")
        text = run_tesseract(fp, tmp_out)
        results[name] = text
        log(f"OCR: {name}")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    log("OCR engine complete.")

if __name__ == "__main__":
    main()
