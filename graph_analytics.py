#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime, UTC
from collections import defaultdict

HOME = "/data/data/com.termux/files/home"
BATCHES = os.path.join(HOME, "forensic-backend", "batches")
LOG = os.path.join(HOME, "downloads", "graph_analytics.log")

def now():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(msg):
    line = f"[GRAPH-ANALYTICS {now()}] {msg}"
    print(line)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def compute_degree_centrality(graph):
    degree = defaultdict(int)
    for edge in graph.get("edges", []):
        degree[edge["source"]] += 1
        degree[edge["target"]] += 1
    return dict(degree)

def compute_risk_propagation(graph, degree):
    risk_map = {}
    for node in graph.get("nodes", []):
        nid = node["id"]
        ntype = node["type"]
        data = node.get("data", {})

        base = 0
        if ntype == "risk":
            level = data.get("risk_level", "low")
            if level == "high":
                base = 3
            elif level == "medium":
                base = 2
            else:
                base = 1

        deg = degree.get(nid, 0)
        score = base + (deg * 0.5)

        risk_map[nid] = {
            "base_risk": base,
            "degree": deg,
            "propagated_risk": score
        }

    return risk_map

def main():
    log("Starting graph analytics...")

    batches = sorted(os.listdir(BATCHES))
    if not batches:
        log("No batches found.")
        return

    latest = batches[-1]
    batch = os.path.join(BATCHES, latest)

    graph_path = os.path.join(batch, "global_graph.json")
    if not os.path.exists(graph_path):
        log("global_graph.json missing.")
        return

    with open(graph_path, "r", encoding="utf-8") as f:
        graph = json.load(f)

    degree = compute_degree_centrality(graph)
    risk = compute_risk_propagation(graph, degree)

    analytics = {
        "generated_at_utc": now(),
        "node_count": len(graph.get("nodes", [])),
        "edge_count": len(graph.get("edges", [])),
        "degree_centrality": degree,
        "risk_propagation": risk
    }

    out_path = os.path.join(batch, "graph_analytics.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(analytics, f, indent=4)

    log("Graph analytics complete.")

if __name__ == "__main__":
    main()
