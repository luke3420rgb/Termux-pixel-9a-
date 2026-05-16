#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime, UTC

HOME = "/data/data/com.termux/files/home"
BATCHES = os.path.join(HOME, "forensic-backend", "batches")
LOG = os.path.join(HOME, "downloads", "narrative_engine.log")

def now():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(msg):
    line = f"[NARRATIVE {now()}] {msg}"
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def safe(v):
    return v if v else "None"

def main():
    log("Starting narrative engine...")

    batches = sorted(os.listdir(BATCHES))
    if not batches:
        log("No batches found.")
        return

    latest = batches[-1]
    batch = os.path.join(BATCHES, latest)

    paths = {
        "entities": os.path.join(batch, "entity_fusion.json"),
        "risk": os.path.join(batch, "face_risk.json"),
        "timeline": os.path.join(batch, "face_timeline.json"),
        "gps": os.path.join(batch, "face_gps_fusion.json"),
        "stego": os.path.join(batch, "stego.json")
    }

    if not all(os.path.exists(p) for p in paths.values()):
        log("Missing required files.")
        return

    with open(paths["entities"], "r", encoding="utf-8") as f:
        entities = json.load(f)

    with open(paths["risk"], "r", encoding="utf-8") as f:
        risk = json.load(f)

    with open(paths["timeline"], "r", encoding="utf-8") as f:
        timeline = json.load(f)

    with open(paths["gps"], "r", encoding="utf-8") as f:
        gps = json.load(f)

    with open(paths["stego"], "r", encoding="utf-8") as f:
        stego = json.load(f)

    narrative = []
    narrative.append(f"Forensic Narrative Report — Generated {now()}")
    narrative.append("=" * 60)
    narrative.append("")

    for filename, data in entities.items():
        narrative.append(f"FILE: {filename}")
        narrative.append("-" * 60)

        r = risk.get(filename, {})
        s = stego.get(filename, {})
        faces = data.get("faces", [])
        ocr = data.get("ocr", "")
        exif = data.get("exif", {})

        narrative.append(f"Faces detected: {len(faces)}")
        narrative.append(f"Risk level: {safe(r.get('risk_level'))}")
        narrative.append(f"Entropy: {safe(s.get('entropy'))}")
        narrative.append(f"LSB suspicious: {safe(s.get('lsb_suspicious'))}")
        narrative.append(f"OCR text present: {'yes' if ocr.strip() else 'no'}")
        narrative.append(f"EXIF present: {'yes' if exif else 'no'}")
        narrative.append("")

    out_path = os.path.join(batch, "narrative.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(narrative))

    log("Narrative engine complete.")

if __name__ == "__main__":
    main()
