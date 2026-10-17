#!/usr/bin/env python3
"""A tiny, dependency-free Modbus/TCP client to probe reachability across zones.

  modbus_client.py <host> [port] [--write ADDR VALUE]

Read:  modbus_client.py 10.10.20.11
Write: modbus_client.py 10.10.20.11 502 --write 0 1234

A short connect timeout means a firewall DROP shows up quickly as a timeout — which is the whole
point of the Purdue-DMZ lab: the SCADA zone can poll the PLC, the enterprise zone cannot.
"""
import socket
import struct
import sys


def _txn(host, port, pdu, timeout=3.0):
    with socket.create_connection((host, port), timeout=timeout) as s:
        s.settimeout(timeout)
        req = struct.pack("!HHHB", 1, 0, len(pdu) + 1, 1) + pdu
        s.sendall(req)
        hdr = s.recv(7)
        tid, pid, length, unit = struct.unpack("!HHHB", hdr)
        return s.recv(length - 1)


def read(host, port, addr=0, count=5):
    body = _txn(host, port, struct.pack("!BHH", 3, addr, count))
    fc = body[0]
    if fc & 0x80:
        return f"exception {body[1]}"
    n = body[1]
    vals = struct.unpack(f"!{n // 2}H", body[2:2 + n])
    return list(vals)


def write(host, port, addr, val):
    body = _txn(host, port, struct.pack("!BHH", 6, addr, val))
    return "ok" if body[0] == 6 else f"exception {body[1]}"


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    host = args[0]
    port = int(args[1]) if len(args) > 1 and args[1].isdigit() else 502
    try:
        if "--write" in args:
            i = args.index("--write")
            addr, val = int(args[i + 1]), int(args[i + 2])
            print(f"WRITE {val}->reg{addr} @ {host}:{port} -> {write(host, port, addr, val)}")
        else:
            print(f"READ regs @ {host}:{port} -> {read(host, port)}")
    except (socket.timeout, OSError) as e:
        print(f"UNREACHABLE {host}:{port} ({e}) — blocked by firewall or host down")
        sys.exit(2)
