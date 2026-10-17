#!/bin/sh
# Purdue-model firewall for the DMZ lab. Run inside the `fw` node.
#
# Zones:
#   eth1  Supervisory (L2)   10.10.10.0/24   SCADA/HMI   -- MAY poll the PLC
#   eth2  Control (L1)        10.10.20.0/24   PLC         -- answers only the SCADA zone
#   eth3  Enterprise (L4)     10.20.0.0/24    office      -- MUST NOT reach the PLC directly
#
# Policy: default DROP on forwarding; allow only the approved conduits; everything is logged.
set -e

echo 1 > /proc/sys/net/ipv4/ip_forward

# flush and set default-deny on the forward path
iptables -F
iptables -P FORWARD DROP
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

# CONDUIT 1: Supervisory -> Control, Modbus/TCP only
iptables -A FORWARD -s 10.10.10.0/24 -d 10.10.20.0/24 -p tcp --dport 502 -j ACCEPT

# CONDUIT 2: Control -> Supervisory return path for the historian pull (also 502) is covered by state

# EXPLICITLY DENY + LOG: Enterprise -> Control (this is the attack the lab shows being blocked)
iptables -A FORWARD -s 10.20.0.0/24 -d 10.10.20.0/24 -j LOG --log-prefix "DENY ENT->OT: "
iptables -A FORWARD -s 10.20.0.0/24 -d 10.10.20.0/24 -j DROP

# final catch-all log before the default DROP
iptables -A FORWARD -j LOG --log-prefix "DENY default: "

echo "[fw] Purdue firewall applied. FORWARD policy = DROP, Modbus allowed only from 10.10.10.0/24."
iptables -S FORWARD
