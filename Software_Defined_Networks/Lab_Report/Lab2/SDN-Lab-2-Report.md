## Topology Design
总体上，代码还是在前一实验的基础上修改。不同的是，这次使用的是三层交换机，所以说在分配同一edge switch上连接的主机IP时，不能让它们处于同一子网了（三层交换机的不同接口应该处在不同子网中）。所以应该修改IP地址的分配原则。下面给出本实验的IP地址与ASN的分配规划。
### 总体规划
- 每台交换机单独一个ASN;
- 每条`Switch-Switch`链路单独一个点对点子网（掩码`/31`）
- 每条`Host-Edge`链路单独设置一个`/24`子网
- 只有edge交换机宣告主机网段，便于包的转发；aggre和core只做中转，不宣告网段。
### ASN分配
必做题中要求每个交换机独立分配一个AS号，这在必做题的情境下也是必要的。因为在使用BGP协议的前提下，每台路由设备把自己知道的网段通过邻居层层传播出去，同时在这个路由信息里告知路由经过了哪些自治系统，也就是`AS-Path`。设备收到多个同一目的网段的路由之后，会根据一套规则设置最优路径，比如`Local Preference` `AS-Path`长度等。而BGP在默认情境下为了防止环路，**会检查收到的路由的 AS-Path，如果发现其中已经包含本机的 ASN，就认为可能形成潜在环路，因此拒绝该路由。** 这就导致如果路由传播途中经过了相同ASN的不同设备，这个包就会被丢弃。
所以，最后设计如下：

| 层级                | 设备  |   ASN |
| ----------------- | --- | ----: |
| Core              | c00 | 65000 |
| Core              | c01 | 65001 |
| Core              | c10 | 65002 |
| Core              | c11 | 65003 |
| Pod 0 Aggregation | a00 | 65100 |
| Pod 0 Aggregation | a01 | 65101 |
| Pod 0 Edge        | e00 | 65102 |
| Pod 0 Edge        | e01 | 65103 |
| Pod 1 Aggregation | a10 | 65110 |
| Pod 1 Aggregation | a11 | 65111 |
| Pod 1 Edge        | e10 | 65112 |
| Pod 1 Edge        | e11 | 65113 |
| Pod 2 Aggregation | a20 | 65120 |
| Pod 2 Aggregation | a21 | 65121 |
| Pod 2 Edge        | e20 | 65122 |
| Pod 2 Edge        | e21 | 65123 |
| Pod 3 Aggregation | a30 | 65130 |
| Pod 3 Aggregation | a31 | 65131 |
| Pod 3 Edge        | e30 | 65132 |
| Pod 3 Edge        | e31 | 65133 |
### Host网段规划
Host的IP网段设计为`10.<pod + 1>.x.0/24`，一个pod里四个主机的`x`值分别取`1,2,3,4`。比如`h000`的IP是`10.1.1.2/24`，网关就是`*.1/24`。

| Pod | Host | 所连 Edge | Host IP     | Gateway  |
| --- | ---- | ------- | ----------- | -------- |
| 0   | h000 | e00     | 10.1.1.2/24 | 10.1.1.1 |
| 0   | h001 | e00     | 10.1.2.2/24 | 10.1.2.1 |
| 0   | h010 | e01     | 10.1.3.2/24 | 10.1.3.1 |
| 0   | h011 | e01     | 10.1.4.2/24 | 10.1.4.1 |
| 1   | h100 | e10     | 10.2.1.2/24 | 10.2.1.1 |
| 1   | h101 | e10     | 10.2.2.2/24 | 10.2.2.1 |
| 1   | h110 | e11     | 10.2.3.2/24 | 10.2.3.1 |
| 1   | h111 | e11     | 10.2.4.2/24 | 10.2.4.1 |
| 2   | h200 | e20     | 10.3.1.2/24 | 10.3.1.1 |
| 2   | h201 | e20     | 10.3.2.2/24 | 10.3.2.1 |
| 2   | h210 | e21     | 10.3.3.2/24 | 10.3.3.1 |
| 2   | h211 | e21     | 10.3.4.2/24 | 10.3.4.1 |
| 3   | h300 | e30     | 10.4.1.2/24 | 10.4.1.1 |
| 3   | h301 | e30     | 10.4.2.2/24 | 10.4.2.1 |
| 3   | h310 | e31     | 10.4.3.2/24 | 10.4.3.1 |
| 3   | h311 | e31     | 10.4.4.2/24 | 10.4.4.1 |
### Edge Switch IP规划
每台edge有4个接口`Ethernet1-1/2/3/4`，1和2连接两个aggre交换机，3和4连接两个主机。`edge-aggre`用`172.16.<pod + 1>.x/31`。
例如 Pod 0的`e00`的各个接口IP设计如下：
- `Eth1-1 = 172.16.1.0/31`
- `Eth1-2 = 172.16.1.4/31`
- `Eth1-3 = 10.1.1.1/24`
- `Eth1-4 = 10.1.2.1/24`
### Aggregation Switch IP规划
每台 aggregation 也有 4 个接口：
- `Ethernet1-1`、`Ethernet1-2` 连接两个 edge
- `Ethernet1-3`、`Ethernet1-4` 连接两个 core
- `aggregation-edge` 侧继续用 `172.16.P.x/31`
- `aggregation-core` 侧统一用 `172.17.P.x/31`
### Core Switch IP规划
- 每台 core 有 4 个接口，分别接 4 个 pod。core 到 aggregation 的链路统一用 `172.17.<pod + 1>.x/31`。
- 每个 pod 对应 core 上一个固定接口：
    - Pod 0 对应 `Eth1-1`
    - Pod 1 对应 `Eth1-2`
    - Pod 2 对应 `Eth1-3`
    - Pod 3 对应 `Eth1-4`
- 例如`c00`
    - `Eth1-1 = 172.17.1.1/31`
    - `Eth1-2 = 172.17.2.1/31`
    - `Eth1-3 = 172.17.3.1/31`
    - `Eth1-4 = 172.17.4.1/31`
### IP 规划总结

| 链路类型                 | 地址范围                       | 说明                        |
| -------------------- | -------------------------- | ------------------------- |
| Host <-> Edge        | `10.<pod+1>.<subnet>.0/24` | 每条 host-edge 链路单独一个 `/24` |
| Edge <-> Aggregation | `172.16.<pod+1>.x/31`      | pod 内部点到点链路               |
| Aggregation <-> Core | `172.17.<pod+1>.x/31`      | pod 到 core 的点到点链路         |

| 设备  | ASN   | Ethernet1-1   | Ethernet1-2   | Ethernet1-3   | Ethernet1-4   |
| --- | ----- | ------------- | ------------- | ------------- | ------------- |
| c00 | 65000 | 172.17.1.1/31 | 172.17.2.1/31 | 172.17.3.1/31 | 172.17.4.1/31 |
| c01 | 65001 | 172.17.1.5/31 | 172.17.2.5/31 | 172.17.3.5/31 | 172.17.4.5/31 |
| c10 | 65002 | 172.17.1.3/31 | 172.17.2.3/31 | 172.17.3.3/31 | 172.17.4.3/31 |
| c11 | 65003 | 172.17.1.7/31 | 172.17.2.7/31 | 172.17.3.7/31 | 172.17.4.7/31 |
| a00 | 65100 | 172.16.1.1/31 | 172.16.1.3/31 | 172.17.1.0/31 | 172.17.1.2/31 |
| a01 | 65101 | 172.16.1.5/31 | 172.16.1.7/31 | 172.17.1.4/31 | 172.17.1.6/31 |
| a10 | 65110 | 172.16.2.1/31 | 172.16.2.3/31 | 172.17.2.0/31 | 172.17.2.2/31 |
| a11 | 65111 | 172.16.2.5/31 | 172.16.2.7/31 | 172.17.2.4/31 | 172.17.2.6/31 |
| a20 | 65120 | 172.16.3.1/31 | 172.16.3.3/31 | 172.17.3.0/31 | 172.17.3.2/31 |
| a21 | 65121 | 172.16.3.5/31 | 172.16.3.7/31 | 172.17.3.4/31 | 172.17.3.6/31 |
| a30 | 65130 | 172.16.4.1/31 | 172.16.4.3/31 | 172.17.4.0/31 | 172.17.4.2/31 |
| a31 | 65131 | 172.16.4.5/31 | 172.16.4.7/31 | 172.17.4.4/31 | 172.17.4.6/31 |
| e00 | 65102 | 172.16.1.0/31 | 172.16.1.4/31 | 10.1.1.1/24   | 10.1.2.1/24   |
| e01 | 65103 | 172.16.1.2/31 | 172.16.1.6/31 | 10.1.3.1/24   | 10.1.4.1/24   |
| e10 | 65112 | 172.16.2.0/31 | 172.16.2.4/31 | 10.2.1.1/24   | 10.2.2.1/24   |
| e11 | 65113 | 172.16.2.2/31 | 172.16.2.6/31 | 10.2.3.1/24   | 10.2.4.1/24   |
| e20 | 65122 | 172.16.3.0/31 | 172.16.3.4/31 | 10.3.1.1/24   | 10.3.2.1/24   |
| e21 | 65123 | 172.16.3.2/31 | 172.16.3.6/31 | 10.3.3.1/24   | 10.3.4.1/24   |
| e30 | 65132 | 172.16.4.0/31 | 172.16.4.4/31 | 10.4.1.1/24   | 10.4.2.1/24   |
| e31 | 65133 | 172.16.4.2/31 | 172.16.4.6/31 | 10.4.3.1/24   | 10.4.4.1/24   |
## Code Implementation
### Phase 1：必做题
#### `main.py`
```python
from frrnet import frrnet_main
from frrnet.topo import FrrTopo

# from frr_compat import patch_frr_search_path


class FatTreeTopo(FrrTopo):
    def build(self, k=4):
        if k % 2 != 0:
            raise ValueError("k must be even")

        pods = k
        half = k // 2

        core = []
        for i in range(half):
            row = []
            for j in range(half):
                switch = self.addSwitch(f"c{i}{j}", daemons=["bgpd"])
                row.append(switch)
            core.append(row)

        for p in range(pods):
            aggre = []
            edge = []

            for a in range(half):
                aggre.append(self.addSwitch(f"a{p}{a}", daemons=["bgpd"]))

            for e in range(half):
                edge.append(self.addSwitch(f"e{p}{e}", daemons=["bgpd"]))

            for a_idx, agg in enumerate(aggre):
                for e_idx, edg in enumerate(edge):
                    self.addLink(
                        agg,
                        edg,
                        intf1=f"Ethernet1-{e_idx + 1}",
                        intf2=f"Ethernet1-{a_idx + 1}",
                        bw=10, # edge and aggre之间设置带宽
                        delay="10ms",
                    )

            for e_idx, edg in enumerate(edge):
                for h_idx in range(half):
                    subnet_id = e_idx * half + h_idx + 1
                    subnet = f"10.{p + 1}.{subnet_id}"
                    gateway = f"{subnet}.1"
                    host = self.addHost(
                        f"h{p}{e_idx}{h_idx}",
                        ip=f"{subnet}.{h_idx + 2}/24",
                        defaultRoute=f"via {gateway}",
                    )
                    self.addLink(
                        edg,
                        host,
                        intf1=f"Ethernet1-{half + h_idx + 1}",
                    )

            for a_idx, agg in enumerate(aggre):
                for c_idx in range(half):
                    self.addLink(
                        agg,
                        core[c_idx][a_idx],
                        intf1=f"Ethernet1-{half + c_idx + 1}",
                        intf2=f"Ethernet1-{p + 1}",
                        bw=10, # core and aggre交换机之间的链路设置带宽
                        delay="10ms",
                    )


if __name__ == "__main__":
    # patch_frr_search_path()
    frrnet_main(FatTreeTopo)

```

