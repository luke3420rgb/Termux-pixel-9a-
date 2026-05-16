#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
global_export.py

Creates a unified export of all intelligence layers:
- entity fusion
- correlation
- risk dashboard
- narratives
- graph analytics
- global graph
- timeline
- gps fusion
- faces
- ocr
- exif

Outputs:
- global_export.json
"""

import os
import json

BASE = os.path.expanduser("~/forensic_media")

FILES = {
    "entity_fusion": "entity_fusion.json",
    "correlation": "intel_correlation.json",
    "risk_dashboard": "risk_dashboard.json",
    "narratives": "narrative.json",
    "graph_analytics": "graph_analytics.json",
    "global_graph": "global_graph.json",
    "timeline": "face_timeline.json",
    "gps_fusion": "face_gps_fusion.json",
    "faces": "faces_advanced.json",
    "ocr": "ocr_data.json",
    "exif": "exif_data.json"
}

OUT_JSON = os.path.join(BASE, "global_export.json")


def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    export = {}

    for key, filename in FILES.items():
        path = os.path.join(BASE, filename)
        export[key] = load_json(path)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=4)

    print("Global export complete →", OUT_JSON)


if __name__ == "__main__":
    main()
