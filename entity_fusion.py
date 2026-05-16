#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime, UTC

HOME = "/data/data/com.termux/files/home"
BATCHES = os.path.join(HOME, "forensic-backend", "batches")
LOG = os.path.join(HOME, "downloads", "entity_fusion.log")

def now():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(msg):
    line = f"[ENTITY-FUSION {now()}] {msg}"
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def main():
    log("Starting entity fusion...")

    batches = sorted(os.listdir(BATCHES))
    if not batches:
        log("No batches found.")
        return

    latest = batches[-1]
    batch = os.path.join(BATCHES, latest)

    paths = {
        "faces": os.path.join(batch, "faces.json"),
        "exif": os.path.join(batch, "exif.json"),
        "ocr": os.path.join(batch, "ocr.json"),
        "stego": os.path.join(batch, "stego.json"),
        "risk": os.path.join(batch, "face_risk.json")
    }

    if not all(os.path.exists(p) for p in paths.values()):
        log("Missing required files.")
        return

    with open(paths["faces"], "r", encoding="utf-8") as f:
        faces = json.load(f)

    with open(paths["exif"], "r", encoding="utf-8") as f:
        exif = json.load(f)

    with open(paths["ocr"], "r", encoding="utf-8") as f:
        ocr = json.load(f)

    with open(paths["stego"], "r", encoding="utf-8") as f:
        stego = json.load(f)

    with open(paths["risk"], "r", encoding="utf-8") as f:
        risk = json.load(f)

    fusion = {}

    for filename in sorted(faces.keys()):
        fusion[filename] = {
            "faces": faces.get(filename, []),
            "exif": exif.get(filename, {}),
            "ocr": ocr.get(filename, ""),
            "stego": stego.get(filename, {}),
            "risk": risk.get(filename, {})
        }

        log(f"Fused: {filename}")

    out_path = os.path.join(batch, "entity_fusion.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(fusion, f, indent=4)

    log("Entity fusion complete.")

if __name__ == "__main__":
    main()
