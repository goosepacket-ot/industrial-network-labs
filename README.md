# industrial-network-labs

**Reproducible, containerlab-based network labs for OT / industrial networking — resilience and segmentation you can run on a laptop.**

Each lab is a [containerlab](https://containerlab.dev) topology plus the device configs, built around a scenario I actually care about on OT networks:

| Lab | Scenario | What it shows |
|---|---|---|
| [`01-ospf-bfd`](labs/01-ospf-bfd/) | OSPF with BFD | Sub-second failover on a dual-path OT WAN instead of ~40 s |
| [`02-vrrp-gateway`](labs/02-vrrp-gateway/) | VRRP redundant gateway | A field segment keeps its default gateway when a router dies |
| [`03-purdue-dmz`](labs/03-purdue-dmz/) | Purdue segmentation + live Modbus | A firewall that lets SCADA poll the PLC but blocks the enterprise zone — demonstrated with a real Modbus read/write |

Labs 01–02 use [FRRouting](https://frrouting.org); lab 03 uses a plain Linux firewall and a pair of ~100-line, dependency-free Modbus apps so you can see the segmentation actually stop traffic.

## Prerequisites

- Docker
- [containerlab](https://containerlab.dev/install/) (`bash -c "$(curl -sL https://get.containerlab.dev)"`)
- Linux host (or WSL2). The FRR/alpine/python images pull on first run.

## Run any lab

```bash
cd labs/01-ospf-bfd
sudo containerlab deploy -t ospf-bfd.clab.yml
# ... follow that lab's README ...
sudo containerlab destroy -t ospf-bfd.clab.yml
```

Every lab folder has its own README with the deploy command, the verification commands and a failure/failover demo to run.

## ⚠ Status: configs reviewed, full runs pending

I want to be straight about this, because in OT "it works on my slides" is not good enough:

- The **topologies and device configs are written and reviewed**, and the Modbus server/client in lab 03 are **tested and working** (pure Python, no dependencies — run them directly: `python3 labs/03-purdue-dmz/apps/modbus_server.py 1502` then point the client at it).
- The **end-to-end containerlab runs have not yet been executed in this repo's CI**, because containerlab needs Docker with privileged networking that a plain CI runner doesn't give. Image tags (FRR 9.1.0, alpine 3.20, python 3.12) and FRR syntax are pinned to current versions, but treat the first local `deploy` as the real test and open an issue if a lab needs a tweak.

This honesty is deliberate: the labs are a solid, documented starting point, not a "trust me" artifact. Corrections via PR are welcome.

## Why these labs

After 5+ years on industrial networks, the two questions that decide whether a design is any good are *"what happens when a link or a box dies?"* and *"can the thing that shouldn't talk to the PLC actually reach it?"*. These labs let you answer both with your own hands in a few minutes, for free, without touching production — which is how I think OT networking should be taught and validated.

## License

MIT — see [LICENSE](LICENSE).
