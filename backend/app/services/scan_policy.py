"""Scan-target policy shared by the API route, the scheduler, and the worker.

``scan_exclude_networks`` must mean the same thing everywhere: a target is
rejected when it overlaps an excluded network in EITHER direction —
scanning inside an excluded block is as wrong as scanning a supernet that
swallows one. (The scheduler's old one-direction ``net.subnet_of(x)``
check missed the supernet case, so an exclusion inside a configured
scan_networks block was silently scanned anyway.)
"""
import ipaddress


def exclusion_hit(net, exclude_networks: list[str]) -> str | None:
    """Return the first excluded CIDR overlapping ``net`` (either direction),
    or None. ``net`` is an ipaddress network; entries that fail to parse or
    are the other address family are ignored (settings validation is the
    place to reject those — a bad entry must not crash the scheduler or
    silently widen a same-family exclusion)."""
    for raw in exclude_networks:
        try:
            xn = ipaddress.ip_network(raw, strict=False)
        except ValueError:
            continue
        if xn.version != net.version:
            continue
        if net.subnet_of(xn) or xn.subnet_of(net):
            return str(xn)
    return None
