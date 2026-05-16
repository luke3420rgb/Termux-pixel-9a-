#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime, UTC

HOME = "/data/data/com.termux/files/home"
BATCHES = os.path.join(HOME, "forensic-backend", "batches")
LOG = os.path.join(HOME, "downloads", "face_risk_engine.log")

def now():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(msg):
    line = f"[FACE-RISK {now()}] {msg}"
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def main():
    log("Starting face risk engine...")

    batches = sorted(os.listdir(BATCHES))
    if not batches:
        log("No batches found.")
        return

    latest = batches[-1]
    batch = os.path.join(BATCHES, latest)

    faces_path = os.path.join(batch, "faces.json")
    gps_path = os.path.join(batch, "face_gps_fusion.json")
    stego_path = os.path.join(batch, "stego.json")
    ocr_path = os.path.join(batch, "ocr.json")

    if not all(os.path.exists(p) for p in [faces_path, gps_path, stego_path, ocr_path]):
        log("Missing required files.")
        return

    with open(faces_path, "r", encoding="utf-8") as f:
        faces = json.load(f)

    with open(gps_path, "r", encoding="utf-8") as f:
        gps = json.load(f)

    with open(stego_path, "r", encoding="utf-8") as f:
        stego = json.load(f)

    with open(ocr_path, "r", encoding="utf-8") as f:
        ocr = json.load(f)

    risk_output = {}

    for filename, face_entries in faces.items():
        count = len(face_entries)
        gps_present = any(entry["gps"] for entry in gps if entry["file"] == filename)
        stego_flag = stego.get(filename, {}).get("lsb_suspicious", False)
        entropy = stego.get(filename, {}).get("entropy", 0)
        ocr_text = ocr.get(filename, "")

        score = 0
        if count > 3:
            score += 2
        if gps_present:
            score += 2
        if stego_flag:
            score += 3
        if entropy > 7.5:
            score += 2
        if len(ocr_text.strip()) > 0:
            score += 1

        if score >= 6:
            risk = "high"
        elif score >= 3:
            risk = "medium"
        else:
            risk = "low"

        risk_output[filename] = {
            "face_count": count,
            "gps_present": gps_present,
            "stego_flag": stego_flag,
            "entropy": entropy,
            "ocr_present": len(ocr_text.strip()) > 0,
            "risk_score": score,
            "risk_level": risk
        }

        log(f"Risk: {filename} → {risk}")

    out_path = os.path.join(batch, "face_risk.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(risk_output, f, indent=4)

    log("Face risk engine complete.")

if __name__ == "__main__":
    main()
