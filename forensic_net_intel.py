#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
forensic_net_intel.py

Unified network intelligence module:
- Continuous LAN scanner (192.168.1.0/24)
- Hotspot range scanner (Android, iOS, Windows, Samsung-style)
- Simple watchdog for specific targets
- MAC vendor fingerprinting
- JSONL evidence logging with timestamps
"""

import subprocess
import json
import time
import datetime
import os
import sys
from typing import List, Dict, Tuple

# =========================
# Config
# =========================

LAN_SUBNETS = [
    "192.168.1.0/24",
]

HOTSPOT_SUBNETS = [
    "192.168.43.0/24",   # Android hotspot
    "172.20.10.0/24",    # iPhone hotspot
    "192.168.137.0/24",  # Windows hotspot
    "10.0.0.0/24",       # Some Samsung/custom hotspots
]

WATCHDOG_TARGETS = [
    "192.168.1.158",
    "192.168.1.153",
    "192.168.1.53",
]

LOG_DIR = os.path.join(os.path.expanduser("~"), "forensic_net_logs")
LAN_LOG = os.path.join(LOG_DIR, "lan_scan.jsonl")
HOTSPOT_LOG = os.path.join(LOG_DIR, "hotspot_scan.jsonl")
WATCHDOG_LOG = os.path.join(LOG_DIR, "watchdog.jsonl")

SCAN_INTERVAL_SECONDS = 10

# =========================
# MAC vendor fingerprinting
# =========================

MAC_VENDOR_MAP = {
    "00:AD:24": "ASUSTek Computer Inc.",
    "FC:DB:B3": "Samsung Electronics",
    "D4:6E:0E": "Samsung Electronics",
    "F0:99:B6": "Samsung Electronics",
    "28:CF:E9": "Apple, Inc.",
    "3C:15:C2": "Apple, Inc.",
    "40:30:04": "Apple, Inc.",
    "BC:30:7D": "Amazon Technologies Inc.",
    "44:65:0D": "Amazon Technologies Inc.",
    "F4:F5:D8": "Amazon Technologies Inc.",
    "C0:28:8D": "Google / Pixel",
    "9C:5C:8E": "Google / Pixel",
    "F8:4D:89": "Google / Nest / Chromecast",
    "00:1D:7E": "Hon Hai Precision (iPhone OEM)",
    "F0:99:BF": "Murata Manufacturing (Samsung/Apple OEM)",
}

# =========================
# Utility
# =========================

def normalize_mac(mac: str) -> str:
    mac = mac.strip().upper().replace("-", ":")
    return mac

def mac_vendor(mac: str) -> str:
    mac = normalize_mac(mac)
    if len(mac) < 8:
        return "Unknown"
    prefix = mac[:8]
    return MAC_VENDOR_MAP.get(prefix, "Unknown")

def now_iso() -> str:
    return datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat()

def ensure_log_dir() -> None:
    os.makedirs(LOG_DIR, exist_ok=True)

def run_cmd(cmd: List[str]) -> Tuple[int, str, str]:
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        out, err = proc.communicate()
        return proc.returncode, out, err
    except Exception as e:
        return 1, "", str(e)

def parse_nmap_ping_scan(output: str) -> List[str]:
    hosts = []
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("Nmap scan report for "):
            ip = line.split()[-1]
            if "(" in ip and ")" in ip:
                ip = ip.split("(")[1].split(")")[0]
            hosts.append(ip)
    return hosts

def get_arp_table() -> Dict[str, str]:
    rc, out, err = run_cmd(["arp", "-a"])
    if rc != 0:
        return {}
    mapping = {}
    for line in out.splitlines():
        line = line.strip()
        if "(" in line and ")" in line and " at " in line:
            try:
                ip = line.split("(")[1].split(")")[0]
                mac = line.split(" at ")[1].split()[0]
                mapping[ip] = normalize_mac(mac)
            except Exception:
                continue
    return mapping

def log_json(path: str, record: Dict) -> None:
    ensure_log_dir()
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")

# =========================
# LAN scanner
# =========================

def scan_subnet(subnet: str) -> List[str]:
    rc, out, err = run_cmd(["nmap", "-sn", subnet])
    if rc != 0:
        return []
    return parse_nmap_ping_scan(out)

def lan_scan_once() -> None:
    timestamp = now_iso()
    arp_map = get_arp_table()
    for subnet in LAN_SUBNETS:
        hosts = scan_subnet(subnet)
        for ip in hosts:
            mac = arp_map.get(ip, "UNKNOWN")
            vendor = mac_vendor(mac)
            log_json(LAN_LOG, {
                "type": "lan_scan",
                "timestamp": timestamp,
                "subnet": subnet,
                "ip": ip,
                "mac": mac,
                "vendor": vendor,
            })

def lan_scan_loop() -> None:
    try:
        while True:
            lan_scan_once()
            time.sleep(SCAN_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        pass

# =========================
# Hotspot scanner
# =========================

def hotspot_scan_once() -> None:
    timestamp = now_iso()
    arp_map = get_arp_table()
    for subnet in HOTSPOT_SUBNETS:
        hosts = scan_subnet(subnet)
        for ip in hosts:
            mac = arp_map.get(ip, "UNKNOWN")
            vendor = mac_vendor(mac)
            log_json(HOTSPOT_LOG, {
                "type": "hotspot_scan",
                "timestamp": timestamp,
                "subnet": subnet,
                "ip": ip,
                "mac": mac,
                "vendor": vendor,
            })

def hotspot_scan_loop() -> None:
    try:
        while True:
            hotspot_scan_once()
            time.sleep(SCAN_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        pass

# =========================
# Watchdog
# =========================

def check_port(ip: str, port: int) -> bool:
    rc, out, err = run_cmd(["nc", "-vz", "-w", "2", ip, str(port)])
    return rc == 0

def watchdog_once() -> None:
    timestamp = now_iso()
    arp_map = get_arp_table()
    for ip in WATCHDOG_TARGETS:
        reachable = ip in scan_subnet(f"{ip}/32")
        mac = arp_map.get(ip, "UNKNOWN")
        vendor = mac_vendor(mac)
        ports = {}
        for p in [80, 443, 8888]:
            if reachable and check_port(ip, p):
                state = "open"
            elif reachable:
                state = "closed_or_filtered"
            else:
                state = "unreachable"
            ports[str(p)] = state
        log_json(WATCHDOG_LOG, {
            "type": "watchdog",
            "timestamp": timestamp,
            "ip": ip,
            "reachable": reachable,
            "mac": mac,
            "vendor": vendor,
            "ports": ports,
        })

def watchdog_loop() -> None:
    try:
        while True:
            watchdog_once()
            time.sleep(SCAN_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        pass

# =========================
# CLI
# =========================

def print_usage() -> None:
    print("forensic_net_intel.py")
    print("")
    print("Modes:")
    print("  lan_once")
    print("  lan_loop")
    print("  hotspot_once")
    print("  hotspot_loop")
    print("  watchdog_once")
    print("  watchdog_loop")

def main() -> None:
    ensure_log_dir()
    if len(sys.argv) < 2:
        print_usage()
        return
    mode = sys.argv[1].strip().lower()
    if mode == "lan_once":
        lan_scan_once()
    elif mode == "lan_loop":
        lan_scan_loop()
    elif mode == "hotspot_once":
        hotspot_scan_once()
    elif mode == "hotspot_loop":
        hotspot_scan_loop()
    elif mode == "watchdog_once":
        watchdog_once()
    elif mode == "watchdog_loop":
        watchdog_loop()
    else:
        print_usage()

if __name__ == "__main__":
    main()
