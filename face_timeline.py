#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime, UTC

HOME = "/data/data/com.termux/files/home"
BATCHES = os.path.join(HOME, "forensic-backend", "batches")
LOG = os.path.join(HOME, "downloads", "face_timeline.log")

def now():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(msg):
    line = f"[TIMELINE {now()}] {msg}"
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def main():
    log("Starting face timeline engine...")

    batches = sorted(os.listdir(BATCHES))
    if not batches:
        log("No batches found.")
        return

    latest = batches[-1]
    batch_path = os.path.join(BATCHES, latest)

    faces_path = os.path.join(batch_path, "faces.json")
    if not os.path.exists(faces_path):
        log("faces.json missing.")
        return

    with open(faces_path, "r", encoding="utf-8") as f:
        faces = json.load(f)

    timeline = []
    for filename, entries in faces.items():
        for face in entries:
            timeline.append({
                "file": filename,
                "timestamp_utc": now(),
                "location": face.get("location", [])
            })

    out_path = os.path.join(batch_path, "face_timeline.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=4)

    log("Face timeline complete.")

if __name__ == "__main__":
    main()
