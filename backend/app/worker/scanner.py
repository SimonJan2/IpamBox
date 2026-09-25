import asyncio
import ipaddress
import os
import socket
import struct
import subprocess
import time
from dataclasses import dataclass, field

import psutil

from app.services.oui import vendor_for


class ScanCancelled(Exception):
    """Raised inside the pipeline when the user cancels the scan."""


@dataclass
class HostResult:
    ip: str
    mac: str | None = None
    vendor: str | None = None
    hostname: str | None = None
    open_ports: list[int] = field(default_factory=list)
    device_type: str | None = None


# ---------------------------------------------------------------------------
# Device-type inference (LAN-Orangutan style): ports -> vendor -> hostname.
# ---------------------------------------------------------------------------

_VENDOR_HINTS = [
    (("mikrotik", "ubiquiti", "netgear", "tp-link", "cisco", "aruba", "juniper",
      "fortinet", "draytek", "avm", "zyxel", "edgecore"), "router"),
    (("synology", "qnap", "asustor", "terramaster", "buffalo", "netgear ready"), "nas"),
    (("hp", "hewlett", "canon", "epson", "brother", "kyocera", "xerox", "ricoh",
      "lexmark", "oki"), "printer"),
    (("hikvision", "dahua", "axis", "reolink", "vivotek", "amcrest", "uniview"), "camera"),
    (("espressif", "tuya", "shelly", "sonoff", "wemo", "tasmota", "xiaomi",
      "tenda", "govee", "meross", "philips hue", "signify", "ring", "blink"), "iot"),
    (("raspberry",), "iot"),
    (("apple", "samsung", "google", "huawei", "oneplus", "motorola"), "phone"),
    (("roku", "amazon", "lg electronics", "sony", "vizio", "tcl", "hisense"), "tv"),
    (("vmware", "virtualbox", "qemu", "kvm", "proxmox", "microsoft hyper-v",
      "parallels"), "vm"),
    (("dell", "supermicro", "lenovo", "fujitsu", "inspur"), "server"),
    (("intel", "azurewave", "realtek", "liteon", "compal", "foxconn",
      "wistron", "pegatron", "vantiva", "sagemcom", "arris", "technicolor"), "workstation"),
]

_PORT_HINTS = [
    ({9100, 515, 631}, "printer"),
    ({554, 8554}, "camera"),
    ({8008, 8009, 8060}, "tv"),          # chromecast / airplay-ish
    ({1900, 5000, 5001}, "nas"),         # ssdp + synology/qnap webui
    ({62078}, "phone"),                  # iphone sync
    ({3389, 445}, "workstation"),        # RDP / SMB -> windows box
    ({5353}, "iot"),                     # mDNS-only devices
]

_HOSTNAME_HINTS = [
    (("router", "gateway", "gw-", "fw-", "firewall", "opnsense", "pfsense",
      "mikrotik", "ubnt", "unifi"), "router"),
    (("print", "laserjet", "officejet", "epson", "brother", "kyocera"), "printer"),
    (("nas", "synology", "qnap", "diskstation", "plex", "truenas", "freenas"), "nas"),
    (("cam", "nvr", "dvr", "doorbell"), "camera"),
    (("iphone", "ipad", "android", "galaxy", "pixel"), "phone"),
    (("tv", "roku", "firestick", "chromecast", "bravia", "webos"), "tv"),
    (("esp", "shelly", "tasmota", "tuya", "wemos", "sonoff", "iot"), "iot"),
    (("server", "srv", "docker", "kube", "node", "proxmox", "pve", "vm-"), "server"),
    (("desktop", "laptop", "pc-", "macbook", "imac", "workstation"), "workstation"),
]


