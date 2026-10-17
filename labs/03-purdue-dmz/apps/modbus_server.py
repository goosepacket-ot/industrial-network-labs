#!/usr/bin/env python3
"""A tiny, dependency-free Modbus/TCP server — just enough to demonstrate segmentation.

It answers Read Holding Registers (FC3) and Write Single Register (FC6) on 40 registers, and logs
the source IP of every request. In the lab you watch its log to prove which zones can reach it and
which the firewall blocks. This is a teaching stub, not a production Modbus stack.
"""
import socket
import socketserver
import struct
import sys

REGS = [i for i in range(40)]


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        peer = self.client_address[0]
        while True:
            hdr = self._recv(7)
            if not hdr:
                return
            tid, pid, length, unit = struct.unpack("!HHHB", hdr)
            body = self._recv(length - 1)
            if not body:
                return
            fc = body[0]
            resp = self._dispatch(fc, body[1:], peer)
            out = struct.pack("!HHHB", tid, 0, len(resp) + 1, unit) + resp
            self.request.sendall(out)

    def _recv(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.request.recv(n - len(buf))
            if not chunk:
                return b""
            buf += chunk
        return buf

    def _dispatch(self, fc, data, peer):
        try:
            if fc == 3:  # read holding registers
                addr, count = struct.unpack("!HH", data[:4])
                vals = REGS[addr:addr + count]
                print(f"[server] FC3 read {count}@{addr} from {peer}", flush=True)
                return struct.pack("!BB", 3, count * 2) + b"".join(struct.pack("!H", v & 0xFFFF) for v in vals)
            if fc == 6:  # write single register
                addr, val = struct.unpack("!HH", data[:4])
                if 0 <= addr < len(REGS):
                    REGS[addr] = val
                print(f"[server] FC6 WRITE {val}->reg{addr} from {peer}", flush=True)
                return struct.pack("!BHH", 6, addr, val)
            print(f"[server] unsupported FC{fc} from {peer}", flush=True)
            return struct.pack("!BB", fc | 0x80, 0x01)  # illegal function
        except Exception:
            return struct.pack("!BB", fc | 0x80, 0x04)


if __name__ == "__main__":
    host, port = "0.0.0.0", int(sys.argv[1]) if len(sys.argv) > 1 else 502
    print(f"[server] Modbus/TCP listening on {host}:{port}", flush=True)
    with socketserver.ThreadingTCPServer((host, port), Handler) as s:
        s.allow_reuse_address = True
        s.serve_forever()
