#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime, UTC
import face_recognition

HOME = "/data/data/com.termux/files/home"
BATCHES = os.path.join(HOME, "forensic-backend", "batches")
LOG = os.path.join(HOME, "downloads", "pipeline_13_faces_advanced.log")

def now():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(msg):
    line = f"[FACES {now()}] {msg}"
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def process_image(path):
    try:
        img = face_recognition.load_image_file(path)
        locations = face_recognition.face_locations(img, model="hog")
        encodings = face_recognition.face_encodings(img, locations)

        faces = []
        for loc, enc in zip(locations, encodings):
            faces.append({
                "location": loc,
                "encoding": enc.tolist()
            })

        return faces
    except:
        return []

def main():
    log("Starting advanced face pipeline...")

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

    out_path = os.path.join(batch_path, "faces.json")
    results = {}

    for name in sorted(os.listdir(ingest_path)):
        fp = os.path.join(ingest_path, name)
        if not name.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        faces = process_image(fp)
        results[name] = faces
        log(f"Faces: {name} ({len(faces)})")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    log("Face pipeline complete.")

if __name__ == "__main__":
    main()
