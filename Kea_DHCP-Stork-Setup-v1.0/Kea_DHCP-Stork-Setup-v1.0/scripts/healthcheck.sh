#!/usr/bin/env bash
set -euo pipefail
echo "===== SERVICE ====="
systemctl status isc-kea-dhcp4-server --no-pager -l
echo "===== UDP/67 ====="
ss -lunp | grep ':67 '
echo "===== CONFIG ====="
kea-dhcp4 -t /etc/kea/kea-dhcp4.conf
echo "===== FULL TEST ====="
kea-dhcp4 -T /etc/kea/kea-dhcp4.conf
echo "===== CONTROL SOCKET ====="
test -S /var/run/kea/kea4-ctrl-socket && echo OK
echo "===== RECENT ERRORS ====="
journalctl -u isc-kea-dhcp4-server --since '10 minutes ago' --no-pager |
  grep -Ei 'error|fail|illegal use|no sockets' || true
