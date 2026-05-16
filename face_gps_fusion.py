#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime, UTC

HOME = "/data/data/com.termux/files/home"
BATCHES = os.path.join(HOME, "forensic-backend", "batches")
LOG = os.path.join(HOME, "downloads", "face_gps_fusion.log")

def now():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(msg):
    line = f"[GPS-FUSION {now()}] {msg}"
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def extract_gps(exif):
    gps = exif.get("GPSInfo", {})
    if not gps:
        return None
    return gps

def main():
    log("Starting face + GPS fusion...")

    batches = sorted(os.listdir(BATCHES))
    if not batches:
        log("No batches found.")
        return

    latest = batches[-1]
    batch_path = os.path.join(BATCHES, latest)

    faces_path = os.path.join(batch_path, "faces.json")
    exif_path = os.path.join(batch_path, "exif.json")

    if not os.path.exists(faces_path) or not os.path.exists(exif_path):
        log("Missing faces.json or exif.json.")
        return

    with open(faces_path, "r", encoding="utf-8") as f:
        faces = json.load(f)

    with open(exif_path, "r", encoding="utf-8") as f:
        exif = json.load(f)

    fusion = []

    for filename, entries in faces.items():
        gps = extract_gps(exif.get(filename, {}))
        for face in entries:
            fusion.append({
                "file": filename,
                "timestamp_utc": now(),
                "location": face.get("location", []),
                "gps": gps
            })

    out_path = os.path.join(batch_path, "face_gps_fusion.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(fusion, f, indent=4)

    log("Face + GPS fusion complete.")

if __name__ == "__main__":
    main()
