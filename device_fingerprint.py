#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
device_fingerprint.py

Device Fingerprinting Engine
- Reads forensic.db
- Groups events by MAC
- Infers device type from vendor + behavior
- Outputs fingerprint summary
"""

import os
import sqlite3
import datetime

LOG_DIR = os.path.join(os.path.expanduser("~"), "forensic_net_logs")
DB_PATH = os.path.join(LOG_DIR, "forensic.db")


VENDOR_MAP = {
    "Samsung": "Samsung Phone / Tablet / Watch",
    "Apple": "iPhone / iPad / Apple Watch",
    "Amazon": "Amazon Firestick / Echo / Tablet",
    "Google Pixel": "Google Pixel Phone",
    "Google/Nest": "Google Home / Nest Device",
    "ASUSTek": "Router / Repeater / AP",
    "Hon Hai": "iPhone OEM Device",
    "Murata": "Samsung/Apple OEM Device",
}


def infer_device_type(vendor: str, appearances: int, hotspot_hits: int, lan_hits: int) -> str:
    """
    Basic inference rules.
    """
    if vendor in VENDOR_MAP:
        base = VENDOR_MAP[vendor]
    else:
        base = "Unknown Device"

    # Behavioral inference
    if hotspot_hits > lan_hits:
        behavior = "Primarily Hotspot Device"
    elif lan_hits > hotspot_hits:
        behavior = "Primarily LAN Device"
    else:
        behavior = "Mixed Behavior"

    if appearances > 50:
        freq = "High Activity"
    elif appearances > 10:
        freq = "Moderate Activity"
    else:
        freq = "Low Activity"

    return f"{base} — {behavior}, {freq}"


def load_events():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT timestamp, source, ip, mac, vendor FROM events ORDER BY timestamp ASC")
    rows = cur.fetchall()
    conn.close()
    return rows


def fingerprint_devices():
    rows = load_events()

    devices = {}

    for ts, source, ip, mac, vendor in rows:
        if mac not in devices:
            devices[mac] = {
                "vendor": vendor,
                "events": 0,
                "lan": 0,
                "hotspot": 0,
                "watchdog": 0,
                "first_seen": ts,
                "last_seen": ts,
                "ips": set(),
            }

        d = devices[mac]
        d["events"] += 1
        d["last_seen"] = ts
        d["ips"].add(ip)

        if source == "lan":
            d["lan"] += 1
        elif source == "hotspot":
            d["hotspot"] += 1
        elif source == "watchdog":
            d["watchdog"] += 1

    return devices


def print_fingerprints(devices):
    for mac, info in devices.items():
        print("=" * 60)
        print(f"MAC: {mac}")
        print(f"Vendor: {info['vendor']}")
        print(f"First Seen: {info['first_seen']}")
        print(f"Last Seen:  {info['last_seen']}")
        print(f"Total Events: {info['events']}")
        print(f"LAN Hits: {info['lan']}")
        print(f"Hotspot Hits: {info['hotspot']}")
        print(f"Watchdog Hits: {info['watchdog']}")
        print(f"IPs Used: {', '.join(sorted(info['ips']))}")

        device_type = infer_device_type(
            info["vendor"],
            info["events"],
            info["hotspot"],
            info["lan"]
        )

        print(f"Fingerprint: {device_type}")
        print("")


def main():
    devices = fingerprint_devices()
    print_fingerprints(devices)


if __name__ == "__main__":
    main()
