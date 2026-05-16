#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
forensic_db.py

SQLite Evidence Database Module
- Imports master_log.jsonl
- Creates SQLite database
- Stores LAN, hotspot, watchdog events
- Provides query functions
"""

import os
import json
import sqlite3
import datetime

LOG_DIR = os.path.join(os.path.expanduser("~"), "forensic_net_logs")
MASTER_LOG = os.path.join(LOG_DIR, "master_log.jsonl")
DB_PATH = os.path.join(LOG_DIR, "forensic.db")


def ensure_db():
    os.makedirs(LOG_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        source TEXT,
        ip TEXT,
        mac TEXT,
        vendor TEXT,
        reachable TEXT,
        raw_json TEXT
    )
    """)

    conn.commit()
    conn.close()


def load_master_log():
    if not os.path.exists(MASTER_LOG):
        return []

    events = []
    with open(MASTER_LOG, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except:
                pass
    return events


def insert_events(events):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for e in events:
        cur.execute("""
        INSERT INTO events (timestamp, source, ip, mac, vendor, reachable, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            e.get("timestamp", ""),
            e.get("source", ""),
            e.get("ip", ""),
            e.get("mac", ""),
            e.get("vendor", ""),
            str(e.get("reachable", "")),
            json.dumps(e)
        ))

    conn.commit()
    conn.close()


def query_all():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT timestamp, source, ip, mac, vendor FROM events ORDER BY timestamp ASC")
    rows = cur.fetchall()
    conn.close()
    return rows


def query_by_ip(ip):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT timestamp, source, mac, vendor FROM events WHERE ip=? ORDER BY timestamp ASC", (ip,))
    rows = cur.fetchall()
    conn.close()
    return rows


def query_by_mac(mac):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT timestamp, source, ip, vendor FROM events WHERE mac=? ORDER BY timestamp ASC", (mac,))
    rows = cur.fetchall()
    conn.close()
    return rows


def main():
    ensure_db()
    events = load_master_log()
    insert_events(events)

    print("Imported events into forensic.db")
    print("Examples:")
    print("  python3 forensic_db.py all")
    print("  python3 forensic_db.py ip 192.168.1.153")
    print("  python3 forensic_db.py mac FC:DB:B3:AA:BB:CC")


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        main()
    else:
        ensure_db()
        if sys.argv[1] == "all":
            rows = query_all()
            for r in rows:
                print(r)
        elif sys.argv[1] == "ip" and len(sys.argv) == 3:
            rows = query_by_ip(sys.argv[2])
            for r in rows:
                print(r)
        elif sys.argv[1] == "mac" and len(sys.argv) == 3:
            rows = query_by_mac(sys.argv[2])
            for r in rows:
                print(r)
        else:
            print("Usage:")
            print("  python3 forensic_db.py all")
            print("  python3 forensic_db.py ip <IP>")
            print("  python3 forensic_db.py mac <MAC>")
