#!/usr/bin/env python3
import socket
import time
import datetime
import requests

TARGET_IP = "192.168.1.158"
TARGET_PORT = 8888
CHECK_INTERVAL = 10  # seconds
LOGFILE = "net_watchdog_192_168_1_158_8888.log"

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOGFILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def check_port():
    try:
        s = socket.create_connection((TARGET_IP, TARGET_PORT), timeout=3)
        s.close()
        return True
    except Exception:
        return False

def check_http():
    try:
        r = requests.get(f"http://{TARGET_IP}:{TARGET_PORT}", timeout=5)
        return r.status_code, len(r.content)
    except Exception:
        return None, None

if __name__ == "__main__":
    log("watchdog started")
    while True:
        port_ok = check_port()
        if port_ok:
            log("port open")
            status, size = check_http()
            if status is not None:
                log(f"http status={status} bytes={size}")
            else:
                log("http unreachable")
        else:
            log("port closed")
        time.sleep(CHECK_INTERVAL)