#### config文件
为了让以上的IP规划和ASN设置能真正作用到网络中，需要设置各种config文件。下面给出几个具有代表性的交换机的配置文件示例（开启ECMP前）。
##### `e00`
```conf
frr defaults datacenter
!
!
interface Ethernet1-1
  ip address 172.16.1.0/31
!
interface Ethernet1-2
  ip address 172.16.1.4/31
!
interface Ethernet1-3
  ip address 10.1.1.1/24
!
interface Ethernet1-4
  ip address 10.1.2.1/24
!
!
router bgp 65102
  neighbor 172.16.1.1 remote-as 65100
  neighbor 172.16.1.5 remote-as 65101
  network 10.1.1.0/24
  network 10.1.2.0/24
```
##### `a00`
```conf
frr defaults datacenter
!
!
interface Ethernet1-1
  ip address 172.16.1.1/31
!
interface Ethernet1-2
  ip address 172.16.1.3/31
!
interface Ethernet1-3
  ip address 172.17.1.0/31
!
interface Ethernet1-4
  ip address 172.17.1.2/31
!
!
router bgp 65100
  neighbor 172.16.1.0 remote-as 65102
  neighbor 172.16.1.2 remote-as 65103
  neighbor 172.17.1.1 remote-as 65000
  neighbor 172.17.1.3 remote-as 65002

```
##### `c00`
```conf
frr defaults datacenter
!
!
interface Ethernet1-1
  ip address 172.17.1.1/31
!
interface Ethernet1-2
  ip address 172.17.2.1/31
!
interface Ethernet1-3
  ip address 172.17.3.1/31
!
interface Ethernet1-4
  ip address 172.17.4.1/31
!
!
router bgp 65000
  neighbor 172.17.1.0 remote-as 65100
  neighbor 172.17.2.0 remote-as 65110
  neighbor 172.17.3.0 remote-as 65120
  neighbor 172.17.4.0 remote-as 65130

```
#### 结果
`sudo uv run fattree/main.py`运行命令后，建立网络。
>首先在不开multipath的情况下运行。
##### 连通性
首先执行`pingall`命令，显示全通。
```bash
mininet> pingall
*** Ping: testing ping reachability
h000 -> h001 h010 h011 h100 h101 h110 h111 h200 h201 h210 h211 h300 h301 h310 h311 
h001 -> h000 h010 h011 h100 h101 h110 h111 h200 h201 h210 h211 h300 h301 h310 h311 
h010 -> h000 h001 h011 h100 h101 h110 h111 h200 h201 h210 h211 h300 h301 h310 h311 
h011 -> h000 h001 h010 h100 h101 h110 h111 h200 h201 h210 h211 h300 h301 h310 h311 
h100 -> h000 h001 h010 h011 h101 h110 h111 h200 h201 h210 h211 h300 h301 h310 h311 
h101 -> h000 h001 h010 h011 h100 h110 h111 h200 h201 h210 h211 h300 h301 h310 h311 
h110 -> h000 h001 h010 h011 h100 h101 h111 h200 h201 h210 h211 h300 h301 h310 h311 
h111 -> h000 h001 h010 h011 h100 h101 h110 h200 h201 h210 h211 h300 h301 h310 h311 
h200 -> h000 h001 h010 h011 h100 h101 h110 h111 h201 h210 h211 h300 h301 h310 h311 
h201 -> h000 h001 h010 h011 h100 h101 h110 h111 h200 h210 h211 h300 h301 h310 h311 
h210 -> h000 h001 h010 h011 h100 h101 h110 h111 h200 h201 h211 h300 h301 h310 h311 
h211 -> h000 h001 h010 h011 h100 h101 h110 h111 h200 h201 h210 h300 h301 h310 h311 
h300 -> h000 h001 h010 h011 h100 h101 h110 h111 h200 h201 h210 h211 h301 h310 h311 
h301 -> h000 h001 h010 h011 h100 h101 h110 h111 h200 h201 h210 h211 h300 h310 h311 
h310 -> h000 h001 h010 h011 h100 h101 h110 h111 h200 h201 h210 h211 h300 h301 h311 
h311 -> h000 h001 h010 h011 h100 h101 h110 h111 h200 h201 h210 h211 h300 h301 h310 
*** Results: 0% dropped (240/240 received)
mininet> 
```
##### BGP邻居状态信息表
然后查看各交换机的BGP neighbor信息表。
```bash
mininet> e00 show ip bgp neighbors
BGP neighbor is 172.16.1.1, remote AS 65100, local AS 65102, external link
  Local Role: undefined
  Remote Role: undefined
Hostname: ziyu-dell
  BGP version 4, remote router ID 172.17.1.2, local router ID 172.16.1.4
  BGP state = Established, up for 00:32:53
  Last read 00:00:02, Last write 00:00:02
  Hold time is 9 seconds, keepalive interval is 3 seconds
  Configured hold time is 9 seconds, keepalive interval is 3 seconds
  Configured tcp-mss is 0, synced tcp-mss is 1448
  Configured conditional advertisements interval is 60 seconds
  Neighbor capabilities:
    4 Byte AS: advertised and received
    Extended Message: advertised and received
    AddPath:
      IPv4 Unicast: RX advertised and received
    Paths-Limit:
      IPv4 Unicast: advertised (0) and received (0)
    Dynamic: advertised and received
    Long-lived Graceful Restart: advertised and received
      Address families by peer:
    Route refresh: advertised and received
    Enhanced Route Refresh: advertised and received
    Address Family IPv4 Unicast: advertised and received
    Hostname Capability: advertised (name: ziyu-dell,domain name: n/a) received (name: ziyu-dell,domain name: n/a)
    Version Capability: advertised software version (FRRouting/10.6.0) received software version (FRRouting/10.6.0)
    Link-Local Next Hop Capability: not advertised not received
    Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Address families by peer:
            Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Peer has restarted (R-bit is set)
      Peer has restarted (N-bit is set)
      Address families by peer:
        none
  Graceful restart information:
    End-of-RIB send: IPv4 Unicast
    End-of-RIB received: IPv4 Unicast
    Local GR Mode: Helper*
    Remote GR Mode: Helper

    R bit: True
    N bit: True
    Timers:
      Configured Restart Time(sec): 120
      Received Restart Time(sec): 120
      Configured LLGR Stale Path Time(sec): 0
    IPv4 Unicast:
      F bit: False
      End-of-RIB sent: Yes
      End-of-RIB sent after update: No
      End-of-RIB received: Yes
      Timers:
        Configured Stale Path Time(sec): 360
        LLGR Stale Path Time(sec): 0
  Message statistics:
    Inq depth is 0
    Outq depth is 0
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:                9         15
    Keepalives:           658        658
    Route Refresh:          0          0
    Capability:             0          0
    Total:                668        674

  Prefix statistics:
    Inbound filtered: 0
    AS-PATH loop: 14
    Originator loop: 0
    Cluster loop: 0
    Invalid next-hop: 0
    Withdrawn: 0
    Attributes discarded: 0

  Minimum time between advertisement runs is 0 seconds
  Update delay timer is 0 seconds (remaining: 0)

 For address family: IPv4 Unicast
  Update group 1, subgroup 2
  Packet Queue length 0
  Community attribute sent to this neighbor(all)
  14 accepted, 16 sent prefixes

  Connections established 1; dropped 0
  Last reset 00:32:54,  No path to specified Neighbor (FRRouting/10.6.0)
  External BGP neighbor may be up to 1 hops away.
Local host: 172.16.1.0, Local port: 38494
Foreign host: 172.16.1.1, Foreign port: 179
Nexthop: 172.16.1.0
Nexthop global: fe80::e0a2:b0ff:feec:8ba8
Nexthop local: fe80::e0a2:b0ff:feec:8ba8
BGP connection: shared network
BGP Connect Retry Timer in Seconds: 10
Estimated round trip time: 24 ms
Read thread: on  Write thread: on  FD used: 27

BGP neighbor is 172.16.1.5, remote AS 65101, local AS 65102, external link
  Local Role: undefined
  Remote Role: undefined
Hostname: ziyu-dell
  BGP version 4, remote router ID 172.17.1.6, local router ID 172.16.1.4
  BGP state = Established, up for 00:32:53
  Last read 00:00:02, Last write 00:00:02
  Hold time is 9 seconds, keepalive interval is 3 seconds
  Configured hold time is 9 seconds, keepalive interval is 3 seconds
  Configured tcp-mss is 0, synced tcp-mss is 1448
  Configured conditional advertisements interval is 60 seconds
  Neighbor capabilities:
    4 Byte AS: advertised and received
    Extended Message: advertised and received
    AddPath:
      IPv4 Unicast: RX advertised and received
    Paths-Limit:
      IPv4 Unicast: advertised (0) and received (0)
    Dynamic: advertised and received
    Long-lived Graceful Restart: advertised and received
      Address families by peer:
    Route refresh: advertised and received
    Enhanced Route Refresh: advertised and received
    Address Family IPv4 Unicast: advertised and received
    Hostname Capability: advertised (name: ziyu-dell,domain name: n/a) received (name: ziyu-dell,domain name: n/a)
    Version Capability: advertised software version (FRRouting/10.6.0) received software version (FRRouting/10.6.0)
    Link-Local Next Hop Capability: not advertised not received
    Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Address families by peer:
            Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Peer has restarted (R-bit is set)
      Peer has restarted (N-bit is set)
      Address families by peer:
        none
  Graceful restart information:
    End-of-RIB send: IPv4 Unicast
    End-of-RIB received: IPv4 Unicast
    Local GR Mode: Helper*
    Remote GR Mode: Helper

    R bit: True
    N bit: True
    Timers:
      Configured Restart Time(sec): 120
      Received Restart Time(sec): 120
      Configured LLGR Stale Path Time(sec): 0
    IPv4 Unicast:
      F bit: False
      End-of-RIB sent: Yes
      End-of-RIB sent after update: No
      End-of-RIB received: Yes
      Timers:
        Configured Stale Path Time(sec): 360
        LLGR Stale Path Time(sec): 0
  Message statistics:
    Inq depth is 0
    Outq depth is 0
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:                9         10
    Keepalives:           658        658
    Route Refresh:          0          0
    Capability:             0          0
    Total:                668        669

  Prefix statistics:
    Inbound filtered: 0
    AS-PATH loop: 4
    Originator loop: 0
    Cluster loop: 0
    Invalid next-hop: 0
    Withdrawn: 0
    Attributes discarded: 0

  Minimum time between advertisement runs is 0 seconds
  Update delay timer is 0 seconds (remaining: 0)

 For address family: IPv4 Unicast
  Update group 1, subgroup 2
  Packet Queue length 0
  Community attribute sent to this neighbor(all)
  14 accepted, 16 sent prefixes

  Connections established 1; dropped 0
  Last reset 00:32:54,  No path to specified Neighbor (FRRouting/10.6.0)
  External BGP neighbor may be up to 1 hops away.
Local host: 172.16.1.4, Local port: 51050
Foreign host: 172.16.1.5, Foreign port: 179
Nexthop: 172.16.1.4
Nexthop global: fe80::c86d:65ff:fe43:571b
Nexthop local: fe80::c86d:65ff:fe43:571b
BGP connection: shared network
BGP Connect Retry Timer in Seconds: 10
Estimated round trip time: 20 ms
Read thread: on  Write thread: on  FD used: 28
```
从e00的邻居状态信息表可以看到，**e00 的两个 BGP 邻居都已经成功建起来了（a00和a01），而且在正常交换路由。**
```bash
mininet> a00 show ip bgp neighbors
BGP neighbor is 172.16.1.0, remote AS 65102, local AS 65100, external link
  Local Role: undefined
  Remote Role: undefined
Hostname: ziyu-dell
  BGP version 4, remote router ID 172.16.1.4, local router ID 172.17.1.2
  BGP state = Established, up for 00:38:42
  Last read 00:00:03, Last write 00:00:03
  Hold time is 9 seconds, keepalive interval is 3 seconds
  Configured hold time is 9 seconds, keepalive interval is 3 seconds
  Configured tcp-mss is 0, synced tcp-mss is 1448
  Configured conditional advertisements interval is 60 seconds
  Neighbor capabilities:
    4 Byte AS: advertised and received
    Extended Message: advertised and received
    AddPath:
      IPv4 Unicast: RX advertised and received
    Paths-Limit:
      IPv4 Unicast: advertised (0) and received (0)
    Dynamic: advertised and received
    Long-lived Graceful Restart: advertised and received
      Address families by peer:
    Route refresh: advertised and received
    Enhanced Route Refresh: advertised and received
    Address Family IPv4 Unicast: advertised and received
    Hostname Capability: advertised (name: ziyu-dell,domain name: n/a) received (name: ziyu-dell,domain name: n/a)
    Version Capability: advertised software version (FRRouting/10.6.0) received software version (FRRouting/10.6.0)
    Link-Local Next Hop Capability: not advertised not received
    Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Address families by peer:
            Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Peer has restarted (R-bit is set)
      Peer has restarted (N-bit is set)
      Address families by peer:
        none
  Graceful restart information:
    End-of-RIB send: IPv4 Unicast
    End-of-RIB received: IPv4 Unicast
    Local GR Mode: Helper*
    Remote GR Mode: Helper

    R bit: True
    N bit: True
    Timers:
      Configured Restart Time(sec): 120
      Received Restart Time(sec): 120
      Configured LLGR Stale Path Time(sec): 0
    IPv4 Unicast:
      F bit: False
      End-of-RIB sent: Yes
      End-of-RIB sent after update: No
      End-of-RIB received: Yes
      Timers:
        Configured Stale Path Time(sec): 360
        LLGR Stale Path Time(sec): 0
  Message statistics:
    Inq depth is 0
    Outq depth is 0
                         Sent       Rcvd
    Opens:                  2          1
    Notifications:          0          0
    Updates:               15          9
    Keepalives:           774        774
    Route Refresh:          0          0
    Capability:             0          0
    Total:                791        784

  Prefix statistics:
    Inbound filtered: 0
    AS-PATH loop: 2
    Originator loop: 0
    Cluster loop: 0
    Invalid next-hop: 0
    Withdrawn: 0
    Attributes discarded: 0

  Minimum time between advertisement runs is 0 seconds
  Update delay timer is 0 seconds (remaining: 0)

 For address family: IPv4 Unicast
  Update group 1, subgroup 1
  Packet Queue length 0
  Community attribute sent to this neighbor(all)
  14 accepted, 16 sent prefixes

  Connections established 1; dropped 0
  Last reset 00:38:45,  No path to specified Neighbor (FRRouting/10.6.0)
  External BGP neighbor may be up to 1 hops away.
Local host: 172.16.1.1, Local port: 179
Foreign host: 172.16.1.0, Foreign port: 38494
Nexthop: 172.16.1.1
Nexthop global: fe80::1092:38ff:fe6b:1944
Nexthop local: fe80::1092:38ff:fe6b:1944
BGP connection: shared network
BGP Connect Retry Timer in Seconds: 10
Estimated round trip time: 20 ms
Read thread: on  Write thread: on  FD used: 27

BGP neighbor is 172.16.1.2, remote AS 65103, local AS 65100, external link
  Local Role: undefined
  Remote Role: undefined
Hostname: ziyu-dell
  BGP version 4, remote router ID 172.16.1.6, local router ID 172.17.1.2
  BGP state = Established, up for 00:38:42
  Last read 00:00:02, Last write 00:00:02
  Hold time is 9 seconds, keepalive interval is 3 seconds
  Configured hold time is 9 seconds, keepalive interval is 3 seconds
  Configured tcp-mss is 0, synced tcp-mss is 1448
  Configured conditional advertisements interval is 60 seconds
  Neighbor capabilities:
    4 Byte AS: advertised and received
    Extended Message: advertised and received
    AddPath:
      IPv4 Unicast: RX advertised and received
    Paths-Limit:
      IPv4 Unicast: advertised (0) and received (0)
    Dynamic: advertised and received
    Long-lived Graceful Restart: advertised and received
      Address families by peer:
    Route refresh: advertised and received
    Enhanced Route Refresh: advertised and received
    Address Family IPv4 Unicast: advertised and received
    Hostname Capability: advertised (name: ziyu-dell,domain name: n/a) received (name: ziyu-dell,domain name: n/a)
    Version Capability: advertised software version (FRRouting/10.6.0) received software version (FRRouting/10.6.0)
    Link-Local Next Hop Capability: not advertised not received
    Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Address families by peer:
            Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Peer has restarted (R-bit is set)
      Peer has restarted (N-bit is set)
      Address families by peer:
        none
  Graceful restart information:
    End-of-RIB send: IPv4 Unicast
    End-of-RIB received: IPv4 Unicast
    Local GR Mode: Helper*
    Remote GR Mode: Helper

    R bit: True
    N bit: True
    Timers:
      Configured Restart Time(sec): 120
      Received Restart Time(sec): 120
      Configured LLGR Stale Path Time(sec): 0
    IPv4 Unicast:
      F bit: False
      End-of-RIB sent: Yes
      End-of-RIB sent after update: No
      End-of-RIB received: Yes
      Timers:
        Configured Stale Path Time(sec): 360
        LLGR Stale Path Time(sec): 0
  Message statistics:
    Inq depth is 0
    Outq depth is 0
                         Sent       Rcvd
    Opens:                  2          1
    Notifications:          0          0
    Updates:               15          9
    Keepalives:           774        774
    Route Refresh:          0          0
    Capability:             0          0
    Total:                791        784

  Prefix statistics:
    Inbound filtered: 0
    AS-PATH loop: 2
    Originator loop: 0
    Cluster loop: 0
    Invalid next-hop: 0
    Withdrawn: 0
    Attributes discarded: 0

  Minimum time between advertisement runs is 0 seconds
  Update delay timer is 0 seconds (remaining: 0)

 For address family: IPv4 Unicast
  Update group 1, subgroup 1
  Packet Queue length 0
  Community attribute sent to this neighbor(all)
  14 accepted, 16 sent prefixes

  Connections established 1; dropped 0
  Last reset 00:38:45,  No path to specified Neighbor (FRRouting/10.6.0)
  External BGP neighbor may be up to 1 hops away.
Local host: 172.16.1.3, Local port: 179
Foreign host: 172.16.1.2, Foreign port: 59648
Nexthop: 172.16.1.3
Nexthop global: fe80::40c5:7eff:fe96:9ab7
Nexthop local: fe80::40c5:7eff:fe96:9ab7
BGP connection: shared network
BGP Connect Retry Timer in Seconds: 10
Estimated round trip time: 20 ms
Read thread: on  Write thread: on  FD used: 28

BGP neighbor is 172.17.1.1, remote AS 65000, local AS 65100, external link
  Local Role: undefined
  Remote Role: undefined
Hostname: ziyu-dell
  BGP version 4, remote router ID 172.17.4.1, local router ID 172.17.1.2
  BGP state = Established, up for 00:38:43
  Last read 00:00:00, Last write 00:00:00
  Hold time is 9 seconds, keepalive interval is 3 seconds
  Configured hold time is 9 seconds, keepalive interval is 3 seconds
  Configured tcp-mss is 0, synced tcp-mss is 1448
  Configured conditional advertisements interval is 60 seconds
  Neighbor capabilities:
    4 Byte AS: advertised and received
    Extended Message: advertised and received
    AddPath:
      IPv4 Unicast: RX advertised and received
    Paths-Limit:
      IPv4 Unicast: advertised (0) and received (0)
    Dynamic: advertised and received
    Long-lived Graceful Restart: advertised and received
      Address families by peer:
    Route refresh: advertised and received
    Enhanced Route Refresh: advertised and received
    Address Family IPv4 Unicast: advertised and received
    Hostname Capability: advertised (name: ziyu-dell,domain name: n/a) received (name: ziyu-dell,domain name: n/a)
    Version Capability: advertised software version (FRRouting/10.6.0) received software version (FRRouting/10.6.0)
    Link-Local Next Hop Capability: not advertised not received
    Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Address families by peer:
            Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Peer has restarted (R-bit is set)
      Peer has restarted (N-bit is set)
      Address families by peer:
        none
  Graceful restart information:
    End-of-RIB send: IPv4 Unicast
    End-of-RIB received: IPv4 Unicast
    Local GR Mode: Helper*
    Remote GR Mode: Helper

    R bit: True
    N bit: True
    Timers:
      Configured Restart Time(sec): 120
      Received Restart Time(sec): 120
      Configured LLGR Stale Path Time(sec): 0
    IPv4 Unicast:
      F bit: False
      End-of-RIB sent: Yes
      End-of-RIB sent after update: No
      End-of-RIB received: Yes
      Timers:
        Configured Stale Path Time(sec): 360
        LLGR Stale Path Time(sec): 0
  Message statistics:
    Inq depth is 0
    Outq depth is 0
                         Sent       Rcvd
    Opens:                  2          1
    Notifications:          0          0
    Updates:               15         16
    Keepalives:           775        775
    Route Refresh:          0          0
    Capability:             0          0
    Total:                792        792

  Prefix statistics:
    Inbound filtered: 0
    AS-PATH loop: 16
    Originator loop: 0
    Cluster loop: 0
    Invalid next-hop: 0
    Withdrawn: 0
    Attributes discarded: 0

  Minimum time between advertisement runs is 0 seconds
  Update delay timer is 0 seconds (remaining: 0)

 For address family: IPv4 Unicast
  Update group 1, subgroup 1
  Packet Queue length 0
  Community attribute sent to this neighbor(all)
  12 accepted, 16 sent prefixes

  Connections established 1; dropped 0
  Last reset 00:38:45,  No path to specified Neighbor (FRRouting/10.6.0)
  External BGP neighbor may be up to 1 hops away.
Local host: 172.17.1.0, Local port: 179
Foreign host: 172.17.1.1, Foreign port: 50484
Nexthop: 172.17.1.0
Nexthop global: fe80::685b:b2ff:fea0:81be
Nexthop local: fe80::685b:b2ff:fea0:81be
BGP connection: shared network
BGP Connect Retry Timer in Seconds: 10
Estimated round trip time: 20 ms
Read thread: on  Write thread: on  FD used: 29

BGP neighbor is 172.17.1.3, remote AS 65002, local AS 65100, external link
  Local Role: undefined
  Remote Role: undefined
Hostname: ziyu-dell
  BGP version 4, remote router ID 172.17.4.3, local router ID 172.17.1.2
  BGP state = Established, up for 00:38:42
  Last read 00:00:00, Last write 00:00:00
  Hold time is 9 seconds, keepalive interval is 3 seconds
  Configured hold time is 9 seconds, keepalive interval is 3 seconds
  Configured tcp-mss is 0, synced tcp-mss is 1448
  Configured conditional advertisements interval is 60 seconds
  Neighbor capabilities:
    4 Byte AS: advertised and received
    Extended Message: advertised and received
    AddPath:
      IPv4 Unicast: RX advertised and received
    Paths-Limit:
      IPv4 Unicast: advertised (0) and received (0)
    Dynamic: advertised and received
    Long-lived Graceful Restart: advertised and received
      Address families by peer:
    Route refresh: advertised and received
    Enhanced Route Refresh: advertised and received
    Address Family IPv4 Unicast: advertised and received
    Hostname Capability: advertised (name: ziyu-dell,domain name: n/a) received (name: ziyu-dell,domain name: n/a)
    Version Capability: advertised software version (FRRouting/10.6.0) received software version (FRRouting/10.6.0)
    Link-Local Next Hop Capability: not advertised not received
    Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Address families by peer:
            Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Peer has restarted (R-bit is set)
      Peer has restarted (N-bit is set)
      Address families by peer:
        none
  Graceful restart information:
    End-of-RIB send: IPv4 Unicast
    End-of-RIB received: IPv4 Unicast
    Local GR Mode: Helper*
    Remote GR Mode: Helper

    R bit: True
    N bit: True
    Timers:
      Configured Restart Time(sec): 120
      Received Restart Time(sec): 120
      Configured LLGR Stale Path Time(sec): 0
    IPv4 Unicast:
      F bit: False
      End-of-RIB sent: Yes
      End-of-RIB sent after update: No
      End-of-RIB received: Yes
      Timers:
        Configured Stale Path Time(sec): 360
        LLGR Stale Path Time(sec): 0
  Message statistics:
    Inq depth is 0
    Outq depth is 0
                         Sent       Rcvd
    Opens:                  2          1
    Notifications:          1          0
    Updates:               15         16
    Keepalives:           775        775
    Route Refresh:          0          0
    Capability:             0          0
    Total:                793        792

  Prefix statistics:
    Inbound filtered: 0
    AS-PATH loop: 16
    Originator loop: 0
    Cluster loop: 0
    Invalid next-hop: 0
    Withdrawn: 0
    Attributes discarded: 0

  Minimum time between advertisement runs is 0 seconds
  Update delay timer is 0 seconds (remaining: 0)

 For address family: IPv4 Unicast
  Update group 1, subgroup 1
  Packet Queue length 0
  Community attribute sent to this neighbor(all)
  12 accepted, 16 sent prefixes

  Connections established 1; dropped 0
  Last reset 00:38:45,  Cease: connection collision (FRRouting/10.6.0)
  External BGP neighbor may be up to 1 hops away.
Local host: 172.17.1.2, Local port: 179
Foreign host: 172.17.1.3, Foreign port: 42950
Nexthop: 172.17.1.2
Nexthop global: fe80::841f:56ff:fe9a:5766
Nexthop local: fe80::841f:56ff:fe9a:5766
BGP connection: shared network
BGP Connect Retry Timer in Seconds: 10
Estimated round trip time: 20 ms
Read thread: on  Write thread: on  FD used: 31

```
```bash
mininet> c00 show ip bgp neighbors
BGP neighbor is 172.17.1.0, remote AS 65100, local AS 65000, external link
  Local Role: undefined
  Remote Role: undefined
Hostname: ziyu-dell
  BGP version 4, remote router ID 172.17.1.2, local router ID 172.17.4.1
  BGP state = Established, up for 00:43:15
  Last read 00:00:02, Last write 00:00:02
  Hold time is 9 seconds, keepalive interval is 3 seconds
  Configured hold time is 9 seconds, keepalive interval is 3 seconds
  Configured tcp-mss is 0, synced tcp-mss is 1448
  Configured conditional advertisements interval is 60 seconds
  Neighbor capabilities:
    4 Byte AS: advertised and received
    Extended Message: advertised and received
    AddPath:
      IPv4 Unicast: RX advertised and received
    Paths-Limit:
      IPv4 Unicast: advertised (0) and received (0)
    Dynamic: advertised and received
    Long-lived Graceful Restart: advertised and received
      Address families by peer:
    Route refresh: advertised and received
    Enhanced Route Refresh: advertised and received
    Address Family IPv4 Unicast: advertised and received
    Hostname Capability: advertised (name: ziyu-dell,domain name: n/a) received (name: ziyu-dell,domain name: n/a)
    Version Capability: advertised software version (FRRouting/10.6.0) received software version (FRRouting/10.6.0)
    Link-Local Next Hop Capability: not advertised not received
    Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Address families by peer:
            Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Peer has restarted (R-bit is set)
      Peer has restarted (N-bit is set)
      Address families by peer:
        none
  Graceful restart information:
    End-of-RIB send: IPv4 Unicast
    End-of-RIB received: IPv4 Unicast
    Local GR Mode: Helper*
    Remote GR Mode: Helper

    R bit: True
    N bit: True
    Timers:
      Configured Restart Time(sec): 120
      Received Restart Time(sec): 120
      Configured LLGR Stale Path Time(sec): 0
    IPv4 Unicast:
      F bit: False
      End-of-RIB sent: Yes
      End-of-RIB sent after update: No
      End-of-RIB received: Yes
      Timers:
        Configured Stale Path Time(sec): 360
        LLGR Stale Path Time(sec): 0
  Message statistics:
    Inq depth is 0
    Outq depth is 0
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:               16         15
    Keepalives:           865        865
    Route Refresh:          0          0
    Capability:             0          0
    Total:                882        881

  Prefix statistics:
    Inbound filtered: 0
    AS-PATH loop: 12
    Originator loop: 0
    Cluster loop: 0
    Invalid next-hop: 0
    Withdrawn: 0
    Attributes discarded: 0

  Minimum time between advertisement runs is 0 seconds
  Update delay timer is 0 seconds (remaining: 0)

 For address family: IPv4 Unicast
  Update group 1, subgroup 1
  Packet Queue length 0
  Community attribute sent to this neighbor(all)
  4 accepted, 16 sent prefixes

  Connections established 1; dropped 0
  Last reset 00:43:16,  No path to specified Neighbor (FRRouting/10.6.0)
  External BGP neighbor may be up to 1 hops away.
Local host: 172.17.1.1, Local port: 50484
Foreign host: 172.17.1.0, Foreign port: 179
Nexthop: 172.17.1.1
Nexthop global: fe80::fcaa:b6ff:feac:64c4
Nexthop local: fe80::fcaa:b6ff:feac:64c4
BGP connection: shared network
BGP Connect Retry Timer in Seconds: 10
Estimated round trip time: 35 ms
Read thread: on  Write thread: on  FD used: 27

BGP neighbor is 172.17.2.0, remote AS 65110, local AS 65000, external link
  Local Role: undefined
  Remote Role: undefined
Hostname: ziyu-dell
  BGP version 4, remote router ID 172.17.2.2, local router ID 172.17.4.1
  BGP state = Established, up for 00:43:15
  Last read 00:00:02, Last write 00:00:02
  Hold time is 9 seconds, keepalive interval is 3 seconds
  Configured hold time is 9 seconds, keepalive interval is 3 seconds
  Configured tcp-mss is 0, synced tcp-mss is 1448
  Configured conditional advertisements interval is 60 seconds
  Neighbor capabilities:
    4 Byte AS: advertised and received
    Extended Message: advertised and received
    AddPath:
      IPv4 Unicast: RX advertised and received
    Paths-Limit:
      IPv4 Unicast: advertised (0) and received (0)
    Dynamic: advertised and received
    Long-lived Graceful Restart: advertised and received
      Address families by peer:
    Route refresh: advertised and received
    Enhanced Route Refresh: advertised and received
    Address Family IPv4 Unicast: advertised and received
    Hostname Capability: advertised (name: ziyu-dell,domain name: n/a) received (name: ziyu-dell,domain name: n/a)
    Version Capability: advertised software version (FRRouting/10.6.0) received software version (FRRouting/10.6.0)
    Link-Local Next Hop Capability: not advertised not received
    Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Address families by peer:
            Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Peer has restarted (R-bit is set)
      Peer has restarted (N-bit is set)
      Address families by peer:
        none
  Graceful restart information:
    End-of-RIB send: IPv4 Unicast
    End-of-RIB received: IPv4 Unicast
    Local GR Mode: Helper*
    Remote GR Mode: Helper

    R bit: True
    N bit: True
    Timers:
      Configured Restart Time(sec): 120
      Received Restart Time(sec): 120
      Configured LLGR Stale Path Time(sec): 0
    IPv4 Unicast:
      F bit: False
      End-of-RIB sent: Yes
      End-of-RIB sent after update: No
      End-of-RIB received: Yes
      Timers:
        Configured Stale Path Time(sec): 360
        LLGR Stale Path Time(sec): 0
  Message statistics:
    Inq depth is 0
    Outq depth is 0
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:               16         18
    Keepalives:           865        865
    Route Refresh:          0          0
    Capability:             0          0
    Total:                882        884

  Prefix statistics:
    Inbound filtered: 0
    AS-PATH loop: 22
    Originator loop: 0
    Cluster loop: 0
    Invalid next-hop: 0
    Withdrawn: 0
    Attributes discarded: 0

  Minimum time between advertisement runs is 0 seconds
  Update delay timer is 0 seconds (remaining: 0)

 For address family: IPv4 Unicast
  Update group 1, subgroup 1
  Packet Queue length 0
  Community attribute sent to this neighbor(all)
  4 accepted, 16 sent prefixes

  Connections established 1; dropped 0
  Last reset 00:43:16,  No path to specified Neighbor (FRRouting/10.6.0)
  External BGP neighbor may be up to 1 hops away.
Local host: 172.17.2.1, Local port: 39794
Foreign host: 172.17.2.0, Foreign port: 179
Nexthop: 172.17.2.1
Nexthop global: fe80::f805:5cff:fe92:8037
Nexthop local: fe80::f805:5cff:fe92:8037
BGP connection: shared network
BGP Connect Retry Timer in Seconds: 10
Estimated round trip time: 28 ms
Read thread: on  Write thread: on  FD used: 28

BGP neighbor is 172.17.3.0, remote AS 65120, local AS 65000, external link
  Local Role: undefined
  Remote Role: undefined
Hostname: ziyu-dell
  BGP version 4, remote router ID 172.17.3.2, local router ID 172.17.4.1
  BGP state = Established, up for 00:43:15
  Last read 00:00:02, Last write 00:00:02
  Hold time is 9 seconds, keepalive interval is 3 seconds
  Configured hold time is 9 seconds, keepalive interval is 3 seconds
  Configured tcp-mss is 0, synced tcp-mss is 1448
  Configured conditional advertisements interval is 60 seconds
  Neighbor capabilities:
    4 Byte AS: advertised and received
    Extended Message: advertised and received
    AddPath:
      IPv4 Unicast: RX advertised and received
    Paths-Limit:
      IPv4 Unicast: advertised (0) and received (0)
    Dynamic: advertised and received
    Long-lived Graceful Restart: advertised and received
      Address families by peer:
    Route refresh: advertised and received
    Enhanced Route Refresh: advertised and received
    Address Family IPv4 Unicast: advertised and received
    Hostname Capability: advertised (name: ziyu-dell,domain name: n/a) received (name: ziyu-dell,domain name: n/a)
    Version Capability: advertised software version (FRRouting/10.6.0) received software version (FRRouting/10.6.0)
    Link-Local Next Hop Capability: not advertised not received
    Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Address families by peer:
            Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Peer has restarted (R-bit is set)
      Peer has restarted (N-bit is set)
      Address families by peer:
        none
  Graceful restart information:
    End-of-RIB send: IPv4 Unicast
    End-of-RIB received: IPv4 Unicast
    Local GR Mode: Helper*
    Remote GR Mode: Helper

    R bit: True
    N bit: True
    Timers:
      Configured Restart Time(sec): 120
      Received Restart Time(sec): 120
      Configured LLGR Stale Path Time(sec): 0
    IPv4 Unicast:
      F bit: False
      End-of-RIB sent: Yes
      End-of-RIB sent after update: No
      End-of-RIB received: Yes
      Timers:
        Configured Stale Path Time(sec): 360
        LLGR Stale Path Time(sec): 0
  Message statistics:
    Inq depth is 0
    Outq depth is 0
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:               16         17
    Keepalives:           865        865
    Route Refresh:          0          0
    Capability:             0          0
    Total:                882        883

  Prefix statistics:
    Inbound filtered: 0
    AS-PATH loop: 26
    Originator loop: 0
    Cluster loop: 0
    Invalid next-hop: 0
    Withdrawn: 0
    Attributes discarded: 0

  Minimum time between advertisement runs is 0 seconds
  Update delay timer is 0 seconds (remaining: 0)

 For address family: IPv4 Unicast
  Update group 1, subgroup 1
  Packet Queue length 0
  Community attribute sent to this neighbor(all)
  4 accepted, 16 sent prefixes

  Connections established 1; dropped 0
  Last reset 00:43:16,  No path to specified Neighbor (FRRouting/10.6.0)
  External BGP neighbor may be up to 1 hops away.
Local host: 172.17.3.1, Local port: 47956
Foreign host: 172.17.3.0, Foreign port: 179
Nexthop: 172.17.3.1
Nexthop global: fe80::5024:3cff:fee1:a3ea
Nexthop local: fe80::5024:3cff:fee1:a3ea
BGP connection: shared network
BGP Connect Retry Timer in Seconds: 10
Estimated round trip time: 33 ms
Read thread: on  Write thread: on  FD used: 29

BGP neighbor is 172.17.4.0, remote AS 65130, local AS 65000, external link
  Local Role: undefined
  Remote Role: undefined
Hostname: ziyu-dell
  BGP version 4, remote router ID 172.17.4.2, local router ID 172.17.4.1
  BGP state = Established, up for 00:43:15
  Last read 00:00:02, Last write 00:00:02
  Hold time is 9 seconds, keepalive interval is 3 seconds
  Configured hold time is 9 seconds, keepalive interval is 3 seconds
  Configured tcp-mss is 0, synced tcp-mss is 1448
  Configured conditional advertisements interval is 60 seconds
  Neighbor capabilities:
    4 Byte AS: advertised and received
    Extended Message: advertised and received
    AddPath:
      IPv4 Unicast: RX advertised and received
    Paths-Limit:
      IPv4 Unicast: advertised (0) and received (0)
    Dynamic: advertised and received
    Long-lived Graceful Restart: advertised and received
      Address families by peer:
    Route refresh: advertised and received
    Enhanced Route Refresh: advertised and received
    Address Family IPv4 Unicast: advertised and received
    Hostname Capability: advertised (name: ziyu-dell,domain name: n/a) received (name: ziyu-dell,domain name: n/a)
    Version Capability: advertised software version (FRRouting/10.6.0) received software version (FRRouting/10.6.0)
    Link-Local Next Hop Capability: not advertised not received
    Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Address families by peer:
            Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Peer has restarted (R-bit is set)
      Peer has restarted (N-bit is set)
      Address families by peer:
        none
  Graceful restart information:
    End-of-RIB send: IPv4 Unicast
    End-of-RIB received: IPv4 Unicast
    Local GR Mode: Helper*
    Remote GR Mode: Helper

    R bit: True
    N bit: True
    Timers:
      Configured Restart Time(sec): 120
      Received Restart Time(sec): 120
      Configured LLGR Stale Path Time(sec): 0
    IPv4 Unicast:
      F bit: False
      End-of-RIB sent: Yes
      End-of-RIB sent after update: No
      End-of-RIB received: Yes
      Timers:
        Configured Stale Path Time(sec): 360
        LLGR Stale Path Time(sec): 0
  Message statistics:
    Inq depth is 0
    Outq depth is 0
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:               16         16
    Keepalives:           865        865
    Route Refresh:          0          0
    Capability:             0          0
    Total:                882        882

  Prefix statistics:
    Inbound filtered: 0
    AS-PATH loop: 26
    Originator loop: 0
    Cluster loop: 0
    Invalid next-hop: 0
    Withdrawn: 0
    Attributes discarded: 0

  Minimum time between advertisement runs is 0 seconds
  Update delay timer is 0 seconds (remaining: 0)

 For address family: IPv4 Unicast
  Update group 1, subgroup 1
  Packet Queue length 0
  Community attribute sent to this neighbor(all)
  4 accepted, 16 sent prefixes

  Connections established 1; dropped 0
  Last reset 00:43:16,  No path to specified Neighbor (FRRouting/10.6.0)
  External BGP neighbor may be up to 1 hops away.
Local host: 172.17.4.1, Local port: 33330
Foreign host: 172.17.4.0, Foreign port: 179
Nexthop: 172.17.4.1
Nexthop global: fe80::1017:4cff:fe5b:5e7
Nexthop local: fe80::1017:4cff:fe5b:5e7
BGP connection: shared network
BGP Connect Retry Timer in Seconds: 10
Estimated round trip time: 28 ms
Read thread: on  Write thread: on  FD used: 30

```
以上是a00和c00的BGP邻居状态信息表，可以看到，这些交换机都成功的和周围的邻居建立了BGP会话，且通过邻居的ASN可以看出，各个节点正确地按照预想的`fat tree`拓扑设计和邻居通信。
下面展示具体的`show ip bgp`结果。
```bash
mininet> e00 show ip bgp
BGP table version is 16, local router ID is 172.16.1.4, vrf id 0
Default local pref 100, local AS 65102
Status codes:  s suppressed, d damped, h history, u unsorted, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

     Network          Next Hop            Metric LocPrf Weight Path
 *>  10.1.1.0/24      0.0.0.0(ziyu-dell)
                                               0         32768 i
 *>  10.1.2.0/24      0.0.0.0(ziyu-dell)
                                               0         32768 i
 *>  10.1.3.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65103 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65103 i
 *>  10.1.4.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65103 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65103 i
 *>  10.2.1.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65111 65112 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65110 65112 i
 *>  10.2.2.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65111 65112 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65110 65112 i
 *>  10.2.3.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65111 65113 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65110 65113 i
 *>  10.2.4.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65111 65113 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65110 65113 i
 *>  10.3.1.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65121 65122 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65120 65122 i
 *>  10.3.2.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65121 65122 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65120 65122 i
 *>  10.3.3.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65121 65123 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65120 65123 i
 *>  10.3.4.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65121 65123 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65120 65123 i
 *>  10.4.1.0/24      172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65130 65132 i
 *                    172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65131 65132 i
 *>  10.4.2.0/24      172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65130 65132 i
 *                    172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65131 65132 i
 *>  10.4.3.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65131 65133 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65130 65133 i
 *>  10.4.4.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65131 65133 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65130 65133 i

Displayed 16 routes and 30 total paths
```

