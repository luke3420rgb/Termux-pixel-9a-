#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime, UTC

HOME = "/data/data/com.termux/files/home"
BATCHES = os.path.join(HOME, "forensic-backend", "batches")
MEDIA = os.path.join(HOME, "forensic_media")
LOG = os.path.join(HOME, "downloads", "global_graph_engine.log")

def now():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(msg):
    line = f"[GRAPH {now()}] {msg}"
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def add_node(graph, node_id, node_type, data=None):
    graph["nodes"].append({
        "id": node_id,
        "type": node_type,
        "data": data or {}
    })

def add_edge(graph, src, dst, relation):
    graph["edges"].append({
        "source": src,
        "target": dst,
        "relation": relation
    })

def main():
    log("Starting global graph engine...")

    batches = sorted(os.listdir(BATCHES))
    if not batches:
        log("No batches found.")
        return

    latest = batches[-1]
    batch = os.path.join(BATCHES, latest)

    paths = {
        "entities": os.path.join(batch, "entity_fusion.json"),
        "risk": os.path.join(batch, "face_risk.json"),
        "network": os.path.join(MEDIA, "network_intel.json"),
        "vendors": os.path.join(MEDIA, "network_vendors.json"),
        "geoip": os.path.join(MEDIA, "network_geoip.json")
    }

    if not all(os.path.exists(p) for p in paths.values()):
        log("Missing required files.")
        return

    with open(paths["entities"], "r", encoding="utf-8") as f:
        entities = json.load(f)

    with open(paths["risk"], "r", encoding="utf-8") as f:
        risk = json.load(f)

    with open(paths["network"], "r", encoding="utf-8") as f:
        network = json.load(f)

    with open(paths["vendors"], "r", encoding="utf-8") as f:
        vendors = json.load(f)

    with open(paths["geoip"], "r", encoding="utf-8") as f:
        geoip = json.load(f)

    graph = {
        "generated_at_utc": now(),
        "nodes": [],
        "edges": []
    }

    # File nodes
    for filename, data in entities.items():
        add_node(graph, filename, "file", data)

        # Risk edge
        r = risk.get(filename, {})
        add_edge(graph, filename, f"risk_{filename}", "has_risk")
        add_node(graph, f"risk_{filename}", "risk", r)

    # Network nodes
    for conn in network.get("connections", []):
        local = conn.get("local")
        remote = conn.get("remote")

        if local:
            add_node(graph, local, "ip")
        if remote:
            add_node(graph, remote, "ip")

        if local and remote:
            add_edge(graph, local, remote, "connected_to")

    # Vendor nodes
    for entry in vendors.get("vendors", []):
        ip = entry.get("ip")
        vendor = entry.get("vendor")
        if ip:
            add_edge(graph, ip, vendor, "vendor")
            add_node(graph, vendor, "vendor")

    # GeoIP nodes
    for entry in geoip.get("ips", []):
        ip = entry.get("ip")
        country = entry.get("country")
        if ip and country:
            add_edge(graph, ip, country, "located_in")
            add_node(graph, country, "country")

    out_path = os.path.join(batch, "global_graph.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=4)

    log("Global graph engine complete.")

if __name__ == "__main__":
    main()
