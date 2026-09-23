#!/usr/bin/env python3
"""Demo DC rack — a 42U cabinet exercising every roadmap feature.

Two modes:

  emit   (default)  Write demo-rack-dc.Rackula.zip — import it from a rack's
                    "Import from Rackula" dialog. Covers what the layout
                    format can express: faces, carriers (V2B), device types
                    with manufacturer/model/colour (V2C image library slugs).

  apply           Drive a running IpamBox API end-to-end — creates the site,
                    group, rack, imports the same layout (through the real
                    /devices/import endpoint), then adds what a zip cannot
                    carry: interface port generation, patch-panel front/rear
                    pairs, cables (data/uplink/console/power), IP→interface
                    links, watts/weight for the V2.5 capacity rollups, and a
                    legacy switch_name/switch_port match-free-text demo.

Usage:

    python3 examples/demo_rack_dc.py                     # write the zip
    python3 examples/demo_rack_dc.py apply \
        --api http://localhost:3010 --user admin         # populate a live app

Env fallbacks: IPAMBOX_API, IPAMBOX_USER, IPAMBOX_PASS. All values are
fictional; nothing references a real network.
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
import ssl
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ZIP_NAME = "demo-rack-dc.Rackula.zip"
RACK_NAME = "Demo DC Rack — Cabling"
SITE_NAME = "Demo DC"
GROUP_NAME = "Demo DC Row A"
PREFIX = "10.200.0.0/24"

UNITS_PER_U = 6  # Rackula >=0.7 position format: position = U * 6
# Fixed timestamps so the zip is byte-identical across runs (same convention
# as generate_demo_data.py's fixed workbook timestamps).
ZIP_DATE = (2020, 1, 1, 0, 0, 0)


# ---------------------------------------------------------------- layout --
# Device types — slugs are the V2C image-library identifiers where they exist
# (front/rear images show on the elevation); a couple are plain Generic defs.
# watts/weight_kg feed the V2.5 capacity rollups on apply (the zip format has
# no fields for them).

DEVICE_TYPES = {
    # slug: (u_height, manufacturer, model, colour, category, watts, kg, slots)
    "eaton-9px3000irt2u": (2, "Eaton", "9PX3000iRT2U", "#818cf8", "power", 3000, 28.0, None),
    "apc-ap4423a": (1, "APC", "AP4423A ATS", "#a78bfa", "power", None, 3.74, None),
    "blank-1u": (1, "Generic", "1U Blank", "#64748b", "blank", None, None, None),
    "generic-blanking-panel-2u": (2, "Generic", "Blanking Panel 2U", "#64748b", "blank", None, 0.3, None),
    "brush-1u": (1, "Generic", "1U Brush Strip", "#94a3b8", "cable-management", None, None, None),
    "generic-cable-management-panel-1u": (1, "Generic", "Cable Management Panel 1U", "#94a3b8", "cable-management", None, None, None),
    "dell-poweredge-r750": (2, "Dell", "PowerEdge R750", "#0ea5e9", "server", 750, 27.7, None),
    "dell-poweredge-r650": (1, "Dell", "PowerEdge R650", "#38bdf8", "server", 600, 21.0, None),
    "dell-powervault-me4024": (2, "Dell", "PowerVault ME4024", "#22d3ee", "storage", 580, 24.0, None),
    "carrier-dual": (1, "Generic", "1U Half-Width Dual Shelf", "#cbd5e1", "carrier", None, None, "halves"),
    "edge-node-half": (1, "Generic", "Half-Width Edge Appliance", "#f97316", "network", 45, 2.2, None),
    "generic-24-port-copper-patch-panel": (1, "Generic", "24-port Copper Patch Panel", "#fbbf24", "patch-panel", None, 0.9, None),
    "generic-24-port-copper-patch-panel-half-depth": (1, "Generic", "24-port Copper Patch Panel Half Depth", "#f59e0b", "patch-panel", None, 0.7, None),
    "cisco-c9300-48p": (1, "Cisco", "Catalyst 9300-48P", "#10b981", "network", 350, 7.59, None),
    "cisco-c9300-24t": (1, "Cisco", "Catalyst 9300-24T", "#34d399", "network", 120, 7.4, None),
    "fortinet-fg-100f": (1, "Fortinet", "FortiGate 100F", "#f43f5e", "firewall", 39, 3.0, None),
    "cisco-asr-9001": (2, "Cisco", "ASR 9001", "#059669", "network", 480, 16.5, None),
    "apc-smt1500rmi2uc": (2, "APC", "SMT1500RMI2UC", "#818cf8", "power", 3600, 38.24, None),
    "apc-smt2200rm2u": (2, "APC", "SMT2200RM2U", "#818cf8", "power", None, 42.3, None),
    "dell-powerswitch-s5248f-on": (1, "Dell", "PowerSwitch S5248F-ON", "#10b981", "network", 647, 8.9, None),
    "generic-lc-24-port-fiber-patch-panel": (1, "Generic", "LC-24-port Fiber Patch Panel", "#f59e0b", "patch-panel", None, None, None),
    "kvm-console": (1, "Generic", "1U LCD Console", "#e2e8f0", "kvm", 60, 4.0, None),
    "eaton-tripp-lite-b096-016": (1, "Eaton", "Tripp Lite B096-016 Console Server", "#8b5cf6", "network", 30, 4.99, None),
    "shelf-1u": (1, "Generic", "1U Cantilever Shelf", "#cbd5e1", "shelf", None, 2.0, None),
}

# name, type slug, u (bottom U), face, notes; carrier children carry
# (carrier=<name>, slot=<idx>) instead of u/face.
DEVICES = [
    ("ups-01",        "eaton-9px3000irt2u", 1,  "front", "feeds the whole rack"),
    ("pdu-a",         "apc-ap4423a",        1,  "rear",  "A feed"),
    ("pdu-b",         "apc-ap4423a",        2,  "rear",  "B feed"),
    ("blank-u3",      "blank-1u",           3,  "front", None),
    ("blank-u4",      "blank-1u",           4,  "front", None),
    ("brush-u5",      "brush-1u",           5,  "front", None),
    ("srv-esxi-01",   "dell-poweredge-r750", 6, "front", "vSphere host 1"),
    ("srv-esxi-02",   "dell-poweredge-r750", 8, "front", "vSphere host 2"),
    ("srv-backup-01", "dell-poweredge-r650", 10, "front", "backup target"),
    ("san-01",        "dell-powervault-me4024", 11, "front", "iSCSI SAN"),
    ("blank-u13",     "blank-1u",           13, "front", None),
    ("tray-edge-01",  "carrier-dual",       14, "front", "half-width pair"),
    ("edge-sdwan-a",  "edge-node-half",     None, None,  {"carrier": "tray-edge-01", "slot": 0}),
    ("edge-sdwan-b",  "edge-node-half",     None, None,  {"carrier": "tray-edge-01", "slot": 1}),
    ("pp-a-24",       "generic-24-port-copper-patch-panel", 15, "front", "Cat6 → sw-access-01"),
    ("cm-bar-15",     "generic-cable-management-panel-1u", 15, "rear", None),
    ("pp-b-24",       "generic-24-port-copper-patch-panel-half-depth", 16, "front", "Cat6A → sw-access-02"),
    ("cm-bar-16",     "generic-cable-management-panel-1u", 16, "rear", None),
    ("brush-u17",     "brush-1u",           17, "front", None),
    ("sw-access-01",  "cisco-c9300-48p",    18, "front", "access A"),
    ("sw-access-02",  "cisco-c9300-48p",    19, "front", "access B"),
    ("sw-mgmt-01",    "cisco-c9300-24t",    20, "front", "OOB management"),
    ("fw-edge-01",    "fortinet-fg-100f",   21, "front", "edge firewall"),
    ("rtr-wan-01",    "cisco-asr-9001",     22, "front", "WAN edge router"),
    ("kvm-01",        "kvm-console",        24, "front", None),
    ("con-srv-01",    "eaton-tripp-lite-b096-016", 25, "front", "serial console"),
    ("shelf-u26",     "shelf-1u",           26, "front", None),
    ("srv-app-01",    "dell-poweredge-r650", 27, "front", "app node"),
    ("srv-app-02",    "dell-poweredge-r650", 28, "front", "app node"),
    ("blank-u29-30",  "generic-blanking-panel-2u", 29, "front", None),
    ("blank-u31-32",  "generic-blanking-panel-2u", 31, "front", None),
    ("blank-u33-34",  "generic-blanking-panel-2u", 33, "front", None),
    ("blank-u35-36",  "generic-blanking-panel-2u", 35, "front", None),
    ("blank-u37-38",  "generic-blanking-panel-2u", 37, "front", None),
    ("blank-u39-40",  "generic-blanking-panel-2u", 39, "front", None),
    ("blank-u41-42",  "generic-blanking-panel-2u", 41, "front", None),
]

# ----------------------------------------------------------- port factory --
# device name -> generate bodies, run in order.
PORTS = {
    "pp-a-24": [dict(kind="patch", prefix="p", count=24, pair_prefix="b")],
    "pp-b-24": [dict(kind="patch", prefix="p", count=24, pair_prefix="b")],
    "sw-access-01": [
        dict(kind="rj45", prefix="Gi1/0/", count=48, speed_mbps=1000),
        dict(kind="sfp28", prefix="Te1/1/", count=4, speed_mbps=25000),
        dict(kind="console", prefix="con", count=1, start_index=0),
        dict(kind="power", prefix="psu", count=2),
    ],
    "sw-access-02": [
        dict(kind="rj45", prefix="Gi1/0/", count=48, speed_mbps=1000),
        dict(kind="sfp28", prefix="Te1/1/", count=4, speed_mbps=25000),
        dict(kind="console", prefix="con", count=1, start_index=0),
        dict(kind="power", prefix="psu", count=2),
    ],
    "sw-mgmt-01": [
        dict(kind="rj45", prefix="Gi1/0/", count=24, speed_mbps=1000),
        dict(kind="sfp", prefix="Te1/1/", count=4, speed_mbps=10000),
        dict(kind="console", prefix="con", count=1, start_index=0),
        dict(kind="power", prefix="psu", count=1),
    ],
    "fw-edge-01": [
        dict(kind="rj45", prefix="port", count=8, speed_mbps=1000),
        dict(kind="console", prefix="con", count=1, start_index=0),
        dict(kind="power", prefix="psu", count=1),
    ],
    "rtr-wan-01": [
        dict(kind="rj45", prefix="Gi0/0/0/", count=4, start_index=0, speed_mbps=1000),
        dict(kind="sfp", prefix="Te0/0/0/", count=4, start_index=0, speed_mbps=10000),
        dict(kind="console", prefix="con", count=1, start_index=0),
        dict(kind="power", prefix="psu", count=2),
    ],
    "con-srv-01": [
        dict(kind="console", prefix="port", count=16),
        dict(kind="rj45", prefix="eth", count=1),
        dict(kind="power", prefix="psu", count=1),
    ],
    "kvm-01": [
        dict(kind="rj45", prefix="ip", count=1),
        dict(kind="power", prefix="psu", count=1),
    ],
    "pdu-a": [
        dict(kind="power", prefix="o", count=8),
        dict(kind="power", prefix="in", count=1),
        dict(kind="rj45", prefix="net", count=1),
    ],
    "pdu-b": [
        dict(kind="power", prefix="o", count=8),
        dict(kind="power", prefix="in", count=1),
        dict(kind="rj45", prefix="net", count=1),
    ],
    "ups-01": [
        dict(kind="power", prefix="out", count=4),
        dict(kind="rj45", prefix="net", count=1),
    ],
    "edge-sdwan-a": [
        dict(kind="rj45", prefix="ge", count=4, start_index=0),
        dict(kind="power", prefix="psu", count=1),
    ],
    "edge-sdwan-b": [
        dict(kind="rj45", prefix="ge", count=4, start_index=0),
        dict(kind="power", prefix="psu", count=1),
    ],
}
_SERVER_PORTS = [
    dict(kind="rj45", prefix="eno", count=2, speed_mbps=10000),
    dict(kind="rj45", prefix="idrac", count=1),
    dict(kind="console", prefix="serial", count=1),
    dict(kind="power", prefix="psu", count=2),
]
for _s in ("srv-esxi-01", "srv-esxi-02", "srv-backup-01", "srv-app-01", "srv-app-02"):
    PORTS[_s] = list(_SERVER_PORTS)
PORTS["san-01"] = [
    dict(kind="rj45", prefix="mgmt", count=2, start_index=0),
    dict(kind="sfp28", prefix="iscsi", count=2, speed_mbps=25000),
    dict(kind="power", prefix="psu", count=2),
]

# ----------------------------------------------------------------- cables --
# (a_dev, a_port, b_dev, b_port, kind, color, label, length_m)
CABLES = [
    # front-of-panel drops: server NIC -> patch front
    ("srv-esxi-01", "eno1", "pp-a-24", "p1", "cat6", "blue", None, 1.0),
    ("srv-esxi-01", "eno2", "pp-b-24", "p1", "cat6a", "yellow", None, 1.0),
    ("srv-esxi-02", "eno1", "pp-a-24", "p2", "cat6", "blue", None, 1.0),
    ("srv-esxi-02", "eno2", "pp-b-24", "p2", "cat6a", "yellow", None, 1.0),
    ("srv-backup-01", "eno1", "pp-a-24", "p3", "cat6", "blue", None, 1.5),
    ("srv-backup-01", "eno2", "pp-b-24", "p3", "cat6a", "yellow", None, 1.5),
    ("srv-app-01", "eno1", "pp-a-24", "p4", "cat6", "blue", None, 1.0),
    ("srv-app-01", "eno2", "pp-b-24", "p4", "cat6a", "yellow", None, 1.0),
    ("srv-app-02", "eno1", "pp-a-24", "p5", "cat6", "blue", None, 1.0),
    ("srv-app-02", "eno2", "pp-b-24", "p5", "cat6a", "yellow", None, 1.0),
    ("san-01", "mgmt0", "pp-a-24", "p6", "cat6", "blue", None, 1.0),
    ("edge-sdwan-a", "ge1", "pp-a-24", "p7", "cat6", "green", None, 0.5),
    ("edge-sdwan-b", "ge1", "pp-a-24", "p8", "cat6", "green", None, 0.5),
    ("kvm-01", "ip1", "pp-a-24", "p9", "cat6", "blue", None, 1.5),
    ("con-srv-01", "eth1", "pp-a-24", "p10", "cat6", "blue", None, 1.0),
    ("fw-edge-01", "port2", "pp-a-24", "p11", "cat6a", "red", "fw inside leg", 1.0),
    # panel rear -> switch (the cross-connect side)
    ("pp-a-24", "b1", "sw-access-01", "Gi1/0/1", "cat6", "blue", None, 0.5),
    ("pp-a-24", "b2", "sw-access-01", "Gi1/0/2", "cat6", "blue", None, 0.5),
    ("pp-a-24", "b3", "sw-access-01", "Gi1/0/3", "cat6", "blue", None, 0.5),
    ("pp-a-24", "b4", "sw-access-01", "Gi1/0/4", "cat6", "blue", None, 0.5),
    ("pp-a-24", "b5", "sw-access-01", "Gi1/0/5", "cat6", "blue", None, 0.5),
    ("pp-a-24", "b6", "sw-access-01", "Gi1/0/6", "cat6", "blue", None, 0.5),
    ("pp-a-24", "b7", "sw-access-01", "Gi1/0/7", "cat6", "blue", None, 0.5),
    ("pp-a-24", "b8", "sw-access-01", "Gi1/0/8", "cat6", "blue", None, 0.5),
    ("pp-a-24", "b9", "sw-access-01", "Gi1/0/9", "cat6", "blue", None, 0.5),
    ("pp-a-24", "b10", "sw-access-01", "Gi1/0/10", "cat6", "blue", None, 0.5),
    ("pp-a-24", "b11", "sw-access-01", "Gi1/0/11", "cat6", "blue", None, 0.5),
    ("pp-b-24", "b1", "sw-access-02", "Gi1/0/1", "cat6a", "yellow", None, 0.5),
    ("pp-b-24", "b2", "sw-access-02", "Gi1/0/2", "cat6a", "yellow", None, 0.5),
    ("pp-b-24", "b3", "sw-access-02", "Gi1/0/3", "cat6a", "yellow", None, 0.5),
    ("pp-b-24", "b4", "sw-access-02", "Gi1/0/4", "cat6a", "yellow", None, 0.5),
    ("pp-b-24", "b5", "sw-access-02", "Gi1/0/5", "cat6a", "yellow", None, 0.5),
    # uplinks + WAN edge
    ("sw-access-01", "Te1/1/1", "fw-edge-01", "port3", "dac", "red", "access-A uplink", 0.5),
    ("sw-access-02", "Te1/1/1", "fw-edge-01", "port4", "dac", "red", "access-B uplink", 0.5),
    ("fw-edge-01", "port1", "rtr-wan-01", "Gi0/0/0/0", "cat6a", "orange", "WAN handoff", 0.5),
    ("sw-mgmt-01", "Te1/1/1", "sw-access-01", "Te1/1/4", "dac", "white", "OOB uplink", 0.5),
    # iSCSI storage on the 25G fabric
    ("san-01", "iscsi1", "sw-access-01", "Te1/1/2", "fiber_mm", "aqua", None, 1.0),
    ("san-01", "iscsi2", "sw-access-02", "Te1/1/2", "fiber_mm", "aqua", None, 1.0),
    # OOB management: iDRAC / mgmt NICs -> sw-mgmt
    ("srv-esxi-01", "idrac1", "sw-mgmt-01", "Gi1/0/1", "cat5e", "grey", None, 1.0),
    ("srv-esxi-02", "idrac1", "sw-mgmt-01", "Gi1/0/2", "cat5e", "grey", None, 1.0),
    ("srv-backup-01", "idrac1", "sw-mgmt-01", "Gi1/0/3", "cat5e", "grey", None, 1.0),
    ("srv-app-01", "idrac1", "sw-mgmt-01", "Gi1/0/4", "cat5e", "grey", None, 1.0),
    ("srv-app-02", "idrac1", "sw-mgmt-01", "Gi1/0/5", "cat5e", "grey", None, 1.0),
    ("san-01", "mgmt1", "sw-mgmt-01", "Gi1/0/6", "cat5e", "grey", None, 1.0),
    ("pdu-a", "net1", "sw-mgmt-01", "Gi1/0/7", "cat5e", "grey", None, 1.5),
    ("pdu-b", "net1", "sw-mgmt-01", "Gi1/0/8", "cat5e", "grey", None, 1.5),
    ("ups-01", "net1", "sw-mgmt-01", "Gi1/0/9", "cat5e", "grey", None, 2.0),
    # serial consoles -> console server
    ("sw-access-01", "con0", "con-srv-01", "port1", "console", "purple", None, 0.5),
    ("sw-access-02", "con0", "con-srv-01", "port2", "console", "purple", None, 0.5),
    ("sw-mgmt-01", "con0", "con-srv-01", "port3", "console", "purple", None, 0.5),
    ("fw-edge-01", "con0", "con-srv-01", "port4", "console", "purple", None, 0.5),
    ("rtr-wan-01", "con0", "con-srv-01", "port5", "console", "purple", None, 0.5),
    ("srv-esxi-01", "serial1", "con-srv-01", "port6", "console", "purple", None, 1.0),
    ("srv-esxi-02", "serial1", "con-srv-01", "port7", "console", "purple", None, 1.0),
    # power feeds — A red / B blue; ups feeds both PDUs then fw+rtr direct
    ("pdu-a", "in1", "ups-01", "out1", "power", "black", "A feed", 0.5),
    ("pdu-b", "in1", "ups-01", "out2", "power", "black", "B feed", 0.5),
    ("srv-esxi-01", "psu1", "pdu-a", "o1", "power", "red", None, 1.0),
    ("srv-esxi-01", "psu2", "pdu-b", "o1", "power", "blue", None, 1.0),
    ("srv-esxi-02", "psu1", "pdu-a", "o2", "power", "red", None, 1.0),
    ("srv-esxi-02", "psu2", "pdu-b", "o2", "power", "blue", None, 1.0),
    ("srv-backup-01", "psu1", "pdu-a", "o3", "power", "red", None, 1.0),
    ("srv-backup-01", "psu2", "pdu-b", "o3", "power", "blue", None, 1.0),
    ("srv-app-01", "psu1", "pdu-a", "o4", "power", "red", None, 1.0),
    ("srv-app-01", "psu2", "pdu-b", "o4", "power", "blue", None, 1.0),
    ("srv-app-02", "psu1", "pdu-a", "o5", "power", "red", None, 1.0),
    ("srv-app-02", "psu2", "pdu-b", "o5", "power", "blue", None, 1.0),
    ("san-01", "psu1", "pdu-a", "o6", "power", "red", None, 1.0),
    ("san-01", "psu2", "pdu-b", "o6", "power", "blue", None, 1.0),
    ("sw-access-01", "psu1", "pdu-a", "o7", "power", "red", None, 1.0),
    ("sw-access-01", "psu2", "pdu-b", "o7", "power", "blue", None, 1.0),
    ("sw-access-02", "psu1", "pdu-a", "o8", "power", "red", None, 1.0),
    ("sw-access-02", "psu2", "pdu-b", "o8", "power", "blue", None, 1.0),
    ("fw-edge-01", "psu1", "ups-01", "out3", "power", "red", None, 1.5),
    ("rtr-wan-01", "psu1", "ups-01", "out4", "power", "red", None, 1.5),
]

# ------------------------------------------------- rack B: compute row -----
DEVICES_B = [
    ("ups-b1",        "apc-smt1500rmi2uc",  1,  "front", "row UPS B"),
    ("pdu-c1",        "apc-ap4423a",        1,  "rear",  "C feed"),
    ("pdu-c2",        "apc-ap4423a",        2,  "rear",  "D feed"),
    ("blank-b3",      "blank-1u",           3,  "front", None),
    ("blank-b4",      "blank-1u",           4,  "front", None),
    ("brush-b5",      "brush-1u",           5,  "front", None),
    *[("srv-compute-%02d" % i, "dell-poweredge-r650", 5 + i, "front", "k8s node")
      for i in range(1, 9)],                       # U6..U13
    ("blank-b14",     "blank-1u",           14, "front", None),
    ("pp-c-24",       "generic-24-port-copper-patch-panel-half-depth", 15, "front", "Cat6 → tor-b-01"),
    ("cm-bar-b15",    "generic-cable-management-panel-1u", 15, "rear", None),
    ("brush-b16",     "brush-1u",           16, "front", None),
    ("tor-b-01",      "cisco-c9300-48p",    17, "front", "top-of-rack"),
    *[("blank-b%d-%d" % (u, u + 1), "generic-blanking-panel-2u", u, "front", None)
      for u in range(18, 41, 2)],                  # U18..U41
    ("blank-b42",     "blank-1u",           42, "front", None),
]

PORTS_B = {
    "pp-c-24": [dict(kind="patch", prefix="p", count=24, pair_prefix="b")],
    "tor-b-01": [
        dict(kind="rj45", prefix="Gi1/0/", count=48, speed_mbps=1000),
        dict(kind="sfp28", prefix="Te1/1/", count=4, speed_mbps=25000),
        dict(kind="console", prefix="con", count=1, start_index=0),
        dict(kind="power", prefix="psu", count=2),
    ],
    "pdu-c1": [
        dict(kind="power", prefix="o", count=8),
        dict(kind="power", prefix="in", count=1),
        dict(kind="rj45", prefix="net", count=1),
    ],
    "pdu-c2": [
        dict(kind="power", prefix="o", count=8),
        dict(kind="power", prefix="in", count=1),
        dict(kind="rj45", prefix="net", count=1),
    ],
    "ups-b1": [
        dict(kind="power", prefix="out", count=4),
        dict(kind="rj45", prefix="net", count=1),
    ],
}
for i in range(1, 9):
    PORTS_B["srv-compute-%02d" % i] = list(_SERVER_PORTS)

CABLES_B = [
    # compute node data + OOB drops through the panel to the ToR
    *[("srv-compute-%02d" % i, "eno1", "pp-c-24", "p%d" % i, "cat6", "blue", None, 1.0)
      for i in range(1, 9)],
    *[("srv-compute-%02d" % i, "idrac1", "pp-c-24", "p%d" % (i + 8), "cat6", "grey", None, 1.0)
      for i in range(1, 9)],
    *[("pp-c-24", "b%d" % i, "tor-b-01", "Gi1/0/%d" % i, "cat6", "blue", None, 0.5)
      for i in range(1, 9)],
    *[("pp-c-24", "b%d" % (i + 8), "tor-b-01", "Gi1/0/%d" % (i + 8), "cat6", "grey", None, 0.5)
      for i in range(1, 9)],
    # PDU inlets + node power (A red / B blue); ToR rides the UPS directly
    ("pdu-c1", "in1", "ups-b1", "out1", "power", "black", "C feed", 0.5),
    ("pdu-c2", "in1", "ups-b1", "out2", "power", "black", "D feed", 0.5),
    *[("srv-compute-%02d" % i, "psu1", "pdu-c1", "o%d" % i, "power", "red", None, 1.0)
      for i in range(1, 9)],
    *[("srv-compute-%02d" % i, "psu2", "pdu-c2", "o%d" % i, "power", "blue", None, 1.0)
      for i in range(1, 9)],
    ("tor-b-01", "psu1", "ups-b1", "out3", "power", "red", None, 1.0),
    ("tor-b-01", "psu2", "ups-b1", "out4", "power", "blue", None, 1.0),
]

# ------------------------------------------------- rack C: edge / MDA ------
DEVICES_C = [
    ("ups-c1",        "apc-smt2200rm2u",    1,  "front", "edge UPS"),
    ("pdu-d1",        "apc-ap4423a",        1,  "rear",  "E feed"),
    ("pdu-d2",        "apc-ap4423a",        2,  "rear",  "F feed"),
    ("blank-c3",      "blank-1u",           3,  "front", None),
    ("blank-c4",      "blank-1u",           4,  "front", None),
    ("blank-c5",      "blank-1u",           5,  "front", None),
    ("con-srv-02",    "eaton-tripp-lite-b096-016", 6, "front", "serial console — row"),
    ("mda-01",        "generic-lc-24-port-fiber-patch-panel", 7, "front", "MDA — cross-rack LC fiber"),
    ("cm-bar-c7",     "generic-cable-management-panel-1u", 7, "rear", None),
    ("blank-c8",      "blank-1u",           8,  "front", None),
    ("spine-01",      "dell-powerswitch-s5248f-on", 9,  "front", "aggregation A"),
    ("spine-02",      "dell-powerswitch-s5248f-on", 10, "front", "aggregation B"),
    *[("blank-c%d-%d" % (u, u + 1), "generic-blanking-panel-2u", u, "front", None)
      for u in range(11, 42, 2)],                  # U11..U42
]

PORTS_C = {
    "spine-01": [
        dict(kind="sfp28", prefix="Eth1/1/", count=48, speed_mbps=25000),
        dict(kind="qsfp", prefix="Eth1/1/", count=4, start_index=49, speed_mbps=100000),
        dict(kind="rj45", prefix="mgmt", count=1, start_index=0),
        dict(kind="console", prefix="con", count=1, start_index=0),
        dict(kind="power", prefix="psu", count=2),
    ],
    "spine-02": [
        dict(kind="sfp28", prefix="Eth1/1/", count=48, speed_mbps=25000),
        dict(kind="qsfp", prefix="Eth1/1/", count=4, start_index=49, speed_mbps=100000),
        dict(kind="rj45", prefix="mgmt", count=1, start_index=0),
        dict(kind="console", prefix="con", count=1, start_index=0),
        dict(kind="power", prefix="psu", count=2),
    ],
    "mda-01": [dict(kind="patch", prefix="lc", count=24, pair_prefix="lb")],
    "con-srv-02": [
        dict(kind="console", prefix="port", count=16),
        dict(kind="rj45", prefix="eth", count=1),
        dict(kind="power", prefix="psu", count=1),
    ],
    "pdu-d1": [
        dict(kind="power", prefix="o", count=8),
        dict(kind="power", prefix="in", count=1),
        dict(kind="rj45", prefix="net", count=1),
    ],
    "pdu-d2": [
        dict(kind="power", prefix="o", count=8),
        dict(kind="power", prefix="in", count=1),
        dict(kind="rj45", prefix="net", count=1),
    ],
    "ups-c1": [
        dict(kind="power", prefix="out", count=4),
        dict(kind="rj45", prefix="net", count=1),
    ],
}

CABLES_C = [
    # consoles + OOB
    ("con-srv-02", "eth1", "spine-01", "mgmt0", "cat6", "grey", None, 0.5),
    ("spine-01", "con0", "con-srv-02", "port2", "console", "purple", None, 0.5),
    ("spine-02", "con0", "con-srv-02", "port3", "console", "purple", None, 0.5),
    # power
    ("pdu-d1", "in1", "ups-c1", "out1", "power", "black", "E feed", 0.5),
    ("pdu-d2", "in1", "ups-c1", "out2", "power", "black", "F feed", 0.5),
    ("spine-01", "psu1", "pdu-d1", "o1", "power", "red", None, 1.0),
    ("spine-01", "psu2", "pdu-d2", "o1", "power", "blue", None, 1.0),
    ("spine-02", "psu1", "pdu-d1", "o2", "power", "red", None, 1.0),
    ("spine-02", "psu2", "pdu-d2", "o2", "power", "blue", None, 1.0),
    ("con-srv-02", "psu1", "pdu-d1", "o3", "power", "red", None, 0.5),
]

# --------------------------------------------- cross-rack (via the MDA) ----
# Singlemode cross-connects landing on the LC field: ToR/spine uplinks traced
# through mda-01's front↔rear pairs — the multi-rack L1 trace demo.
XCABLES = [
    ("tor-b-01", "Te1/1/1", "mda-01", "lc1", "fiber_sm", "yellow", "XR-B-01", 15.0),
    ("mda-01", "lb1", "spine-01", "Eth1/1/1", "fiber_sm", "yellow", "XR-B-01", 1.0),
    ("tor-b-01", "Te1/1/2", "mda-01", "lc2", "fiber_sm", "yellow", "XR-B-02", 15.0),
    ("mda-01", "lb2", "spine-02", "Eth1/1/1", "fiber_sm", "yellow", "XR-B-02", 1.0),
    ("sw-access-01", "Te1/1/3", "mda-01", "lc3", "fiber_sm", "yellow", "XR-A-01", 8.0),
    ("mda-01", "lb3", "spine-01", "Eth1/1/2", "fiber_sm", "yellow", "XR-A-01", 1.0),
    ("sw-access-02", "Te1/1/3", "mda-01", "lc4", "fiber_sm", "yellow", "XR-A-02", 8.0),
    ("mda-01", "lb4", "spine-02", "Eth1/1/2", "fiber_sm", "yellow", "XR-A-02", 1.0),
    ("tor-b-01", "con0", "con-srv-02", "port1", "console", "purple", None, 10.0),
]

RACKS = [
    dict(name=RACK_NAME, position=0, height_u=42,
         desc="V4A cabling demo — carriers, patch panels, L1 traces",
         devices=DEVICES, ports=PORTS, cables=CABLES),
    dict(name="Demo DC Rack — Compute", position=1, height_u=42,
         desc="dense compute row-end — ToR + OOB through pp-c",
         devices=DEVICES_B, ports=PORTS_B, cables=CABLES_B),
    dict(name="Demo DC Rack — Edge / MDA", position=2, height_u=42,
         desc="aggregation + LC fiber MDA — cross-rack cross-connects",
         devices=DEVICES_C, ports=PORTS_C, cables=CABLES_C),
]

# ------------------------------------------------------------------- IPs ---
# (last_octet, hostname, device, connected (dev,port) | None, notes)
IPS = [
    (1,   "gw.demo.local",        "rtr-wan-01",    None, "WAN edge gateway"),
    (2,   "sw-access-01.demo",    "sw-access-01",  None, "SVI"),
    (3,   "sw-access-02.demo",    "sw-access-02",  None, "SVI"),
    (4,   "sw-mgmt-01.demo",      "sw-mgmt-01",    None, "OOB SVI"),
    (5,   "fw-edge-01.demo",      "fw-edge-01",    None, None),
    (11,  "esxi-01.demo.local",   "srv-esxi-01",   ("sw-access-01", "Gi1/0/1"), "vmk0"),
    (12,  "esxi-02.demo.local",   "srv-esxi-02",   ("sw-access-02", "Gi1/0/1"), "vmk0"),
    (13,  "backup-01.demo.local", "srv-backup-01", ("sw-access-01", "Gi1/0/3"), None),
    (14,  "app-01.demo.local",    "srv-app-01",    ("sw-access-01", "Gi1/0/4"), None),
    (15,  "app-02.demo.local",    "srv-app-02",    ("sw-access-01", "Gi1/0/5"), None),
    (16,  "san-01.demo.local",    "san-01",        ("sw-access-01", "Gi1/0/6"), "controller A"),
    (21,  "sdwan-a.demo.local",   "edge-sdwan-a",  ("sw-access-01", "Gi1/0/7"), "carrier slot 0"),
    (22,  "sdwan-b.demo.local",   "edge-sdwan-b",  ("sw-access-01", "Gi1/0/8"), "carrier slot 1"),
    (25,  "kvm-01.demo.local",    "kvm-01",        ("sw-access-01", "Gi1/0/9"), None),
    (26,  "con-srv-01.demo.local","con-srv-01",    ("sw-access-01", "Gi1/0/10"), None),
    # rack B — compute row
    *[(30 + i, "compute-%02d.demo.local" % i, "srv-compute-%02d" % i,
       ("tor-b-01", "Gi1/0/%d" % i), "k8s node") for i in range(1, 9)],
    (41,  "tor-b-01.demo",        "tor-b-01",      None, "SVI"),
    # rack C — edge/MDA
    (42,  "spine-01.demo",        "spine-01",      None, "agg A SVI"),
    (43,  "spine-02.demo",        "spine-02",      None, "agg B SVI"),
    (44,  "con-srv-02.demo",      "con-srv-02",    None, "row console"),
]
# Legacy free-text rows — then POST /interfaces/match-free-text links them.
LEGACY_IPS = [
    (101, "printer-legacy-01", "sw-access-01", "Gi1/0/20"),
    (102, "printer-legacy-02", "sw-access-01", "Gi1/0/21"),
    (103, "printer-legacy-03", "sw-old-03", "Fa0/1"),  # honest "unmatched"
]
# Host-side NIC -> IP binding (DeviceInterface.connected_ip_id).
NIC_IP = {
    ("srv-esxi-01", "eno1"): 11,
    ("srv-esxi-02", "eno1"): 12,
    ("srv-compute-01", "eno1"): 31,
}


# ------------------------------------------------------------- zip emit ----
def _yaml_scalar(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    s = str(v)
    if s and all(c.isalnum() or c in " _-./" for c in s) and not s[0].isdigit():
        return s
    return json.dumps(s, ensure_ascii=False)


def _yaml_lines(obj, indent: int) -> list[str]:
    pad = "  " * indent
    out: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                out.append(f"{pad}{k}:")
                out += _yaml_lines(v, indent + 1)
            elif isinstance(v, (dict, list)):
                out.append(f"{pad}{k}: {'[]' if isinstance(v, list) else '{}'}")
            else:
                out.append(f"{pad}{k}: {_yaml_scalar(v)}")
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                first = True
                for k, v in item.items():
                    head = f"{pad}- " if first else f"{pad}  "
                    first = False
                    if isinstance(v, (dict, list)) and v:
                        out.append(f"{head}{k}:")
                        out += _yaml_lines(v, indent + 2)
                    elif isinstance(v, (dict, list)):
                        out.append(f"{head}{k}: {'[]' if isinstance(v, list) else '{}'}")
                    else:
                        out.append(f"{head}{k}: {_yaml_scalar(v)}")
            else:
                out.append(f"{pad}- {_yaml_scalar(item)}")
    else:
        out.append(f"{pad}{_yaml_scalar(obj)}")
    return out


def layout_doc() -> dict:
    """The layout.yaml payload — mirrors frontend/src/lib/rackula.ts's export."""
    types: dict[str, dict] = {}
    devices = []
    carriers = {d[0]: d for d in DEVICES if DEVICE_TYPES[d[1]][7]}

    for i, d in enumerate(DEVICES):
        name, slug, u, face, extra = d
        t = DEVICE_TYPES[slug]
        slots_layout = t[7]
        carrier = extra.get("carrier") if isinstance(extra, dict) else None
        notes = extra if isinstance(extra, str) else None

        if slug not in types:
            td: dict = {
                "slug": slug,
                "u_height": t[0],
                "manufacturer": t[1],
                "model": t[2],
                "colour": t[3],
                "category": "chassis" if t[4] == "carrier" else t[4],
            }
            if slots_layout == "halves":
                td.update(
                    slot_width=1,
                    subdevice_role="parent",
                    slots=[
                        {"id": "0", "position": {"row": 0, "col": 0}},
                        {"id": "1", "position": {"row": 0, "col": 1}},
                    ],
                )
            elif slots_layout:
                td.update(
                    slot_width=2,
                    subdevice_role="parent",
                    slots=[{"id": "0", "position": {"row": 0, "col": 0}}],
                )
            types[slug] = td

        entry: dict = {"id": f"dev-{i}", "device_type": slug, "face": face or "front"}
        if carrier:
            ci = next(j for j, x in enumerate(DEVICES) if x[0] == carrier)
            entry["position"] = extra["slot"]
            entry["container_id"] = f"dev-{ci}"
            entry["slot_id"] = str(extra["slot"])
            child_type = types.get(slug)
            if child_type is not None:
                child_type["subdevice_role"] = "child"
        else:
            entry["position"] = u * UNITS_PER_U
        if name:
            entry["name"] = name
        if notes:
            entry["notes"] = notes
        devices.append(entry)

    for slug in {d[1] for d in DEVICES if isinstance(d[4], dict) and "carrier" in d[4]}:
        if slug in types:
            types[slug]["subdevice_role"] = "child"

    return {
        "version": "1.1.0",
        "name": RACK_NAME,
        "metadata": {"id": "d3m0-v4a0-cab1-1ing-d3m0rack000001", "name": RACK_NAME, "schema_version": "1.1"},
        "racks": [{
            "id": "rack-1",
            "name": RACK_NAME,
            "height": 42,
            "width": 19,
            "desc_units": False,
            "show_rear": True,
            "form_factor": "4-post-cabinet",
            "starting_unit": 1,
            "position": 0,
            "devices": devices,
        }],
        "device_types": list(types.values()),
        "settings": {"display_mode": "label", "show_labels_on_images": False},
    }