```bash
mininet> a00 show ip bgp
BGP table version is 28, local router ID is 172.17.1.2, vrf id 0
Default local pref 100, local AS 65100
Status codes:  s suppressed, d damped, h history, u unsorted, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

     Network          Next Hop            Metric LocPrf Weight Path
 *>  10.1.1.0/24      172.16.1.0(ziyu-dell)
                                               0             0 65102 i
 *                    172.16.1.2(ziyu-dell)
                                                             0 65103 65101 65102 i
 *>  10.1.2.0/24      172.16.1.0(ziyu-dell)
                                               0             0 65102 i
 *                    172.16.1.2(ziyu-dell)
                                                             0 65103 65101 65102 i
 *>  10.1.3.0/24      172.16.1.2(ziyu-dell)
                                               0             0 65103 i
 *                    172.16.1.0(ziyu-dell)
                                                             0 65102 65101 65103 i
 *>  10.1.4.0/24      172.16.1.2(ziyu-dell)
                                               0             0 65103 i
 *                    172.16.1.0(ziyu-dell)
                                                             0 65102 65101 65103 i
 *>  10.2.1.0/24      172.17.1.1(ziyu-dell)
                                                             0 65000 65110 65112 i
 *                    172.17.1.3(ziyu-dell)
                                                             0 65002 65110 65112 i
 *                    172.16.1.0(ziyu-dell)
                                                             0 65102 65101 65001 65111 65112 i
 *                    172.16.1.2(ziyu-dell)
                                                             0 65103 65101 65001 65111 65112 i
 *>  10.2.2.0/24      172.17.1.1(ziyu-dell)
                                                             0 65000 65110 65112 i
 *                    172.17.1.3(ziyu-dell)
                                                             0 65002 65110 65112 i
 *                    172.16.1.0(ziyu-dell)
                                                             0 65102 65101 65001 65111 65112 i
 *                    172.16.1.2(ziyu-dell)
                                                             0 65103 65101 65001 65111 65112 i
 *>  10.2.3.0/24      172.17.1.1(ziyu-dell)
                                                             0 65000 65110 65113 i
 *                    172.17.1.3(ziyu-dell)
                                                             0 65002 65110 65113 i
 *                    172.16.1.0(ziyu-dell)
                                                             0 65102 65101 65001 65111 65113 i
 *                    172.16.1.2(ziyu-dell)
                                                             0 65103 65101 65001 65111 65113 i
 *>  10.2.4.0/24      172.17.1.1(ziyu-dell)
                                                             0 65000 65110 65113 i
 *                    172.17.1.3(ziyu-dell)
                                                             0 65002 65110 65113 i
 *                    172.16.1.0(ziyu-dell)
                                                             0 65102 65101 65001 65111 65113 i
 *                    172.16.1.2(ziyu-dell)
                                                             0 65103 65101 65001 65111 65113 i
 *>  10.3.1.0/24      172.17.1.1(ziyu-dell)
                                                             0 65000 65120 65122 i
 *                    172.17.1.3(ziyu-dell)
                                                             0 65002 65120 65122 i
 *                    172.16.1.0(ziyu-dell)
                                                             0 65102 65101 65001 65121 65122 i
 *                    172.16.1.2(ziyu-dell)
                                                             0 65103 65101 65001 65121 65122 i
 *>  10.3.2.0/24      172.17.1.1(ziyu-dell)
                                                             0 65000 65120 65122 i
 *                    172.17.1.3(ziyu-dell)
                                                             0 65002 65120 65122 i
 *                    172.16.1.0(ziyu-dell)
                                                             0 65102 65101 65001 65121 65122 i
 *                    172.16.1.2(ziyu-dell)
                                                             0 65103 65101 65001 65121 65122 i
 *>  10.3.3.0/24      172.17.1.1(ziyu-dell)
                                                             0 65000 65120 65123 i
 *                    172.17.1.3(ziyu-dell)
                                                             0 65002 65120 65123 i
 *                    172.16.1.0(ziyu-dell)
                                                             0 65102 65101 65001 65121 65123 i
 *                    172.16.1.2(ziyu-dell)
                                                             0 65103 65101 65001 65121 65123 i
 *>  10.3.4.0/24      172.17.1.1(ziyu-dell)
                                                             0 65000 65120 65123 i
 *                    172.17.1.3(ziyu-dell)
                                                             0 65002 65120 65123 i
 *                    172.16.1.0(ziyu-dell)
                                                             0 65102 65101 65001 65121 65123 i
 *                    172.16.1.2(ziyu-dell)
                                                             0 65103 65101 65001 65121 65123 i
 *>  10.4.1.0/24      172.17.1.1(ziyu-dell)
                                                             0 65000 65130 65132 i
 *                    172.17.1.3(ziyu-dell)
                                                             0 65002 65130 65132 i
 *>  10.4.2.0/24      172.17.1.1(ziyu-dell)
                                                             0 65000 65130 65132 i
 *                    172.17.1.3(ziyu-dell)
                                                             0 65002 65130 65132 i
 *>  10.4.3.0/24      172.17.1.1(ziyu-dell)
                                                             0 65000 65130 65133 i
 *                    172.17.1.3(ziyu-dell)
                                                             0 65002 65130 65133 i
 *                    172.16.1.0(ziyu-dell)
                                                             0 65102 65101 65001 65131 65133 i
 *                    172.16.1.2(ziyu-dell)
                                                             0 65103 65101 65001 65131 65133 i
 *>  10.4.4.0/24      172.17.1.1(ziyu-dell)
                                                             0 65000 65130 65133 i
 *                    172.17.1.3(ziyu-dell)
                                                             0 65002 65130 65133 i
 *                    172.16.1.0(ziyu-dell)
                                                             0 65102 65101 65001 65131 65133 i
 *                    172.16.1.2(ziyu-dell)
                                                             0 65103 65101 65001 65131 65133 i

Displayed 16 routes and 52 total paths
```

