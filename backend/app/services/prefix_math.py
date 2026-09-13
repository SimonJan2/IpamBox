import ipaddress
from ipaddress import IPv4Network, IPv6Network

Network = IPv4Network | IPv6Network


def to_network(cidr) -> Network:
    return ipaddress.ip_network(str(cidr), strict=False)


def usable_bounds(net: Network) -> tuple[int, int]:
    """Inclusive [first, last] integer range of host-usable addresses."""
    first = int(net.network_address)
    last = int(net.broadcast_address) if net.version == 4 else int(net.network_address) + net.num_addresses - 1
    if net.version == 6:
        return first, last
    if net.prefixlen >= 31:  # /31 point-to-point and /32 host: all addresses usable
        return first, last
    return first + 1, last - 1


def usable_count(net: Network) -> int:
    lo, hi = usable_bounds(net)
    return max(0, hi - lo + 1)


def reserves_boundaries(net: Network) -> bool:
    """True when network/broadcast addresses are unusable for hosts (IPv4 <= /30)."""
    return net.version == 4 and net.prefixlen <= 30


def lowest_free(
    net: Network,
    taken: set[int],
    excluded_ranges: tuple[tuple[int, int], ...] = (),
) -> int | None:
    """Lowest usable address integer not in `taken` or any excluded range."""
    lo, hi = usable_bounds(net)
    # Merge taken singles and excluded ranges into sorted (start, end) blocks.
    blocks = sorted([(t, t) for t in taken] + list(excluded_ranges))
    candidate = lo
    for s, e in blocks:
        if e < candidate:
            continue
        if s > hi:
            break
        if s <= candidate <= e:
            candidate = e + 1
        elif s > candidate:
            break
    return candidate if candidate <= hi else None


def children(net: Network, new_prefix: int) -> list[Network]:
    """Split `net` into children of `new_prefix` length."""
    if new_prefix <= net.prefixlen or new_prefix > net.max_prefixlen:
        raise ValueError("new mask must be longer than current and within address family")
    return list(net.subnets(new_prefix=new_prefix))


def parent_chain(net: Network, candidates: list[Network]) -> Network | None:
    """The smallest candidate network that strictly contains `net`."""
    parents = [c for c in candidates if c.prefixlen < net.prefixlen and net.subnet_of(c)]
    return max(parents, key=lambda n: n.prefixlen, default=None)