def infer_device_type(
    vendor: str | None, hostname: str | None, open_ports: list[int]
) -> str | None:
    """Best-effort device classification; None when nothing matched."""
    ports = set(open_ports or [])

    # 1. Strong port signatures first
    for sig, dtype in _PORT_HINTS:
        if sig & ports:
            return dtype

    # 2. Hostname keywords (user-set names are more specific than OUI)
    if hostname:
        h = hostname.lower()
        for words, dtype in _HOSTNAME_HINTS:
            if any(w in h for w in words):
                return dtype

    # 3. Vendor keywords
    if vendor:
        v = vendor.lower()
        for words, dtype in _VENDOR_HINTS:
            if any(w in v for w in words):
                return dtype

    # 4. Heuristic: many open TCP services -> likely a server
    if len(ports) >= 3:
        return "server"
    return None


def detect_interface(explicit: str = "") -> str | None:
    if explicit:
        return explicit
    try:
        out = subprocess.run(
            ["ip", "route", "show", "default"], capture_output=True, text=True, timeout=5
        ).stdout
        if " dev " in out:
            return out.split(" dev ")[1].split()[0]
    except Exception:
        pass
    return None


def detect_local_cidr(iface: str = "") -> str | None:
    """CIDR of the default-route interface, e.g. '192.168.1.0/24'."""
    dev = detect_interface(iface)
    if not dev:
        return None
    for addr in psutil.net_if_addrs().get(dev, []):
        if addr.family == socket.AF_INET and addr.address and addr.netmask:
            return str(ipaddress.ip_network(f"{addr.address}/{addr.netmask}", strict=False))
    return None


def _arp_scan(cidr: str, iface: str | None, timeout: float) -> dict[str, str]:
    """Blocking scapy ARP sweep -> {ip: mac}. Runs in a thread."""
    try:
        from scapy.all import ARP, Ether, srp

        pkt = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=cidr)
        kwargs: dict = {"timeout": timeout, "verbose": 0}
        if iface:
            kwargs["iface"] = iface
        answered, _ = srp(pkt, **kwargs)
        return {rcv.psrc: rcv.hwsrc.upper() for _, rcv in answered}
    except Exception:
        return {}


_ICMP_ECHO_REQUEST = 8
_ICMP_ECHO_REPLY = 0


def _icmp_checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\x00"
    total = sum(
        int.from_bytes(data[i : i + 2], "big") for i in range(0, len(data), 2)
    )
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return ~total & 0xFFFF


def _icmp_echo_packet(ident: int, seq: int, payload: bytes) -> bytes:
    """A well-formed ICMP echo request: the kernel validates type/code
    and checksum even on unprivileged ping sockets — an arbitrary
    payload with no header is rejected with EINVAL."""
    head = struct.pack("!BBHHH", _ICMP_ECHO_REQUEST, 0, 0, ident, seq)
    check = _icmp_checksum(head + payload)
    return struct.pack("!BBHHH", _ICMP_ECHO_REQUEST, 0, check, ident, seq) + payload


def _icmp_socket() -> tuple[socket.socket | None, bool, str | None]:
    """Open an IPv4 ICMP echo socket: unprivileged ping socket
    (SOCK_DGRAM) first, raw socket fallback for hosts whose
    ping_group_range denies the unprivileged kind (the worker carries
    cap_net_raw for exactly that). Returns (sock, is_raw, err)."""
    err: str | None = None
    for stype in (socket.SOCK_DGRAM, socket.SOCK_RAW):
        try:
            return (
                socket.socket(socket.AF_INET, stype, socket.IPPROTO_ICMP),
                stype == socket.SOCK_RAW,
                None,
            )
        except OSError as e:
            err = e.strerror or str(e)
    return None, False, err


def _is_echo_reply(data: bytes, is_raw: bool) -> bool:
    """RAW sockets prepend the IP header to every read; DGRAM ping
    sockets hand back the ICMP message alone and only ever deliver
    replies addressed to this socket."""
    if is_raw:
        if len(data) < 21:
            return False
        ihl = (data[0] & 0x0F) * 4
        return len(data) >= ihl + 1 and data[ihl] == _ICMP_ECHO_REPLY
    return True


