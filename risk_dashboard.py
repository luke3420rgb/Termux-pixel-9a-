#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime, UTC

HOME = "/data/data/com.termux/files/home"
BATCHES = os.path.join(HOME, "forensic-backend", "batches")
LOG = os.path.join(HOME, "downloads", "risk_dashboard.log")

def now():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(msg):
    line = f"[RISK-DASH {now()}] {msg}"
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def main():
    log("Starting risk dashboard...")

    batches = sorted(os.listdir(BATCHES))
    if not batches:
        log("No batches found.")
        return

    latest = batches[-1]
    batch = os.path.join(BATCHES, latest)

    risk_path = os.path.join(batch, "face_risk.json")
    if not os.path.exists(risk_path):
        log("face_risk.json missing.")
        return

    with open(risk_path, "r", encoding="utf-8") as f:
        risk = json.load(f)

    dashboard = {
        "generated_at_utc": now(),
        "counts": {
            "high": 0,
            "medium": 0,
            "low": 0
        },
        "files": {
            "high": [],
            "medium": [],
            "low": []
        }
    }

    for filename, info in risk.items():
        level = info.get("risk_level", "low")
        dashboard["counts"][level] += 1
        dashboard["files"][level].append(filename)

    out_path = os.path.join(batch, "risk_dashboard.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, indent=4)

    log("Risk dashboard complete.")

if __name__ == "__main__":
    main()
