## Introduction to SDN
### Features of SDN
- （SDN的目的）让网络设备 **“白盒化”**，可以自己定义协议/系统/计算目标。
- 路由协议是分布式运行的（每个设备自己计算路由表）；但是在SDN上是**集中式**的控制，每个设备上只有很简单的OS，不进行任何分布式计算，路由计算在一个集中式的**网络操作系统**上进行，所以计算也都在这个NOS上进行。
- 数据平面和控制平面的解耦。 
> 网络的两种分类视角：
> - 分层式
> - Data Panel + Control Panel
### 2 Types of Panels
#### Data Panel
- Packet Streaming;
- Table Lookup
- Forward
- Filter
- Buffer
#### Control Panel
- 执行分布式算法
- 追踪拓扑
- 计算路由
- Install Forward Rules
>不直接接触数据单元。
### Layering
#### 传输单元
- 链路层：frames
- 物理层：bits（bit flow）
- 传输层：segments
- 网络层：packets
- 应用层：messages
#### End2End
在不同layer的设备看到的网络层数不同，每一层设备只关注当层和其下面几层的事情。
#### The Hourglass Model
网络层的协议最少（IP），此层向上/下协议都慢慢变多。
>但是这些协议都只是**数据平面**的。但是比如`ARP/ICMP/DHCP`之类的并不处于这个沙漏模型中，而是属于**控制平面**的，且很难以层分类，比如ARP就是IP到MAC地址的映射，因而是跨层的。

### Switching（交换机）
网卡（NIC/Adapter）和网卡之间通信。
#### 标识（地址）
用MAC Addr来标识，48位，在全局是唯一的（Global Unique）。
```text
xx:xx:xx:xx:xx:xx
```
>Range of Addr: $2^{48}$
#### MAC Addr is Hierarchical
前六个数字就可以看出某些有关厂商的信息。
#### Special Address
##### Broadcast Addr
`ff:ff:ff:ff:ff:ff`。
#### IP Allocation
##### DHCP
控制平面协议。步骤如下：
1. Device sends a broadcast with a `dstmac` of  all f;
2. DHCP Offer gives a addr to the request device
#### From IP to MAC
##### ARP, Address Resolution Protocol
1. Device with IP `192.168.1.9` sends a broadcast, request for `192.168.1.10`'s MAC Address;
2. Device `192.168.1.10` sends its MAC Addr back to the request device.
### Ethernet Hub（集线器）
#### 特征
- Bus Structure
- A device sends a message, flooding to all devices in the hub 
- Drawbacks: 一个设备占用集线器，其他都只能等待。
#### CSMA/CD
- 为了解决Hub通信的竞争/独占问题。
- 在数据链路层，但是已经不复存在，不再被使用。集线器不再被使用，而交换机不需要这个。
>半双工通信
### Ethernet Switch
- Switch is plug-and-play；
- 需要MAC表来实现点对点通信。
- MAC Table is filled through learning. 随着收发过程的进行，MAC表会逐步被建立。
#### Broadcast Storm
- 前提：存在环路
- 如果一个设备收到广播包，它会转发给邻居，于是这个广播包数会指数型地增长。
- IP中有TTL，TTL到最大值包就会被丢掉。但是链路层没有，所以发生loop很可怕
- Solution：在拓扑中找到非环路，形成最小生成树（Prim/Kruskal）。**Spanning Tree Protocol（STP）** 就用来生成这个。不在生成树上的边都禁掉。
#### STP
- 作用上文已说；
- 缺点：会禁用很多链路，于是就会造成链路的资源浪费，严重降低传输效率。
### DNS
域名系统，是一种分布式数据库，解决从**域名**到**IP Addr**的映射，起“翻译”的作用。
#### Domain Name
- Managed by IANA；
- Domain Name is Hierarchical；
- 最top是一个root Server；层层向下。全球范围内有13个根服务器
#### DNS Server & Records
一个DNS服务器存储很多records，它们由`name` `value` `type` `TTL`组成。
##### 记录
###### 类型
- `CNAME`：“别名”，canonical name；
- `A`/`AAAA`：可以记录从一个域名到实际的`IPv4/v6`地址。
###### TTL
在TTL失效之前，不需要重新查询这个东西。不能设太大，也不能设太小。
>使用linux的`dig`命令搜索一个域名，就会返回好几条记录。
#### 负载均衡
不同的地区，利用DNS就可以把一个域名解析到不同的IP。
#### DNS IP
不同的DNS服务器IP对应的不同的DNS服务器。
#### DNS Cache Poisoning
也就是DNS污染。对DNS服务器投毒，让一个域名的解析结果导向一个有恶意的IP。
黑客可以假装域名服务器，发送一个UTP包，把某个IP地址返回到DNS，导致DNS服务器有了错误的缓存。所以一个用户请求域名解析的时候只会从这个错误的缓存记录获得错误的IP。
#### 如何判断何时需要用ARP协议
看私有IP和子网掩码，如果不属于掩码规定的子网范围内，就不调用ARP，而是把IP发到**网关**；ARP来解析网关（如`192.168.1.1`）的MAC地址，然后把包发出去。
所以此时`dstmac`是网关MAC，而`dstip`仍然是最终的目标IP。