def _ping_host_blocking(ip: str, timeout: float) -> tuple[bool, str | None]:
    """Single ICMP echo + reply wait, plain blocking socket ops. Runs in
    a worker thread via asyncio.to_thread — uvloop (the API's loop) has
    no sock_sendto/sock_recvfrom for datagrams, so the loop-level API is
    not usable everywhere."""
    sock, is_raw, err = _icmp_socket()
    if sock is None:
        return False, f"icmp socket unavailable: {err}"
    try:
        packet = _icmp_echo_packet(
            os.getpid() & 0xFFFF, 1, b"ipambox" + b"\x00" * 24
        )
        sock.sendto(packet, (ip, 0))
        deadline = time.monotonic() + timeout
        while True:
            left = deadline - time.monotonic()
            if left <= 0:
                return False, "timeout"
            sock.settimeout(left)
            try:
                data, (src, _p) = sock.recvfrom(4096)
            except TimeoutError:
                return False, "timeout"
            except OSError:
                continue
            if src == ip and _is_echo_reply(data, is_raw):
                return True, None
    except OSError as e:
        return False, str(e)
    finally:
        sock.close()


def _icmp_sweep_blocking(ips: list[str], timeout: float) -> set[str]:
    """ICMP echo sweep on one socket: fire all echos, then drain replies
    until the deadline. Blocking variant of the old loop-based sweep —
    identical semantics, safe under any loop policy."""
    alive: set[str] = set()
    if not ips:
        return alive
    sock, is_raw, _err = _icmp_socket()
    if sock is None:
        return alive
    try:
        ident = os.getpid() & 0xFFFF
        payload = b"ipambox" + b"\x00" * 24
        sent = 0
        for seq, ip in enumerate(ips, start=1):
            try:
                sock.sendto(_icmp_echo_packet(ident, seq, payload), (ip, 0))
                sent += 1
                if sent % 64 == 0:
                    time.sleep(0.02)
            except OSError:
                continue
        deadline = time.monotonic() + timeout
        while True:
            left = deadline - time.monotonic()
            if left <= 0:
                break
            sock.settimeout(left)
            try:
                data, (src, _port) = sock.recvfrom(4096)
            except TimeoutError:
                break
            except OSError:
                continue
            if _is_echo_reply(data, is_raw):
                alive.add(src)
    finally:
        sock.close()
    return alive


async def _icmp_sweep(ips: list[str], timeout: float) -> set[str]:
    """ICMP echo sweep — the kernel builds the ICMP header and matches
    replies to this socket's ident, so we only need recvfrom sources."""
    return await asyncio.to_thread(_icmp_sweep_blocking, ips, timeout)


async def _tcp_probe(ip: str, ports: list[int], timeout: float, sem: asyncio.Semaphore) -> list[int]:
    async def one(port: int) -> int | None:
        async with sem:
            try:
                _, w = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout)
                w.close()
                try:
                    await asyncio.wait_for(w.wait_closed(), 1.0)
                except Exception:
                    pass
                return port
            except Exception:
                return None

    results = await asyncio.gather(*(one(p) for p in ports))
    return [p for p in results if p is not None]


async def _ptr_lookup(ip: str, sem: asyncio.Semaphore) -> str | None:
    async with sem:
        try:
            name, _, _ = await asyncio.wait_for(asyncio.to_thread(socket.gethostbyaddr, ip), 2.0)
            return name.rstrip(".")
        except Exception:
            return None


def _host_chunks(net, size: int = 1024):
    """Yield host-IP string lists without materializing the whole network.

    `net.hosts()` is already a lazy iterator; chunking keeps memory bounded
    regardless of target size (the scan_max_hosts guard bounds it anyway).
    """
    source = net.hosts() if net.num_addresses > 2 else iter(net)
    chunk: list[str] = []
    for ip in source:
        chunk.append(str(ip))
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


