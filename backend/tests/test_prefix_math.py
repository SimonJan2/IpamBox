import ipaddress

from app.services import prefix_math as pm


def test_usable_bounds_24():
    net = pm.to_network("192.168.10.0/24")
    lo, hi = pm.usable_bounds(net)
    assert (ipaddress.ip_address(lo), ipaddress.ip_address(hi)) == (
        ipaddress.ip_address("192.168.10.1"),
        ipaddress.ip_address("192.168.10.254"),
    )
    assert pm.usable_count(net) == 254
    assert pm.reserves_boundaries(net)


def test_usable_bounds_31_and_32():
    n31 = pm.to_network("10.0.0.0/31")
    assert pm.usable_count(n31) == 2
    assert not pm.reserves_boundaries(n31)
    n32 = pm.to_network("10.0.0.5/32")
    assert pm.usable_count(n32) == 1


def test_lowest_free_skips_taken_and_boundaries():
    net = pm.to_network("192.168.10.0/24")
    taken = {int(ipaddress.ip_address("192.168.10.1")), int(ipaddress.ip_address("192.168.10.2"))}
    free = pm.lowest_free(net, taken)
    assert ipaddress.ip_address(free) == ipaddress.ip_address("192.168.10.3")


def test_lowest_free_exhausted():
    net = pm.to_network("10.9.9.0/30")  # usable: .1, .2
    taken = {int(ipaddress.ip_address("10.9.9.1")), int(ipaddress.ip_address("10.9.9.2"))}
    assert pm.lowest_free(net, taken) is None


def test_children_split():
    net = pm.to_network("192.168.10.0/24")
    kids = pm.children(net, 25)
    assert [str(k) for k in kids] == ["192.168.10.0/25", "192.168.10.128/25"]
