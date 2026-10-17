# Lab 03 — Purdue-model segmentation with a live Modbus demo

A Linux firewall (`fw`) sits between three zones and enforces the one rule everyone claims to have
but rarely proves: **the SCADA zone may poll the PLC on Modbus/TCP, the enterprise zone may not.**
A tiny pure-Python Modbus server runs on the PLC, and a matching client runs on the other two
hosts, so you can *watch* the segmentation work instead of taking the ruleset on faith.

```
 scada 10.10.10.10 ──┐         ┌── plc 10.10.20.11  (Modbus server, FC3/FC6)
                     ├── fw ───┤
 enterprise 10.20.0.50 ┘  iptables, default DROP
```

- **Conduit (allowed):** `10.10.10.0/24 → 10.10.20.0/24` TCP/502
- **Denied + logged:** `10.20.0.0/24 → 10.10.20.0/24` (enterprise to control)
- Everything else: default DROP, logged.

The firewall policy is in [`configs/fw/firewall.sh`](configs/fw/firewall.sh); it reads like the
conduit list from a IEC 62443 zone model (see the `iec62443-zone-kit` project — this lab is the
other half of that story, the enforcement).

## Run

```bash
sudo containerlab deploy -t purdue-dmz.clab.yml
```

## Prove the segmentation

```bash
# SCADA CAN read the PLC (allowed conduit)
docker exec clab-purdue-scada python3 /modbus_client.py 10.10.20.11
#   -> READ regs @ 10.10.20.11:502 -> [0, 1, 2, 3, 4]

# SCADA can also write a register
docker exec clab-purdue-scada python3 /modbus_client.py 10.10.20.11 502 --write 0 4242

# ENTERPRISE CANNOT reach the PLC (blocked + logged)
docker exec clab-purdue-enterprise python3 /modbus_client.py 10.10.20.11
#   -> UNREACHABLE 10.10.20.11:502 (timed out) — blocked by firewall or host down
#   (exit code 2)

# see the drop logged on the firewall
docker exec clab-purdue-fw sh -c "dmesg | grep 'DENY ENT->OT' | tail"
```

## Teardown

```bash
sudo containerlab destroy -t purdue-dmz.clab.yml
```

> The Modbus server/client under [`apps/`](apps/) are dependency-free teaching stubs (≈100 lines
> each). They implement just FC3 (read) and FC6 (write) so the demo is self-contained — they are
> not a complete or production Modbus stack.
