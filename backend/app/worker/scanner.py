import asyncio
import ipaddress
import socket
import subprocess
from dataclasses import dataclass, field

import psutil

from app.services.oui import vendor_for


@dataclass
class HostResult:
    ip: str
    mac: str | None = None
    vendor: str | None = None
    hostname: str | None = None
    open_ports: list[int] = field(default_factory=list)


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


async def _icmp_sweep(ips: list[str], timeout: float) -> set[str]:
    """ICMP echo sweep over a Linux ping socket (SOCK_DGRAM/IPPROTO_ICMP).

    The kernel builds the ICMP header and matches replies to this socket's
    ident, so we only need recvfrom sources. Fully async and fast.
    """
    alive: set[str] = set()
    if not ips:
        return alive
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_ICMP)
        sock.setblocking(False)
    except OSError:
        return alive

    loop = asyncio.get_running_loop()
    payload = b"ipambox" + b"\x00" * 24
    try:
        sent = 0
        for ip in ips:
            try:
                await loop.sock_sendto(sock, payload, (ip, 0))
                sent += 1
                if sent % 64 == 0:
                    await asyncio.sleep(0.02)
            except OSError:
                continue
        deadline = loop.time() + timeout
        while True:
            left = deadline - loop.time()
            if left <= 0:
                break
            try:
                _data, (src, _port) = await asyncio.wait_for(
                    loop.sock_recvfrom(sock, 4096), left
                )
            except (asyncio.TimeoutError, TimeoutError):
                break
            except OSError:
                continue
            alive.add(src)
    finally:
        sock.close()
    return alive


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


async def scan_cidr(
    cidr: str,
    *,
    iface: str = "",
    tcp_ports: list[int] | None = None,
    icmp_timeout: float = 1.5,
    tcp_timeout: float = 0.6,
    concurrency: int = 256,
    on_progress=None,
) -> list[HostResult]:
    """Full pipeline: ARP (L2) -> ICMP -> TCP port probe -> PTR -> OUI."""
    net = ipaddress.ip_network(cidr, strict=False)
    tcp_ports = tcp_ports or []
    sem = asyncio.Semaphore(concurrency)
    dev = detect_interface(iface)

    hosts: dict[str, HostResult] = {}

    def _mark(ip: str, **kw):
        h = hosts.setdefault(ip, HostResult(ip=ip))
        for k, v in kw.items():
            if v is not None:
                setattr(h, k, v)

    # 1. ARP scan (local subnet -> fast, authoritative for MACs)
    if net.version == 4:
        arp_timeout = max(2.0, min(10.0, net.num_addresses / 1500.0))
        arp_res = await asyncio.to_thread(_arp_scan, str(net), dev, arp_timeout)
        for ip, mac in arp_res.items():
            _mark(ip, mac=mac, vendor=vendor_for(mac))
    if on_progress:
        await on_progress("arp", 0.4)

    # 2. ICMP sweep for everything not already found via ARP
    all_ips = [str(ip) for ip in net.hosts()] if net.num_addresses > 2 else [str(ip) for ip in net]
    remaining = [ip for ip in all_ips if ip not in hosts]
    # chunk the sweep so progress events flow on large subnets
    chunk = 1024
    for i in range(0, len(remaining), chunk):
        batch = remaining[i : i + chunk]
        alive = await _icmp_sweep(batch, icmp_timeout)
        for ip in alive:
            _mark(ip)
        if on_progress:
            await on_progress("icmp", 0.4 + 0.3 * min(1.0, (i + chunk) / max(1, len(remaining))))

    # Fallback: if L2+L3 found nothing (e.g. no CAP_NET_RAW), sweep TCP ports
    if not hosts and tcp_ports:
        async def probe_all(ip: str):
            ports = await _tcp_probe(ip, tcp_ports, tcp_timeout, sem)
            if ports:
                _mark(ip, open_ports=ports)

        await asyncio.gather(*(probe_all(ip) for ip in all_ips))

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
        done += 1
        if on_progress and (done % 8 == 0 or done == len(live)):
            await on_progress("enrich", 0.7 + 0.3 * done / max(1, len(live)))

    await asyncio.gather(*(enrich(h) for h in live))
    return sorted(live, key=lambda h: int(ipaddress.ip_address(h.ip)))
