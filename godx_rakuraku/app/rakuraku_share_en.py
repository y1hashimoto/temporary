#!/usr/bin/env python3
# ============================================================================
# rakuraku_share_en.py  --  "Rakuraku Data Share" English edition
#   GO DX Corporation (fictional vendor)
#
#   Run:
#     python3 rakuraku_share_en.py                 connect to a live FUXA
#     python3 rakuraku_share_en.py --demo          run with simulated values
#     python3 rakuraku_share_en.py --host 192.168.111.11:1881
#
#   NOTE: A fictional product for education & defensive training only.
# ============================================================================
import rakuraku_core

STRINGS_EN = {
    "title":     "Rakuraku Data Share — GO DX",
    "product":   "Rakuraku Data Share",
    "tagline":   "Operational data-sharing tool",
    "provided":  "provided by GO DX",
    "host":      "SCADA host:",
    "get":       "GET  Read current values",
    "demo_badge": "DEMO mode",
    "columns":   ("Factory", "Line", "Device", "Tag", "Value"),
    "rows": {
        "factory": "Factory A",
        "line":    "Line B",
        "device":  "Device C",
        "tags":    ("Temp Ctrl SV", "Temp Ctrl PV", "Temp Ctrl OUT"),
    },
    "ready":       "Ready. Press GET to read current values.",
    "reading":     "Reading…",
    "no_tags":     "Target tags not found",
    "status_ok":   "Read OK  {host}  @ {time}",
    "status_demo": "Showing demo values (cannot reach {host})  @ {time}",
}

if __name__ == "__main__":
    rakuraku_core.run(STRINGS_EN)
