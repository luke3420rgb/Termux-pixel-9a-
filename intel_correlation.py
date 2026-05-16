#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime, UTC

HOME = "/data/data/com.termux/files/home"
BATCHES = os.path.join(HOME, "forensic-backend", "batches")
MEDIA = os.path.join(HOME, "forensic_media")
LOG = os.path.join(HOME, "downloads", "intel_correlation.log")

def now():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(msg):
    line = f"[CORRELATION {now()}] {msg}"
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def main():
    log("Starting intelligence correlation...")

    batches = sorted(os.listdir(BATCHES))
    if not batches:
        log("No batches found.")
        return

    latest = batches[-1]
    batch = os.path.join(BATCHES, latest)

    paths = {
        "entities": os.path.join(batch, "entity_fusion.json"),
        "network": os.path.join(MEDIA, "network_intel.json"),
        "vendors": os.path.join(MEDIA, "network_vendors.json"),
        "geoip": os.path.join(MEDIA, "network_geoip.json")
    }

    if not all(os.path.exists(p) for p in paths.values()):
        log("Missing required intel files.")
        return

    with open(paths["entities"], "r", encoding="utf-8") as f:
        entities = json.load(f)

    with open(paths["network"], "r", encoding="utf-8") as f:
        network = json.load(f)

    with open(paths["vendors"], "r", encoding="utf-8") as f:
        vendors = json.load(f)

    with open(paths["geoip"], "r", encoding="utf-8") as f:
        geoip = json.load(f)

    correlation = {
        "generated_at_utc": now(),
        "entities": entities,
        "network": network,
        "vendors": vendors,
        "geoip": geoip
    }

    out_path = os.path.join(batch, "intel_correlation.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(correlation, f, indent=4)

    log("Intelligence correlation complete.")

if __name__ == "__main__":
    main()