def emit_zip(path: Path) -> Path:
    text = "\n".join(_yaml_lines(layout_doc(), 0)) + "\n"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        info = zipfile.ZipInfo("layout.yaml", date_time=ZIP_DATE)
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, text)
    return path


# --------------------------------------------------------------- apply -----
class _KeepMethodRedirect(urllib.request.HTTPRedirectHandler):
    """urllib downgrades redirected POSTs to GET; an API behind an
    http->https upgrade needs the method + body preserved (307 semantics)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if code in (301, 302, 303, 307, 308):
            return urllib.request.Request(
                newurl, data=req.data, method=req.get_method(),
                headers=dict(req.header_items()),
            )
        return None


class Api:
    """Minimal client — works over http:// and https:// alike.

    Carries the session cookie by hand (so Secure cookies still reach
    plain-http dev boxes), verifies TLS properly by default, and follows
    scheme-upgrade redirects without dropping POST bodies."""

    def __init__(self, base: str, insecure: bool = False):
        if "://" not in base:  # bare host[:port] — guess the scheme
            host = base.split("/", 1)[0].split(":", 1)[0]
            scheme = "http" if host in ("localhost", "127.0.0.1", "::1") else "https"
            base = f"{scheme}://{base}"
        self.base = base.rstrip("/") + "/api/v1"
        self.cookie: str | None = None
        ctx = ssl.create_default_context()
        if insecure:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=ctx), _KeepMethodRedirect()
        )

    def req(self, method: str, path: str, body=None):
        url = self.base + path
        data = json.dumps(body).encode() if body is not None else None
        r = urllib.request.Request(url, data=data, method=method)
        r.add_header("Content-Type", "application/json")
        if self.cookie:
            r.add_header("Cookie", self.cookie)
        try:
            resp = self.opener.open(r)
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:300]
            raise RuntimeError(f"{method} {path} -> {e.code}: {detail}") from e
        with resp:
            for sc in resp.headers.get_all("Set-Cookie") or []:
                nv = sc.split(";", 1)[0].strip()
                if nv.startswith("ipambox_session="):
                    self.cookie = nv
            raw = resp.read()
            return json.loads(raw) if raw else {}

    def login(self, user: str, password: str):
        st = self.req("GET", "/auth/status")
        if st.get("authenticated"):
            print(f"auth: already authenticated ({st.get('username') or 'insecure'})")
            return
        self.req("POST", "/auth/login", {"username": user, "password": password})
        print(f"auth: logged in as {user}")


def find_one(api: Api, path: str, name: str):
    rows = api.req("GET", path)
    items = rows.get("items", rows) if isinstance(rows, dict) else rows
    return next((r for r in items if r.get("name") == name), None)


def _device_payload(devices) -> list[dict]:
    """DEVICES rows -> RackDeviceImport items (carrier children deferred via
    carrier_key, watts/weight included for the capacity rollups)."""
    payload = []
    for name, slug, u, face, extra in devices:
        t = DEVICE_TYPES[slug]
        e = {
            "name": name, "device_type": slug,
            "u_position": u, "u_height": t[0], "face": face or "front",
            "colour": t[3], "category": "chassis" if t[4] == "carrier" else t[4],
            "manufacturer": t[1], "model": t[2],
            "watts": t[5], "weight_kg": t[6],
            "notes": extra if isinstance(extra, str) else None,
        }
        if isinstance(extra, dict):  # carrier child — u derives from the tray
            e["carrier_key"] = f"z-{extra['carrier']}"
            e["slot"] = extra["slot"]
            e["u_position"] = None
        if t[7]:  # carrier tray
            e["slot_layout"] = t[7]
            e["carrier_key"] = f"z-{name}"
        payload.append({k: v for k, v in e.items() if v is not None})
    return payload


def apply(api: Api) -> None:
    # --- scaffolding: site -> group -> the whole row of racks
    site = find_one(api, "/sites", SITE_NAME) or api.req(
        "POST", "/sites", {"name": SITE_NAME, "code": "DDC", "description": "Demo data center row"}
    )
    group = find_one(api, "/rack-groups", GROUP_NAME) or api.req(
        "POST", "/rack-groups", {"name": GROUP_NAME, "site_id": site["id"], "description": "demo row"}
    )

    dev_by_name: dict = {}
    iface: dict = {}
    rack_ids: list[tuple[str, int]] = []
    for spec in RACKS:
        rack = find_one(api, "/racks", spec["name"])
        if rack:
            detail = api.req("GET", f"/racks/{rack['id']}")
            if detail.get("devices"):
                print(f"rack '{spec['name']}' exists (id {rack['id']}) — wiping devices")
                for d in detail["devices"]:
                    api.req("DELETE", f"/devices/{d['id']}")
            api.req("PATCH", f"/racks/{rack['id']}", {
                "group_id": group["id"], "group_position": spec["position"],
                "site_id": site["id"], "description": spec["desc"],
            })
        else:
            rack = api.req("POST", "/racks", {
                "name": spec["name"], "site_id": site["id"], "group_id": group["id"],
                "group_position": spec["position"], "height_u": spec["height_u"],
                "description": spec["desc"],
            })
        rack_ids.append((spec["name"], rack["id"]))

        res = api.req("POST", f"/racks/{rack['id']}/devices/import",
                      {"mode": "merge", "devices": _device_payload(spec["devices"])})
        print(f"{spec['name']} (rack {rack['id']}): {res.get('created')} devices"
              + (f", skipped {res['skipped']}" if res.get("skipped") else ""))

        detail = api.req("GET", f"/racks/{rack['id']}")
        for d in detail.get("devices", []):
            dev_by_name[d["name"]] = d
        for d in spec["devices"]:  # carrier children may not list on the rack
            if d[0] not in dev_by_name:
                rows = api.req("GET", f"/devices?q={d[0]}")
                for r in (rows.get("items", rows)):
                    if r["name"] == d[0]:
                        dev_by_name[d[0]] = r

        for name, gens in spec["ports"].items():
            dev = dev_by_name.get(name)
            if not dev:
                print(f"  !! no device {name} — ports skipped")
                continue
            for body in gens:
                api.req("POST", f"/devices/{dev['id']}/interfaces/generate", body)
            ifaces = api.req("GET", f"/devices/{dev['id']}/interfaces")
            rows = ifaces.get("items", ifaces) if isinstance(ifaces, dict) else ifaces
            iface[name] = {i["name"]: i["id"] for i in rows}
    print(f"interfaces generated: {sum(len(v) for v in iface.values())} across {len(iface)} devices")

    def iid(dev: str, port: str) -> int:
        try:
            return iface[dev][port]
        except KeyError:
            raise RuntimeError(f"no interface {dev}:{port} (have {sorted(iface.get(dev, {}))[:8]}…)")

    # --- cables: intra-rack plans, then the cross-rack MDA runs
    n = 0
    for plan in [c for spec in RACKS for c in spec["cables"]] + XCABLES:
        a_dev, a_port, b_dev, b_port, kind, color, label, length = plan
        api.req("POST", "/cables", {
            "a_interface_id": iid(a_dev, a_port), "b_interface_id": iid(b_dev, b_port),
            "kind": kind, "color": color, "label": label, "length_m": length,
        })
        n += 1
    print(f"cables created: {n}")

    # --- IPs: prefix + addresses + connected_interface links + NIC bindings
    vrf = find_one(api, "/vrfs", "Demo") or api.req("POST", "/vrfs", {"name": "Demo", "description": "demo vrf"})
    prefix = next(
        (p for p in api.req("GET", "/prefixes") if p.get("prefix") == PREFIX), None
    ) or api.req("POST", "/prefixes", {
        "prefix": PREFIX, "vrf_id": vrf["id"], "site_id": site["id"],
        "description": "demo cabling subnet",
    })
    def upsert_address(body: dict, patch_extra: dict | None = None) -> int:
        """POST the address, or PATCH the existing row on a re-run.
        `patch_extra` is sent verbatim on PATCH so explicit nulls survive."""
        body = {k: v for k, v in body.items() if v is not None}
        existing = next(
            (a for a in api.req("GET", f"/addresses?prefix_id={prefix['id']}&q={body['address']}")
             if a["address"] == body["address"]), None)
        if existing:
            api.req("PATCH", f"/addresses/{existing['id']}", {**body, **(patch_extra or {})})
            return existing["id"]
        return api.req("POST", "/addresses", body)["id"]

    ip_by_octet = {}
    for octet, host, dev, conn, notes in IPS:
        body = {
            "address": f"10.200.0.{octet}", "prefix_id": prefix["id"],
            "hostname": host, "device_id": dev_by_name[dev]["id"],
            "role": "vip" if octet == 1 else None,
            "notes": notes,
        }
        if conn:
            body["connected_interface_id"] = iid(*conn)
        ip_by_octet[octet] = upsert_address(body)
    print(f"addresses upserted: {len(ip_by_octet)}")

    for (dev, port), octet in NIC_IP.items():
        api.req("PATCH", f"/devices/{dev_by_name[dev]['id']}/interfaces/{iid(dev, port)}",
                {"connected_ip_id": ip_by_octet[octet]})

    for octet, host, sw, port in LEGACY_IPS:
        upsert_address({
            "address": f"10.200.0.{octet}", "prefix_id": prefix["id"],
            "hostname": host, "switch_name": sw, "switch_port": port,
            "notes": "legacy free-text switch reference",
        }, patch_extra={"connected_interface_id": None})
    report = api.req("POST", "/interfaces/match-free-text")
    print(f"match-free-text: {report}")

    # --- two traces as a smoke check: intra-rack panel hop + cross-rack MDA
    for dev, port in (("srv-esxi-01", "eno1"), ("tor-b-01", "Te1/1/1")):
        hops = api.req("GET", f"/cables/trace?interface_id={iid(dev, port)}")
        chain = " -> ".join(f"{h['device_name']}:{h['interface_name']}" for h in hops)
        print(f"trace {dev}:{port}  {chain}")

    rows = " / ".join(f"/racks/{rid}" for _, rid in rack_ids)
    print(f"\ndone — racks: {rows} · panel: /devices/{dev_by_name['pp-a-24']['id']}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", nargs="?", default="emit", choices=["emit", "apply"])
    ap.add_argument("--api", default=os.environ.get("IPAMBOX_API", "http://localhost:3010"),
                    help="base URL — http or https (bare host guesses by name)")
    ap.add_argument("--user", default=os.environ.get("IPAMBOX_USER", "admin"))
    ap.add_argument("--password", default=os.environ.get("IPAMBOX_PASS"))
    ap.add_argument("--insecure", action="store_true",
                    default=os.environ.get("IPAMBOX_INSECURE") == "1",
                    help="skip TLS verification (self-signed certs)")
    args = ap.parse_args()

    if args.mode == "emit":
        out = emit_zip(HERE / ZIP_NAME)
        print(f"wrote {out}")
        return

    api = Api(args.api, insecure=args.insecure)
    try:
        st = api.req("GET", "/auth/status")
    except urllib.error.URLError as e:
        hint = " (try --insecure for a self-signed cert)" if "certificate" in str(e).lower() else ""
        raise SystemExit(f"cannot reach {api.base}: {e.reason}{hint}")
    pw = args.password
    if not st.get("authenticated") and not st.get("allow_insecure") and pw is None:
        pw = getpass.getpass(f"password for {args.user}@{args.api}: ")
    api.login(args.user, pw or "")
    apply(api)


if __name__ == "__main__":
    main()
