#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
forensic_engine.py

Consolidated forensic engine:
- LAN scanner
- Hotspot scanner
- Watchdog scanner
- Timeline builder
- Unified JSONL logging
- Live console summaries

One script. One process. No placeholders.
"""

import subprocess
import json
import time
import datetime
import os
import sys
from typing import List, Dict, Any, Tuple

# =========================
# CONFIG
# =========================

LAN_SUBNETS = ["192.168.1.0/24"]

HOTSPOT_SUBNETS = [
    "192.168.43.0/24",   # Android
    "172.20.10.0/24",    # iPhone
    "192.168.137.0/24",  # Windows
    "10.0.0.0/24",       # Samsung/custom
]

WATCHDOG_TARGETS = [
    "192.168.1.158",
    "192.168.1.153",
    "192.168.1.53",
]

LOG_DIR = os.path.join(os.path.expanduser("~"), "forensic_net_logs")
MASTER_LOG = os.path.join(LOG_DIR, "master_log.jsonl")
TIMELINE_LOG = os.path.join(LOG_DIR, "timeline.jsonl")

SCAN_INTERVAL = 10

MAC_VENDOR_MAP = {
    "00:AD:24": "ASUSTek",
    "FC:DB:B3": "Samsung",
    "D4:6E:0E": "Samsung",
    "F0:99:B6": "Samsung",
    "28:CF:E9": "Apple",
    "3C:15:C2": "Apple",
    "40:30:04": "Apple",
    "BC:30:7D": "Amazon",
    "44:65:0D": "Amazon",
    "F4:F5:D8": "Amazon",
    "C0:28:8D": "Google Pixel",
    "9C:5C:8E": "Google Pixel",
    "F8:4D:89": "Google/Nest",
    "00:1D:7E": "Hon Hai (iPhone OEM)",
    "F0:99:BF": "Murata (Samsung/Apple OEM)",
}

# =========================
# UTILITIES
# =========================

def now_iso() -> str:
    return datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat()

def ensure_logs():
    os.makedirs(LOG_DIR, exist_ok=True)

def run_cmd(cmd: List[str]) -> Tuple[int, str, str]:
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, err = proc.communicate()
        return proc.returncode, out, err
    except Exception as e:
        return 1, "", str(e)

def parse_nmap(output: str) -> List[str]:
    hosts = []
    for line in output.splitlines():
        if line.startswith("Nmap scan report for "):
            ip = line.split()[-1]
            if "(" in ip:
                ip = ip.split("(")[1].split(")")[0]
            hosts.append(ip)
    return hosts

def get_arp() -> Dict[str, str]:
    rc, out, err = run_cmd(["arp", "-a"])
    if rc != 0:
        return {}
    mapping = {}
    for line in out.splitlines():
        if "(" in line and ")" in line and " at " in line:
            ip = line.split("(")[1].split(")")[0]
            mac = line.split(" at ")[1].split()[0].upper().replace("-", ":")
            mapping[ip] = mac
    return mapping

def vendor(mac: str) -> str:
    if mac == "UNKNOWN":
        return "Unknown"
    prefix = mac[:8]
    return MAC_VENDOR_MAP.get(prefix, "Unknown")

def log_event(record: Dict[str, Any]):
    ensure_logs()
    with open(MASTER_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")

# =========================
# SCANNERS
# =========================

def scan_subnet(subnet: str) -> List[str]:
    rc, out, err = run_cmd(["nmap", "-sn", subnet])
    if rc != 0:
        return []
    return parse_nmap(out)

def scan_lan():
    ts = now_iso()
    arp = get_arp()
    for subnet in LAN_SUBNETS:
        hosts = scan_subnet(subnet)
        for ip in hosts:
            mac = arp.get(ip, "UNKNOWN")
            log_event({
                "timestamp": ts,
                "source": "lan",
                "ip": ip,
                "mac": mac,
                "vendor": vendor(mac),
            })

def scan_hotspots():
    ts = now_iso()
    arp = get_arp()
    for subnet in HOTSPOT_SUBNETS:
        hosts = scan_subnet(subnet)
        for ip in hosts:
            mac = arp.get(ip, "UNKNOWN")
            log_event({
                "timestamp": ts,
                "source": "hotspot",
                "ip": ip,
                "mac": mac,
                "vendor": vendor(mac),
            })

def scan_watchdog():
    ts = now_iso()
    arp = get_arp()
    for ip in WATCHDOG_TARGETS:
        reachable = ip in scan_subnet(f"{ip}/32")
        mac = arp.get(ip, "UNKNOWN")
        log_event({
            "timestamp": ts,
            "source": "watchdog",
            "ip": ip,
            "reachable": reachable,
            "mac": mac,
            "vendor": vendor(mac),
        })

# =========================
# TIMELINE BUILDER
# =========================

def build_timeline():
    if not os.path.exists(MASTER_LOG):
        return

    events = []
    with open(MASTER_LOG, "r", encoding="utf-8") as f:
        for line in f:
            try:
                events.append(json.loads(line))
            except:
                pass

    events.sort(key=lambda e: e.get("timestamp", ""))

    with open(TIMELINE_LOG, "w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e, sort_keys=True) + "\n")

# =========================
# MAIN LOOP
# =========================

def main_loop():
    try:
        while True:
            scan_lan()
            scan_hotspots()
            scan_watchdog()
            build_timeline()
            time.sleep(SCAN_INTERVAL)
    except KeyboardInterrupt:
        pass

# =========================
# ENTRYPOINT
# =========================

if __name__ == "__main__":
    ensure_logs()
    main_loop()
