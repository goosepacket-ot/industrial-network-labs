# Lab 02 — VRRP redundant gateway

A field host points its default route at a **virtual IP** (`10.50.0.1`) shared by two routers.
`gw1` (priority 200) is master; `gw2` (priority 100) is backup. If the master dies, the backup
takes over the virtual IP and virtual MAC in a couple of seconds and the host never notices.

```
 host(10.50.0.100) ── sw(bridge) ── gw1  priority 200  ┐
                                   └ gw2  priority 100  ┘  VIP 10.50.0.1
```

## Run

```bash
sudo containerlab deploy -t vrrp.clab.yml
```

## Verify

```bash
# gw1 should be MASTER, gw2 BACKUP
docker exec clab-vrrp-gw1 vtysh -c "show vrrp"
docker exec clab-vrrp-gw2 vtysh -c "show vrrp"

# the host reaches its gateway VIP
docker exec clab-vrrp-host ping -c2 10.50.0.1
```

## Demonstrate failover

```bash
# keep pinging the VIP from the host
docker exec clab-vrrp-host ping 10.50.0.1 &

# stop the master
docker stop clab-vrrp-gw1

# within ~3 s gw2 becomes MASTER and the ping continues
docker exec clab-vrrp-gw2 vtysh -c "show vrrp"
```

## Teardown

```bash
sudo containerlab destroy -t vrrp.clab.yml
```

> VRRP in FRR needs the `vrrpd` daemon (enabled in `configs/*/daemons`) and the virtual-MAC
> macvlan support in the container kernel. On some hosts you may need to load the `macvlan`
> module. See the FRR VRRP docs if `show vrrp` reports the interface as not ready.
