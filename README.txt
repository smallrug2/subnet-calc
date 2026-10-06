========================================
CIDR Subnet Calculator (subnet_calc.py)
========================================
Coded by: Muse Spark (Meta AI assistant)
Curated by: smallrug2
License: MIT (see LICENSE file)

WHAT IT DOES:
Computes network, netmask, wildcard, broadcast, CIDR, total hosts and
usable first/last addresses for IPv4/IPv6 CIDR or IP + MASK input.
Lists usable hosts when count <= 1024, else use --limit N.

REQUIREMENTS:
Python 3.8+ only - no extra packages needed (stdlib only).

HOW TO RUN:
python subnet_calc.py --help
python subnet_calc.py 192.168.1.0/24
python subnet_calc.py 10.0.0.5 255.255.255.0
python subnet_calc.py 192.168.1.0/24 --limit 10

PLATFORM:
Windows + Linux + Mac: yes.

CREDITS:
- Coded by Muse Spark (Meta AI assistant) for smallrug2's open-source collection.
- If this script helped you, a star on the repo is appreciated.