async def scan_cidr(
    cidr: str,
    *,
    iface: str = "",
    tcp_ports: list[int] | None = None,
    icmp_timeout: float = 1.5,
    tcp_timeout: float = 0.6,
    concurrency: int = 256,
    on_progress=None,
    on_hosts=None,
    should_stop=None,
) -> list[HostResult]:
    """Full pipeline: ARP (L2) -> ICMP -> TCP port probe -> PTR -> OUI.

    `on_hosts` is an optional async callable `(ips: list[str], phase: str)`
    fired once per detection step with the newly confirmed host IPs — after
    the ARP sweep, after each ICMP chunk, and after each fallback TCP batch —
    so deltas stay bounded to a chunk, never per-IP.
    `should_stop` is an optional async callable returning True when the scan
    has been cancelled; checked between phases/chunks -> raises ScanCancelled.
    """
    net = ipaddress.ip_network(cidr, strict=False)
    if net.version != 4:
        raise ValueError("IPv6 scanning is not supported yet")
    tcp_ports = tcp_ports or []
    sem = asyncio.Semaphore(concurrency)
    dev = detect_interface(iface)

    hosts: dict[str, HostResult] = {}

    async def _stopped() -> bool:
        return bool(should_stop and await should_stop())

    def _mark(ip: str, **kw):
        h = hosts.setdefault(ip, HostResult(ip=ip))
        for k, v in kw.items():
            if v is not None:
                setattr(h, k, v)

    def _ip_key(ip: str) -> int:
        return int(ipaddress.ip_address(ip))

    # 1. ARP scan (local subnet -> fast, authoritative for MACs)
    if net.version == 4:
        arp_timeout = max(2.0, min(10.0, net.num_addresses / 1500.0))
        arp_res = await asyncio.to_thread(_arp_scan, str(net), dev, arp_timeout)
        for ip, mac in arp_res.items():
            _mark(ip, mac=mac, vendor=vendor_for(mac))
        if on_hosts and arp_res:
            await on_hosts(sorted(arp_res, key=_ip_key), "arp")
    if on_progress:
        await on_progress("arp", 0.4)
    if await _stopped():
        raise ScanCancelled()

    # 2. ICMP sweep for everything not already found via ARP — iterated in
    # chunks so the target range is never materialized as a whole.
    total = max(1, net.num_addresses - (2 if net.num_addresses > 2 else 0))
    scanned = 0
    for batch in _host_chunks(net):
        alive = await _icmp_sweep([ip for ip in batch if ip not in hosts], icmp_timeout)
        for ip in alive:
            _mark(ip)
        if on_hosts and alive:
            await on_hosts(sorted(alive, key=_ip_key), "icmp")
        scanned += len(batch)
        if on_progress:
            await on_progress("icmp", 0.4 + 0.3 * min(1.0, scanned / total))
        if await _stopped():
            raise ScanCancelled()

    # Fallback: if L2+L3 found nothing (e.g. no CAP_NET_RAW), sweep TCP ports
    if not hosts and tcp_ports:
        async def probe_all(ip: str, found: list[str]):
            ports = await _tcp_probe(ip, tcp_ports, tcp_timeout, sem)
            if ports:
                _mark(ip, open_ports=ports)
                found.append(ip)

        for batch in _host_chunks(net, 256):
            found: list[str] = []
            await asyncio.gather(*(probe_all(ip, found) for ip in batch))
            if on_hosts and found:
                await on_hosts(sorted(found, key=_ip_key), "tcp")
            if await _stopped():
                raise ScanCancelled()

    # 3. Enrich: TCP port probe + PTR, bounded concurrency
    live = list(hosts.values())
    done = 0

    async def enrich(h: HostResult):
        nonlocal done
        ports, ptr = await asyncio.gather(
            _tcp_probe(h.ip, tcp_ports, tcp_timeout, sem),
            _ptr_lookup(h.ip, sem),
        )
        h.open_ports = ports
        h.hostname = ptr
        h.device_type = infer_device_type(h.vendor, h.hostname, ports)
        done += 1
        if on_progress and (done % 8 == 0 or done == len(live)):
            await on_progress("enrich", 0.7 + 0.3 * done / max(1, len(live)))

    await asyncio.gather(*(enrich(h) for h in live))
    if await _stopped():
        raise ScanCancelled()
    return sorted(live, key=lambda h: int(ipaddress.ip_address(h.ip)))