```bash
mininet> c00 show ip bgp
BGP table version is 30, local router ID is 172.17.4.1, vrf id 0
Default local pref 100, local AS 65000
Status codes:  s suppressed, d damped, h history, u unsorted, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

     Network          Next Hop            Metric LocPrf Weight Path
 *>  10.1.1.0/24      172.17.1.0(ziyu-dell)
                                                             0 65100 65102 i
 *>  10.1.2.0/24      172.17.1.0(ziyu-dell)
                                                             0 65100 65102 i
 *>  10.1.3.0/24      172.17.1.0(ziyu-dell)
                                                             0 65100 65103 i
 *>  10.1.4.0/24      172.17.1.0(ziyu-dell)
                                                             0 65100 65103 i
 *>  10.2.1.0/24      172.17.2.0(ziyu-dell)
                                                             0 65110 65112 i
 *>  10.2.2.0/24      172.17.2.0(ziyu-dell)
                                                             0 65110 65112 i
 *>  10.2.3.0/24      172.17.2.0(ziyu-dell)
                                                             0 65110 65113 i
 *>  10.2.4.0/24      172.17.2.0(ziyu-dell)
                                                             0 65110 65113 i
 *>  10.3.1.0/24      172.17.3.0(ziyu-dell)
                                                             0 65120 65122 i
 *>  10.3.2.0/24      172.17.3.0(ziyu-dell)
                                                             0 65120 65122 i
 *>  10.3.3.0/24      172.17.3.0(ziyu-dell)
                                                             0 65120 65123 i
 *>  10.3.4.0/24      172.17.3.0(ziyu-dell)
                                                             0 65120 65123 i
 *>  10.4.1.0/24      172.17.4.0(ziyu-dell)
                                                             0 65130 65132 i
 *>  10.4.2.0/24      172.17.4.0(ziyu-dell)
                                                             0 65130 65132 i
 *>  10.4.3.0/24      172.17.4.0(ziyu-dell)
                                                             0 65130 65133 i
 *>  10.4.4.0/24      172.17.4.0(ziyu-dell)
                                                             0 65130 65133 i

Displayed 16 routes and 16 total paths
```
从 e00、a00 和 c00 的 BGP 表可以看出，所有 16 个主机网段（10.1.1.0/24 至 10.4.4.0/24）均已被网络正确学习，说明各交换机之间的 BGP 邻接关系和路由传播过程正常。与此同时，这些输出中多数前缀虽具有多条候选路径，但最终只有一条被标记为最优路径（`*>`），尚未出现 multipath 标记（`=`），说明当前网络尚未启用 ECMP。
##### `traceroute`
追踪从`h000`到`h311`的路由信息：
```bash
mininet> h000 traceroute -n h311
traceroute to 10.4.4.3 (10.4.4.3), 30 hops max, 60 byte packets
 1  10.1.1.1  0.048 ms  0.009 ms  0.007 ms
 2  172.16.1.5  20.130 ms  20.109 ms  20.096 ms
 3  * * *
 4  * * *
 5  * * *
 6  10.4.4.3  80.614 ms  80.555 ms  80.540 ms
```
第一跳是默认网关，也就是对应的edge交换机的接口；第二跳`172.16.1.5`对应上面的a01的第一个以太网口，它和e00的第二个以太网口处于同一网段。中间三跳显示三个星号，但是根据上文的`e00`的BGP邻居信息表
```bash
 *>  10.4.4.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65131 65133 i
```
我们可以得出，实际上的路径是`h000 -> e00 -> a01 -> c01 -> a31 -> e31 -> h311`。其中第 3 至第 5 跳未显示的原因，初步判断原因是，这些中间节点未返回或未被 traceroute 正确识别为 ICMP Time Exceeded 报文，但是不影响网络的实际连通性。
##### 吞吐量
###### 未开ECMP
测试从`h000`到`h311`的路径。
```bash
mininet> h000 iperf -s &
mininet> h311 iperf -c h000 -P 4
------------------------------------------------------------
Client connecting to 10.1.1.2, TCP port 5001
TCP window size: 85.3 KByte (default)
------------------------------------------------------------
[  2] local 10.4.4.3 port 60878 connected with 10.1.1.2 port 5001
[  1] local 10.4.4.3 port 60862 connected with 10.1.1.2 port 5001
[  3] local 10.4.4.3 port 60890 connected with 10.1.1.2 port 5001
[  4] local 10.4.4.3 port 60892 connected with 10.1.1.2 port 5001
[ ID] Interval       Transfer     Bandwidth
[  2] 0.0000-16.1616 sec  4.73 MBytes  2.45 Mbits/sec
[  1] 0.0000-16.1616 sec  4.14 MBytes  2.15 Mbits/sec
[  4] 0.0000-16.4352 sec  4.91 MBytes  2.51 Mbits/sec
[  3] 0.0000-16.5800 sec  4.98 MBytes  2.52 Mbits/sec
[SUM] 0.0000-16.5800 sec  18.8 MBytes  9.49 Mbits/sec
```
###### 开ECMP
**ECMP（Equal-Cost Multi-Path，等价多路径）** 是一种允许设备对同一目的前缀同时使用多条等价最优路径进行负载分担的路由转发机制。当路由设备到同一目的网络存在多条代价相同的最优路径时，同时保留并使用这些路径进行转发。在本实验中，ECMP 表示交换机对同一目标主机网段，不再只选择一条最优路径，而是将多条等价路径同时安装到路由表中，从而把不同流量分散到多条链路上，提高总吞吐量并增强链路冗余能力。
下面给各个交换机加上`bgp bestpath as-path multipath-relax`这行代码，之后运行吞吐量测试代码。
```bash
mininet> h000 iperf -s & 
mininet> h311 iperf -c h000 -P 4  
------------------------------------------------------------
Client connecting to 10.1.1.2, TCP port 5001
TCP window size: 85.3 KByte (default)
------------------------------------------------------------
[  3] local 10.4.4.3 port 49594 connected with 10.1.1.2 port 5001
[  2] local 10.4.4.3 port 49586 connected with 10.1.1.2 port 5001
[  1] local 10.4.4.3 port 49570 connected with 10.1.1.2 port 5001
[  4] local 10.4.4.3 port 49600 connected with 10.1.1.2 port 5001
[ ID] Interval       Transfer     Bandwidth
[  1] 0.0000-14.0529 sec  6.00 MBytes  3.58 Mbits/sec
[  4] 0.0000-14.1016 sec  7.89 MBytes  4.69 Mbits/sec
[  3] 0.0000-14.1015 sec  7.99 MBytes  4.75 Mbits/sec
[  2] 0.0000-14.3600 sec  10.2 MBytes  5.94 Mbits/sec
[SUM] 0.0000-14.3600 sec  32.0 MBytes  18.7 Mbits/sec
```
可以看到，带宽倍增。查看BGP RIB：
```bash
mininet> e00 show ip bgp
BGP table version is 30, local router ID is 172.16.1.4, vrf id 0
Default local pref 100, local AS 65102
Status codes:  s suppressed, d damped, h history, u unsorted, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

     Network          Next Hop            Metric LocPrf Weight Path
 *>  10.1.1.0/24      0.0.0.0(ziyu-dell)
                                               0         32768 i
 *>  10.1.2.0/24      0.0.0.0(ziyu-dell)
                                               0         32768 i
 *>  10.1.3.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65103 i
 *=                   172.16.1.1(ziyu-dell)
                                                             0 65100 65103 i
 *>  10.1.4.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65103 i
 *=                   172.16.1.1(ziyu-dell)
                                                             0 65100 65103 i
 *>  10.2.1.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65111 65112 i
 *=                   172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65110 65112 i
 *>  10.2.2.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65111 65112 i
 *=                   172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65110 65112 i
 *>  10.2.3.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65111 65113 i
 *=                   172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65110 65113 i
 *>  10.2.4.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65111 65113 i
 *=                   172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65110 65113 i
 *>  10.3.1.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65121 65122 i
 *=                   172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65120 65122 i
 *>  10.3.2.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65121 65122 i
 *=                   172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65120 65122 i
 *>  10.3.3.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65121 65123 i
 *=                   172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65120 65123 i
 *>  10.3.4.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65121 65123 i
 *=                   172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65120 65123 i
 *>  10.4.1.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65131 65132 i
 *=                   172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65130 65132 i
 *>  10.4.2.0/24      172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65131 65132 i
 *=                   172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65130 65132 i
 *>  10.4.3.0/24      172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65130 65133 i
 *=                   172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65131 65133 i
 *>  10.4.4.0/24      172.16.1.1(ziyu-dell)
                                                             0 65100 65000 65130 65133 i
 *=                   172.16.1.5(ziyu-dell)
                                                             0 65101 65001 65131 65133 i

Displayed 16 routes and 30 total paths
```
出现了`=`号，说明是开启了multipath操作。

