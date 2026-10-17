# Lab 01 — OSPF with BFD (sub-second failover)

Two sites (`r1`, `r2`) with two paths between them: a direct link and a backup path through `r3`.
OSPF picks the best path; **BFD** detects a link failure in well under a second, so when the primary
link drops, traffic reroutes almost immediately instead of waiting ~40 s for OSPF's dead interval.

This is the pattern behind a resilient OT WAN between substations or plants.

```
        eth1        eth1
  r1 ───────────────── r2
   │ eth2         eth2 │
   └──── r3 ───────────┘
      eth1   eth2
```

## Run

```bash
sudo containerlab deploy -t ospf-bfd.clab.yml
```

## Verify

```bash
# OSPF neighbours should be Full on both interfaces
docker exec clab-ospfbfd-r1 vtysh -c "show ip ospf neighbor"

# BFD sessions should be Up with a sub-second detect time
docker exec clab-ospfbfd-r1 vtysh -c "show bfd peers"

# r1 can reach r2's loopback
docker exec clab-ospfbfd-r1 ping -c2 10.0.0.2
```

## Demonstrate fast failover

```bash
# start a ping across the direct link path
docker exec clab-ospfbfd-r1 ping 10.0.0.2 &

# drop the direct link (r1 eth1 <-> r2 eth1)
sudo ip link set dev $(docker exec clab-ospfbfd-r1 sh -c 'echo eth1') down   # inside r1
# (or: containerlab tools disrupt — see containerlab docs)

# watch the ping: with BFD you lose ~1 packet; without it you'd lose ~40 s of traffic.
docker exec clab-ospfbfd-r1 vtysh -c "show ip route 10.0.0.2"   # now via r3
```

## Teardown

```bash
sudo containerlab destroy -t ospf-bfd.clab.yml
```
