"""CIDR subnet calculator (IPv4 + IPv6).

Given CIDR (e.g. 192.168.1.0/24) or IP + netmask pair
(e.g. 10.0.0.5 255.255.255.0), prints network, netmask,
wildcard, broadcast, CIDR, totals and usable host range.

Usage examples:
    python subnet_calc.py 192.168.1.0/24
    python subnet_calc.py 10.0.0.5 255.255.255.0
    python subnet_calc.py 192.168.1.0/24 --limit 10
    python subnet_calc.py 2001:db8::/32

Platform notes:
    Windows + Linux + macOS: pure-stdlib (ipaddress), no OS calls.
    On Windows (os.name == 'nt') output uses plain ASCII only;
    on Linux / macOS (sys.platform == 'darwin' for Mac) UTF-8 is fine.

Dependencies:
    Standard library only (argparse, sys, os, ipaddress).
"""

import argparse
import ipaddress
import os
import sys

# Explicit platform flags (required cross-platform handling).
IS_WINDOWS = os.name == "nt"
IS_MAC = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")


def parse_network(inputs):
    """Build an IPv4/IPv6 interface or network from 1-2 CLI tokens."""
    if len(inputs) == 1:
        token = inputs[0].strip()
        if not token:
            raise ValueError("empty input")
        try:
            # strict=False so host bits set (e.g. 10.0.0.5/24) still works.
            if "/" in token:
                return ipaddress.ip_network(token, strict=False)
            # Bare IP with no mask: treat as single host (/32 or /128).
            addr = ipaddress.ip_address(token)
            bits = 32 if addr.version == 4 else 128
            return ipaddress.ip_network("%s/%d" % (token, bits), strict=False)
        except ValueError as e:
            raise ValueError("invalid CIDR or IP %r (%s)" % (token, e))
    elif len(inputs) == 2:
        ip_str, mask_str = inputs[0].strip(), inputs[1].strip()
        try:
            # ipaddress accepts (address, netmask) tuple form.
            return ipaddress.ip_network((ip_str, mask_str), strict=False)
        except ValueError as e:
            raise ValueError(
                "invalid IP/MASK pair %r %r (%s)" % (ip_str, mask_str, e)
            )
    else:
        raise ValueError("expected 1 (CIDR) or 2 (IP MASK) arguments")


def summarize(net):
    """Return dict of display fields for an ipaddress network object."""
    total = net.num_addresses
    if net.version == 4:
        netmask = str(net.netmask)
        wildcard = str(net.hostmask)
        broadcast = str(net.broadcast_address)
    else:
        # IPv6 has no broadcast/wildcard; show n/a equivalents.
        netmask = str(net.netmask)
        wildcard = "n/a (IPv6)"
        broadcast = "n/a (IPv6)"
    if total <= 2:
        usable_count = total
        first = str(net.network_address) if total >= 1 else "n/a"
        last = str(net.broadcast_address) if total >= 1 else "n/a"
    elif net.version == 6:
        usable_count = total - 1  # no broadcast in IPv6; matches hosts()
        first = str(net.network_address + 1)
        last = str(net.broadcast_address)
    else:
        usable_count = total - 2  # exclude network + broadcast (IPv4)
        first = str(net.network_address + 1)
        last = str(net.broadcast_address - 1)
    return {
        "network": str(net.network_address),
        "netmask": netmask,
        "wildcard": wildcard,
        "broadcast": broadcast,
        "cidr": "/%d" % net.prefixlen,
        "total": total,
        "usable_count": usable_count,
        "first": first,
        "last": last,
        "version": net.version,
    }


def build_parser():
    p = argparse.ArgumentParser(
        description="CIDR subnet calculator (e.g. 192.168.1.0/24 or '10.0.0.5 255.255.255.0')."
    )
    p.add_argument(
        "inputs",
        nargs="+",
        help="CIDR like 192.168.1.0/24, or IP MASK like '10.0.0.5 255.255.255.0'.",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Show only first N usable hosts when list is large.",
    )
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)

    if args.limit is not None and args.limit < 0:
        print("error: --limit must be >= 0", file=sys.stderr)
        return 2

    try:
        net = parse_network(args.inputs)
    except ValueError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2

    info = summarize(net)

    # Explicit Windows vs POSIX newline/encoding handling.
    # print() already uses os.linesep; on Windows force ASCII-safe output.
    print("network:   %s" % info["network"])
    print("netmask:   %s" % info["netmask"])
    print("wildcard:  %s" % info["wildcard"])
    print("broadcast: %s" % info["broadcast"])
    print("cidr:      %s%s" % (info["network"], info["cidr"]))
    print("prefixlen: %s" % net.prefixlen)
    print("version:   IPv%d" % info["version"])
    print("total hosts:  %d" % info["total"])
    print("usable hosts: %d" % info["usable_count"])
    if info["total"] > 0:
        print("usable first: %s" % info["first"])
        print("usable last:  %s" % info["last"])

    # List hosts only when reasonable; otherwise require --limit.
    LIST_CAP = 1024
    if info["usable_count"] <= LIST_CAP:
        hosts = list(net.hosts())
        if not hosts and info["total"] <= 2:
            hosts = list(net)  # /31, /32, /127, /128 edge cases
        if args.limit is not None:
            hosts = hosts[: args.limit]
        print("hosts (%d shown):" % len(hosts))
        for h in hosts:
            print("  %s" % h)
    else:
        if args.limit is not None and args.limit > 0:
            shown = 0
            print("hosts (first %d of %d usable):" % (args.limit, info["usable_count"]))
            for h in net.hosts():
                if shown >= args.limit:
                    break
                print("  %s" % h)
                shown += 1
        else:
            print(
                "hosts: %d usable (too many to list; use --limit N to show first N)."
                % info["usable_count"]
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