### Phase 2：选做题
要求是Core公用一个ASN，下面每层aggre/edge交换机同pod共用一个ASN。所以除了将Core的ASN设置为65001后，同一层一个pod内的aggre/edge，都统一设置成原本偶数的那个ASN。比如原本的a00和a01是65100和65101，现在则都是65100；以此类推，整体的ASN设置就不赘述。
在修改完关于ASN的分配问题后，就要面临一个冲突：如果同一个pod下的两个主机要通信，他们必然分别与同pod下两台edge switch相连，这个时候两个edge的ASN是相同的，目的主机连接的edge switch遇到这种包，就会识别出`AS-Path`中含有和自身相同的ASN，就会出现上面所说的拒收的情况，即默认BGP认为可能形成环路，故而拒收。
所以怎么解决？需要设置相应的路由策略来解决问题。这里我选择让各**边缘交换机**对上层汇聚交换机启用`allowas-in 1`，这样edge就可以接受那些起源于同pod的edge/AS-Path中已经包括本ASN**一次**的路由。至于**汇聚/核心交换机**，因为它们并不会收到来自同一层同一pod的交换机发来的包，所以也就不会出现拒收的问题，因此不用设置。
所以根据以上的分析，修改`config`文件。
#### `config`修改
除了edge，其他交换机在换完ASN后没有什么特殊的变动，所以只展示一个edge switch。
```bash
frr defaults datacenter
!
!
interface Ethernet1-1
  ip address 172.16.1.0/31
!
interface Ethernet1-2
  ip address 172.16.1.4/31
!
interface Ethernet1-3
  ip address 10.1.1.1/24
!
interface Ethernet1-4
  ip address 10.1.2.1/24
!
!
router bgp 65102
  neighbor 172.16.1.1 remote-as 65100
  neighbor 172.16.1.1 allowas-in 1
  neighbor 172.16.1.5 remote-as 65100
  neighbor 172.16.1.5 allowas-in 1
  network 10.1.1.0/24
  network 10.1.2.0/24
```
用`neighbor <ip_addr> allowas-in 1`命令允许携带自身ASN的包进入。
>`bgp bestpath as-path multipath-relax`这个命令是否添加已经对实验结果没有影响了，因为在各pod共用ASN后，就算到达某个指定IP的下一跳IP不同，但是经过的`AS-Path`一致，那么就可以认为二者是等价候选了，所以测试时会发现`show ip bgp`仍然会出现`*=`的标志。
### 结果
#### 连通性
```bash
mininet> pingall
*** Ping: testing ping reachability
h000 -> h001 h010 h011 h100 h101 h110 h111 h200 h201 h210 h211 h300 h301 h310 h311 
h001 -> h000 h010 h011 h100 h101 h110 h111 h200 h201 h210 h211 h300 h301 h310 h311 
h010 -> h000 h001 h011 h100 h101 h110 h111 h200 h201 h210 h211 h300 h301 h310 h311 
h011 -> h000 h001 h010 h100 h101 h110 h111 h200 h201 h210 h211 h300 h301 h310 h311 
h100 -> h000 h001 h010 h011 h101 h110 h111 h200 h201 h210 h211 h300 h301 h310 h311 
h101 -> h000 h001 h010 h011 h100 h110 h111 h200 h201 h210 h211 h300 h301 h310 h311 
h110 -> h000 h001 h010 h011 h100 h101 h111 h200 h201 h210 h211 h300 h301 h310 h311 
h111 -> h000 h001 h010 h011 h100 h101 h110 h200 h201 h210 h211 h300 h301 h310 h311 
h200 -> h000 h001 h010 h011 h100 h101 h110 h111 h201 h210 h211 h300 h301 h310 h311 
h201 -> h000 h001 h010 h011 h100 h101 h110 h111 h200 h210 h211 h300 h301 h310 h311 
h210 -> h000 h001 h010 h011 h100 h101 h110 h111 h200 h201 h211 h300 h301 h310 h311 
h211 -> h000 h001 h010 h011 h100 h101 h110 h111 h200 h201 h210 h300 h301 h310 h311 
h300 -> h000 h001 h010 h011 h100 h101 h110 h111 h200 h201 h210 h211 h301 h310 h311 
h301 -> h000 h001 h010 h011 h100 h101 h110 h111 h200 h201 h210 h211 h300 h310 h311 
h310 -> h000 h001 h010 h011 h100 h101 h110 h111 h200 h201 h210 h211 h300 h301 h311 
h311 -> h000 h001 h010 h011 h100 h101 h110 h111 h200 h201 h210 h211 h300 h301 h310 
*** Results: 0% dropped (240/240 received)
```
#### BGP邻居状态信息表
```bash
mininet> e00 show ip bgp neighbors
BGP neighbor is 172.16.1.1, remote AS 65100, local AS 65102, external link
  Local Role: undefined
  Remote Role: undefined
Hostname: ziyu-dell
  BGP version 4, remote router ID 172.17.1.2, local router ID 172.16.1.4
  BGP state = Established, up for 00:00:39
  Last read 00:00:03, Last write 00:00:03
  Hold time is 9 seconds, keepalive interval is 3 seconds
  Configured hold time is 9 seconds, keepalive interval is 3 seconds
  Configured tcp-mss is 0, synced tcp-mss is 1448
  Configured conditional advertisements interval is 60 seconds
  Neighbor capabilities:
    4 Byte AS: advertised and received
    Extended Message: advertised and received
    AddPath:
      IPv4 Unicast: RX advertised and received
    Paths-Limit:
      IPv4 Unicast: advertised (0) and received (0)
    Dynamic: advertised and received
    Long-lived Graceful Restart: advertised and received
      Address families by peer:
    Route refresh: advertised and received
    Enhanced Route Refresh: advertised and received
    Address Family IPv4 Unicast: advertised and received
    Hostname Capability: advertised (name: ziyu-dell,domain name: n/a) received (name: ziyu-dell,domain name: n/a)
    Version Capability: advertised software version (FRRouting/10.6.0) received software version (FRRouting/10.6.0)
    Link-Local Next Hop Capability: not advertised not received
    Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Address families by peer:
            Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Peer has restarted (R-bit is set)
      Peer has restarted (N-bit is set)
      Address families by peer:
        none
  Graceful restart information:
    End-of-RIB send: IPv4 Unicast
    End-of-RIB received: IPv4 Unicast
    Local GR Mode: Helper*
    Remote GR Mode: Helper

    R bit: True
    N bit: True
    Timers:
      Configured Restart Time(sec): 120
      Received Restart Time(sec): 120
      Configured LLGR Stale Path Time(sec): 0
    IPv4 Unicast:
      F bit: False
      End-of-RIB sent: Yes
      End-of-RIB sent after update: No
      End-of-RIB received: Yes
      Timers:
        Configured Stale Path Time(sec): 360
        LLGR Stale Path Time(sec): 0
  Message statistics:
    Inq depth is 0
    Outq depth is 0
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:                8          9
    Keepalives:            13         13
    Route Refresh:          0          0
    Capability:             0          0
    Total:                 22         23

  Prefix statistics:
    Inbound filtered: 0
    AS-PATH loop: 0
    Originator loop: 0
    Cluster loop: 0
    Invalid next-hop: 0
    Withdrawn: 0
    Attributes discarded: 0

  Minimum time between advertisement runs is 0 seconds
  Update delay timer is 0 seconds (remaining: 0)

 For address family: IPv4 Unicast
  Update group 1, subgroup 2
  Packet Queue length 0
  Local AS allowed in path, 1 occurrences
  Community attribute sent to this neighbor(all)
  16 accepted, 16 sent prefixes

  Connections established 1; dropped 0
  Last reset 00:00:40,  No path to specified Neighbor (FRRouting/10.6.0)
  External BGP neighbor may be up to 1 hops away.
Local host: 172.16.1.0, Local port: 47920
Foreign host: 172.16.1.1, Foreign port: 179
Nexthop: 172.16.1.0
Nexthop global: fe80::b04d:b5ff:fe45:c077
Nexthop local: fe80::b04d:b5ff:fe45:c077
BGP connection: shared network
BGP Connect Retry Timer in Seconds: 10
Estimated round trip time: 21 ms
Read thread: on  Write thread: on  FD used: 27

BGP neighbor is 172.16.1.5, remote AS 65100, local AS 65102, external link
  Local Role: undefined
  Remote Role: undefined
Hostname: ziyu-dell
  BGP version 4, remote router ID 172.17.1.6, local router ID 172.16.1.4
  BGP state = Established, up for 00:00:39
  Last read 00:00:03, Last write 00:00:03
  Hold time is 9 seconds, keepalive interval is 3 seconds
  Configured hold time is 9 seconds, keepalive interval is 3 seconds
  Configured tcp-mss is 0, synced tcp-mss is 1448
  Configured conditional advertisements interval is 60 seconds
  Neighbor capabilities:
    4 Byte AS: advertised and received
    Extended Message: advertised and received
    AddPath:
      IPv4 Unicast: RX advertised and received
    Paths-Limit:
      IPv4 Unicast: advertised (0) and received (0)
    Dynamic: advertised and received
    Long-lived Graceful Restart: advertised and received
      Address families by peer:
    Route refresh: advertised and received
    Enhanced Route Refresh: advertised and received
    Address Family IPv4 Unicast: advertised and received
    Hostname Capability: advertised (name: ziyu-dell,domain name: n/a) received (name: ziyu-dell,domain name: n/a)
    Version Capability: advertised software version (FRRouting/10.6.0) received software version (FRRouting/10.6.0)
    Link-Local Next Hop Capability: not advertised not received
    Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Address families by peer:
            Graceful Restart Capability: advertised and received
      Remote Restart timer is 120 seconds
      Peer has restarted (R-bit is set)
      Peer has restarted (N-bit is set)
      Address families by peer:
        none
  Graceful restart information:
    End-of-RIB send: IPv4 Unicast
    End-of-RIB received: IPv4 Unicast
    Local GR Mode: Helper*
    Remote GR Mode: Helper

    R bit: True
    N bit: True
    Timers:
      Configured Restart Time(sec): 120
      Received Restart Time(sec): 120
      Configured LLGR Stale Path Time(sec): 0
    IPv4 Unicast:
      F bit: False
      End-of-RIB sent: Yes
      End-of-RIB sent after update: No
      End-of-RIB received: Yes
      Timers:
        Configured Stale Path Time(sec): 360
        LLGR Stale Path Time(sec): 0
  Message statistics:
    Inq depth is 0
    Outq depth is 0
                         Sent       Rcvd
    Opens:                  1          1
    Notifications:          0          0
    Updates:                9          8
    Keepalives:            13         13
    Route Refresh:          0          0
    Capability:             0          0
    Total:                 23         22

  Prefix statistics:
    Inbound filtered: 0
    AS-PATH loop: 0
    Originator loop: 0
    Cluster loop: 0
    Invalid next-hop: 0
    Withdrawn: 0
    Attributes discarded: 0

  Minimum time between advertisement runs is 0 seconds
  Update delay timer is 0 seconds (remaining: 0)

 For address family: IPv4 Unicast
  Update group 1, subgroup 2
  Packet Queue length 0
  Local AS allowed in path, 1 occurrences
  Community attribute sent to this neighbor(all)
  16 accepted, 16 sent prefixes

  Connections established 1; dropped 0
  Last reset 00:00:40,  No path to specified Neighbor (FRRouting/10.6.0)
  External BGP neighbor may be up to 1 hops away.
Local host: 172.16.1.4, Local port: 46886
Foreign host: 172.16.1.5, Foreign port: 179
Nexthop: 172.16.1.4
Nexthop global: fe80::c67:f5ff:fe3d:f9c
Nexthop local: fe80::c67:f5ff:fe3d:f9c
BGP connection: shared network
BGP Connect Retry Timer in Seconds: 10
Estimated round trip time: 21 ms
Read thread: on  Write thread: on  FD used: 28

```
可以看到，edge交换机已经和邻居成功建立了联系。由于信息过长，aggre和core的输出就不贴出。
```
mininet> e00 show ip bgp
BGP table version is 30, local router ID is 172.16.1.4, vrf id 0
Default local pref 100, local AS 65102
Status codes:  s suppressed, d damped, h history, u unsorted, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

     Network          Next Hop            Metric LocPrf Weight Path
 *>  10.1.1.0/24      0.0.0.0(ziyu-dell)
                                               0         32768 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65102 i
 *                    172.16.1.5(ziyu-dell)
                                                             0 65100 65102 i
 *>  10.1.2.0/24      0.0.0.0(ziyu-dell)
                                               0         32768 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65102 i
 *                    172.16.1.5(ziyu-dell)
                                                             0 65100 65102 i
 *>  10.1.3.0/24      172.16.1.5(ziyu-dell)
                                                             0 65100 65102 i
 *=                   172.16.1.1(ziyu-dell)
                                                             0 65100 65102 i
 *>  10.1.4.0/24      172.16.1.5(ziyu-dell)
                                                             0 65100 65102 i
 *=                   172.16.1.1(ziyu-dell)
                                                             0 65100 65102 i
 *>  10.2.1.0/24      172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65110 65112 i
 *=                   172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65110 65112 i
 *>  10.2.2.0/24      172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65110 65112 i
 *=                   172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65110 65112 i
 *>  10.2.3.0/24      172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65110 65112 i
 *=                   172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65110 65112 i
 *>  10.2.4.0/24      172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65110 65112 i
 *=                   172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65110 65112 i
 *>  10.3.1.0/24      172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65120 65122 i
 *=                   172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65120 65122 i
 *>  10.3.2.0/24      172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65120 65122 i
 *=                   172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65120 65122 i
 *>  10.3.3.0/24      172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65120 65122 i
 *=                   172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65120 65122 i
 *>  10.3.4.0/24      172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65120 65122 i
 *=                   172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65120 65122 i
 *>  10.4.1.0/24      172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65130 65132 i
 *=                   172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65130 65132 i
 *>  10.4.2.0/24      172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65130 65132 i
 *=                   172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65130 65132 i
 *>  10.4.3.0/24      172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65130 65132 i
 *=                   172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65130 65132 i
 *>  10.4.4.0/24      172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65130 65132 i
 *=                   172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65130 65132 i

Displayed 16 routes and 34 total paths
```
#### 吞吐量
现在的默认情况下，multipath也是处于开启状态的，吞吐量测试结果如下
```bash
mininet> h000 iperf -s &
mininet> h311 iperf -c h000 -P 4
------------------------------------------------------------
Client connecting to 10.1.1.2, TCP port 5001
TCP window size: 85.3 KByte (default)
------------------------------------------------------------
[  4] local 10.4.4.3 port 41904 connected with 10.1.1.2 port 5001
[  1] local 10.4.4.3 port 41898 connected with 10.1.1.2 port 5001
[  2] local 10.4.4.3 port 41918 connected with 10.1.1.2 port 5001
[  3] local 10.4.4.3 port 41916 connected with 10.1.1.2 port 5001
[ ID] Interval       Transfer     Bandwidth
[  1] 0.0000-14.6745 sec  6.54 MBytes  3.74 Mbits/sec
[  4] 0.0000-14.8841 sec  5.51 MBytes  3.10 Mbits/sec
[  3] 0.0000-14.9004 sec  10.3 MBytes  5.77 Mbits/sec
[  2] 0.0000-14.9810 sec  11.4 MBytes  6.37 Mbits/sec
[SUM] 0.0000-14.9810 sec  33.7 MBytes  18.9 Mbits/sec
mininet> e00 show ip route 10.4.4.0/24
Routing entry for 10.4.4.0/24
  Known via "bgp", distance 20, metric 0, best
  Last update 00:13:55 ago
  Flags: Selected 
  Status: Installed 
  * 172.16.1.1, via Ethernet1-1, weight 1
  * 172.16.1.5, via Ethernet1-2, weight 1
```
那么如何对比不开multipath模式下的吞吐量？经过测试，应该设置`maximum-paths 1`这个选项，让等价路径条数最大为1，这样就可以强制禁止multipath了，***从结果上等同于关闭ECMP模式***。对应吞吐量数据如下：
```bash
mininet> h000 iperf -s &
mininet> h311 iperf -c h000 -P 4
------------------------------------------------------------
Client connecting to 10.1.1.2, TCP port 5001
TCP window size: 85.3 KByte (default)
------------------------------------------------------------
[  1] local 10.4.4.3 port 45400 connected with 10.1.1.2 port 5001
[  2] local 10.4.4.3 port 45402 connected with 10.1.1.2 port 5001
[  3] local 10.4.4.3 port 45416 connected with 10.1.1.2 port 5001
[  4] local 10.4.4.3 port 45410 connected with 10.1.1.2 port 5001
[ ID] Interval       Transfer     Bandwidth
[  4] 0.0000-16.4085 sec  4.91 MBytes  2.51 Mbits/sec
[  2] 0.0000-16.4247 sec  4.91 MBytes  2.51 Mbits/sec
[  3] 0.0000-16.4407 sec  4.45 MBytes  2.27 Mbits/sec
[  1] 0.0000-16.4731 sec  4.33 MBytes  2.20 Mbits/sec
[SUM] 0.0000-16.4732 sec  18.6 MBytes  9.47 Mbits/sec
```
此时查看BGP表：
```bash
mininet> e00 show ip bgp
BGP table version is 16, local router ID is 172.16.1.4, vrf id 0
Default local pref 100, local AS 65102
Status codes:  s suppressed, d damped, h history, u unsorted, * valid, > best, = multipath,
               i internal, r RIB-failure, S Stale, R Removed
Nexthop codes: @NNN nexthop's vrf id, < announce-nh-self
Origin codes:  i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found

     Network          Next Hop            Metric LocPrf Weight Path
 *>  10.1.1.0/24      0.0.0.0(ziyu-dell)
                                               0         32768 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65102 i
 *                    172.16.1.5(ziyu-dell)
                                                             0 65100 65102 i
 *>  10.1.2.0/24      0.0.0.0(ziyu-dell)
                                               0         32768 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65102 i
 *                    172.16.1.5(ziyu-dell)
                                                             0 65100 65102 i
 *>  10.1.3.0/24      172.16.1.1(ziyu-dell)
                                                             0 65100 65102 i
 *                    172.16.1.5(ziyu-dell)
                                                             0 65100 65102 i
 *>  10.1.4.0/24      172.16.1.1(ziyu-dell)
                                                             0 65100 65102 i
 *                    172.16.1.5(ziyu-dell)
                                                             0 65100 65102 i
 *>  10.2.1.0/24      172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65110 65112 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65110 65112 i
 *>  10.2.2.0/24      172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65110 65112 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65110 65112 i
 *>  10.2.3.0/24      172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65110 65112 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65110 65112 i
 *>  10.2.4.0/24      172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65110 65112 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65110 65112 i
 *>  10.3.1.0/24      172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65120 65122 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65120 65122 i
 *>  10.3.2.0/24      172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65120 65122 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65120 65122 i
 *>  10.3.3.0/24      172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65120 65122 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65120 65122 i
 *>  10.3.4.0/24      172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65120 65122 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65120 65122 i
 *>  10.4.1.0/24      172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65130 65132 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65130 65132 i
 *>  10.4.2.0/24      172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65130 65132 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65130 65132 i
 *>  10.4.3.0/24      172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65130 65132 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65130 65132 i
 *>  10.4.4.0/24      172.16.1.5(ziyu-dell)
                                                             0 65100 65001 65130 65132 i
 *                    172.16.1.1(ziyu-dell)
                                                             0 65100 65001 65130 65132 i

Displayed 16 routes and 34 total paths
```
可以看到，multipath模式已经被禁用了。所以必做题/样例中给出的`bestpath`命令本质上是决定“**AS-Path 不完全一样时，能不能也拿来做 multipath**”。二者虽然都是为了调整是否开启ECMP，但是从方式上是不同的。