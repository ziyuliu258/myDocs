## 实验目的

1. 理解并实现 SDN 环境下的二层自学习交换机逻辑 。
2. 掌握在环状拓扑中处理 ARP 广播风暴的策略 。
3. 学习利用 LLDP 和 Echo 报文测量链路实时时延的原理 。
4. 实现基于最小时延的有权图路由算法（如 Dijkstra）。
5. （可选）探索链路故障下的动态路由切换机制 。

## 实验环境
`Arch Linux` 物理机，内核版本`7.0.3-arch1-2`。

## 实验内容
### 任务一：自学习交换机
#### 默认情况
执行以下命令：
```bash
 uv run -m controllers.task1.self_learning_switch
loading app controllers.task1.self_learning_switch
loading app os_ken.controller.ofp_handler
instantiating app controllers.task1.self_learning_switch of Switch
instantiating app os_ken.controller.ofp_handler of OFPHandler
```
再创建新的shell进程，创建拓扑并用wireshark抓包测试原始设置。
```bash
 sudo uv run topos/topo_1969_1.py
*** Creating network
*** Adding controller
*** Adding hosts:
SRI UCLA UCSB UTAH 
*** Adding switches:
s1 s2 s3 s4 
*** Adding links:
(s1, SRI) (10.00Mbit 50ms delay) (10.00Mbit 50ms delay) (s1, s2) (10.00Mbit 34ms delay) (10.00Mbit 34ms delay) (s1, s3) (10.00Mbit 13ms delay) (10.00Mbit 13ms delay) (s1, s4) (s2, UTAH) (s3, UCSB) (s4, UCLA) 
*** Configuring hosts
SRI UCLA UCSB UTAH 
*** Starting controller
c0 
*** Starting 4 switches
s1 s2 s3 s4 ...(10.00Mbit 50ms delay) (10.00Mbit 34ms delay) (10.00Mbit 13ms delay) (10.00Mbit 50ms delay) (10.00Mbit 34ms delay) (10.00Mbit 13ms delay) 
SRI SRI-eth0:s1-eth1
UCLA UCLA-eth0:s4-eth1
UCSB UCSB-eth0:s3-eth1
UTAH UTAH-eth0:s2-eth1
*** Starting CLI:
mininet> UCSB wireshark &
mininet> UCLA ping UTAH
PING 10.0.0.4 (10.0.0.4) 56(84) bytes of data.
64 bytes from 10.0.0.4: icmp_seq=1 ttl=64 time=267 ms
64 bytes from 10.0.0.4: icmp_seq=2 ttl=64 time=133 ms
64 bytes from 10.0.0.4: icmp_seq=3 ttl=64 time=134 ms
64 bytes from 10.0.0.4: icmp_seq=4 ttl=64 time=133 ms
64 bytes from 10.0.0.4: icmp_seq=5 ttl=64 time=134 ms
64 bytes from 10.0.0.4: icmp_seq=6 ttl=64 time=134 ms
64 bytes from 10.0.0.4: icmp_seq=7 ttl=64 time=133 ms
64 bytes from 10.0.0.4: icmp_seq=8 ttl=64 time=134 ms
64 bytes from 10.0.0.4: icmp_seq=9 ttl=64 time=134 ms
64 bytes from 10.0.0.4: icmp_seq=10 ttl=64 time=134 ms
64 bytes from 10.0.0.4: icmp_seq=11 ttl=64 time=134 ms
64 bytes from 10.0.0.4: icmp_seq=12 ttl=64 time=134 ms
64 bytes from 10.0.0.4: icmp_seq=13 ttl=64 time=133 ms
64 bytes from 10.0.0.4: icmp_seq=14 ttl=64 time=133 ms
^C
--- 10.0.0.4 ping statistics ---
14 packets transmitted, 14 received, 0% packet loss, time 13014ms
rtt min/avg/max/mdev = 132.623/143.151/267.086/34.377 ms
mininet> dump # 可以看到各个node的MAC地址/IP地址等信息
<Host SRI: SRI-eth0:10.0.0.1 pid=166760> 
<Host UCLA: UCLA-eth0:10.0.0.2 pid=166762> 
<Host UCSB: UCSB-eth0:10.0.0.3 pid=166764> 
<Host UTAH: UTAH-eth0:10.0.0.4 pid=166766> 
<OVSSwitch s1: lo:127.0.0.1,s1-eth1:None,s1-eth2:None,s1-eth3:None,s1-eth4:None pid=166771> 
<OVSSwitch s2: lo:127.0.0.1,s2-eth1:None,s2-eth2:None pid=166774> 
<OVSSwitch s3: lo:127.0.0.1,s3-eth1:None,s3-eth2:None pid=166777> 
<OVSSwitch s4: lo:127.0.0.1,s4-eth1:None,s4-eth2:None pid=166780> 
<RemoteController c0: 127.0.0.1:6633 pid=166751> 
```
抓包结果如下：
![](../../../attachments/Pasted%20image%2020260508163400.png)
可以看到，虽然是UCLA到UTAH，但是UCSB还是可以看到包，这是因为默认情况下 `task1` 里交换机只有一条 table-miss 规则，凡是没命中流表的包都会直接送到控制器，而如果控制器不做 MAC 学习并指定输出端口，就只能采用 `FLOOD` 泛洪转发；泛洪会把包发到除入端口外的所有端口，所以本来只想发给 UCLA 的帧，连在同一交换机上的 UCSB 也会收到。只有学到“目标 MAC 对应哪个端口”之后，交换机才能做单点转发。
#### 改进
补全代码：
```python
from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from os_ken.controller.handler import set_ev_cls
from os_ken.ofproto import ofproto_v1_3
from os_ken.lib.packet import packet
from os_ken.lib.packet import ethernet
from os_ken import log

class Switch(app_manager.OSKenApp):
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    def __init__(self, *args, **kwargs):
        super(Switch, self).__init__(*args, **kwargs)
        # maybe you need a global data structure to save the mapping
        self.map2port = {}
        
    def add_flow(self, datapath, priority, match, actions,idle_timeout=0,hard_timeout=0):
        dp = datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=dp, priority=priority,
                                idle_timeout=idle_timeout,
                                hard_timeout=hard_timeout,
                                match=match,instructions=inst)
        dp.send_msg(mod)
        
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofp.OFPP_CONTROLLER,ofp.OFPCML_NO_BUFFER)]
        self.add_flow(dp, 0, match, actions)
        
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        
        # the identity of switch
        dpid = dp.id
        # the port that receive the packet
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        # get the mac
        dst = eth_pkt.dst
        src = eth_pkt.src
        # we can use the logger to print some useful information
        self.logger.info('packet: %s %s %s %s', dpid, src, dst, in_port)
        
        # You need to code here to avoid the direct flooding
        # Have fun!
        # :)
        self.map2port.setdefault(dpid, {})
        self.map2port[dpid][src] = in_port

        if dst in self.map2port[dpid]:
            out_port = self.map2port[dpid][dst]
        else:
            out_port = ofp.OFPP_FLOOD
        
        act = [parser.OFPActionOutput(out_port)]
        if out_port != ofp.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            self.add_flow(dp, 1, match, act)
        
        out = parser.OFPPacketOut(datapath=dp, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=act, data=msg.data)
        dp.send_msg(out)

if __name__ == '__main__':
    log.init_log()
    app_manager.AppManager.run_apps(["controllers.task1.self_learning_switch"])
```
这下重启交换机，果然抓不到ICMP包了，只剩下开头的一个ARP广播包。
![](../../../attachments/Pasted%20image%2020260508171055.png)
分析原因：设置规则后，交换机已经不再对未知流量一直进行无脑泛洪了。控制器先通过 `src -> in_port` 学习每个主机的 MAC 地址位置；当后续收到发往 `UCLA` 的包时，如果发现目标 MAC 已经在表里，就会把 `out_port` 精确设置为 `UCLA` 所在端口，并下发一条流表让交换机以后直接按这个端口转发。这样数据帧只会从对应端口单播发送出去，不会再像默认情况那样被 `FLOOD` 到其他端口，所以 `UCSB` 就看不到这个包了。

### 任务二：处理环路广播
在复杂网络中，如果目的 MAC未知， 会触发全网洪泛。如果网络存在环路，一个主机发出的 ARP 广播包会绕着环路无限循环转发，呈指数级放大，形成**广播风暴**，从而瞬间压垮网络。
解决思路就是让控制器记录下每一次处理过的 ARP 请求特征。如果很快又从另一个端口收到了长得一模一样的 ARP 请求，说明这是从环路绕回来的冗余包，直接丢弃。
#### 改进方法
根据要求改进代码：
```python
from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from os_ken.controller.handler import set_ev_cls
from os_ken.ofproto import ofproto_v1_3
from os_ken.lib.packet import packet
from os_ken.lib.packet import ethernet
from os_ken.lib.packet import arp
from os_ken.lib.packet import ether_types
from os_ken import log

ETHERNET = ethernet.ethernet.__name__
ETHERNET_MULTICAST = "ff:ff:ff:ff:ff:ff"
ARP = arp.arp.__name__


class Switch_Dict(app_manager.OSKenApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Switch_Dict, self).__init__(*args, **kwargs)
        self.sw = {} #(dpid, src_mac, dst_ip)=>in_port, you may use it in task 2
        # maybe you need a global data structure to save the mapping
        # just data structure in task 1
        self.map2port = {}
        

    def add_flow(self, datapath, priority, match, actions, idle_timeout=0, hard_timeout=0):
        dp = datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=dp, priority=priority,
                                idle_timeout=idle_timeout,
                                hard_timeout=hard_timeout,
                                match=match, instructions=inst)
        dp.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofp.OFPP_CONTROLLER, ofp.OFPCML_NO_BUFFER)]
        self.add_flow(dp, 0, match, actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        # the identity of switch
        dpid = dp.id
        # the port that receive the packet
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        if eth_pkt.ethertype == ether_types.ETH_TYPE_LLDP:
            return
        if eth_pkt.ethertype == ether_types.ETH_TYPE_IPV6:
            return
        # get the mac
        dst = eth_pkt.dst
        src = eth_pkt.src
        # get protocols
        header_list = dict((p.protocol_name, p) for p in pkt.protocols if type(p) != str)
        if dst == ETHERNET_MULTICAST and ARP in header_list:
            arp_pkt = header_list[ARP] # 解出arp协议头
            arp_key = (dpid, src, arp_pkt.dst_ip) # 构造唯一标志，交换机、src主机、目标IP
            prev_port = self.sw.get(arp_key) # 在字典self.sw里查询，如果出现过类似的ARP广播，那就返回它第一次进入交换机的端口号
            if prev_port is not None and prev_port != in_port: # 说明很可能出现环路，上一个port不等于进入的port。
                return
            self.sw[arp_key] = in_port
        # you need to code here to avoid broadcast loop to finish task 2
        
        # self-learning
        # you need to code here to avoid the direct flooding
        # having fun
        # :)
        # just code in task 1
        self.map2port.setdefault(dpid, {})
        self.map2port[dpid][src] = in_port

        if dst in self.map2port[dpid]:
            out_port = self.map2port[dpid][dst]
        else:
            out_port = ofp.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]
        if out_port != ofp.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            self.add_flow(dp, 1, match, actions)

        out = parser.OFPPacketOut(datapath=dp, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=msg.data)
        dp.send_msg(out)

if __name__ == '__main__':
    log.init_log()
    app_manager.AppManager.run_apps(["controllers.task2.loop_detecting_switch"])

```
可以看到，下面的自学习交换机配置就是照抄Task 1的，而重点是上面ARP广播的去重操作。这段代码首先构建一个三元组唯一标识`arp_key`，以此为去重检测的依据：**同一台交换机上，同一个源 MAC 发出的、查询同一个目标 IP 的 ARP 广播，只允许第一次经过；如果它从别的端口绕回来，就直接丢掉。** 其他补充解释在上面的代码的注释中给出。
下面应用代码：
```bash
 uv run -m controllers.task2.loop_detecting_switch
loading app controllers.task2.loop_detecting_switch
loading app os_ken.controller.ofp_handler
instantiating app controllers.task2.loop_detecting_switch of Switch_Dict
instantiating app os_ken.controller.ofp_handler of OFPHandler
# 打开另一个终端
 sudo uv run topos/topo_1969_2.py
*** Creating network
*** Adding controller
*** Adding hosts:
SRI UCLA UCSB UTAH 
*** Adding switches:
s1 s2 s3 s4 
*** Adding links:
(s1, SRI) (10.00Mbit) (10.00Mbit) (s1, s2) (10.00Mbit) (10.00Mbit) (s1, s3) (10.00Mbit) (10.00Mbit) (s1, s4) (s2, UTAH) (s3, UCSB) (10.00Mbit) (10.00Mbit) (s3, s4) (s4, UCLA) 
*** Configuring hosts
SRI UCLA UCSB UTAH 
*** Starting controller
c0 
*** Starting 4 switches
s1 s2 s3 s4 ...(10.00Mbit) (10.00Mbit) (10.00Mbit) (10.00Mbit) (10.00Mbit) (10.00Mbit) (10.00Mbit) (10.00Mbit) 
SRI SRI-eth0:s1-eth1
UCLA UCLA-eth0:s4-eth1
UCSB UCSB-eth0:s3-eth1
UTAH UTAH-eth0:s2-eth1
*** Starting CLI:
mininet> UCSB wireshark &
mininet> UCLA ping UTAH -c 4
PING 10.0.0.4 (10.0.0.4) 56(84) bytes of data.
64 bytes from 10.0.0.4: icmp_seq=1 ttl=64 time=16.6 ms
64 bytes from 10.0.0.4: icmp_seq=2 ttl=64 time=0.629 ms
64 bytes from 10.0.0.4: icmp_seq=3 ttl=64 time=0.093 ms
64 bytes from 10.0.0.4: icmp_seq=4 ttl=64 time=0.089 ms

--- 10.0.0.4 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3048ms
rtt min/avg/max/mdev = 0.089/4.343/16.562/7.057 ms
mininet> 
```
wireshark的抓包结果如下：
![](../../../attachments/Pasted%20image%2020260508174316.png)

使用`dpctl dump-flows`来查看交换机的流表命中次数，结果如下：
```bash
mininet> dpctl dump-flows
*** s1 ------------------------------------------------------------------------
 cookie=0x0, duration=149.994s, table=0, n_packets=5, n_bytes=434, priority=1,in_port="s1-eth2",dl_src=46:83:0f:e4:8a:9c,dl_dst=ae:32:45:0a:b4:07 actions=output:"s1-eth4"
 cookie=0x0, duration=149.990s, table=0, n_packets=4, n_bytes=336, priority=1,in_port="s1-eth4",dl_src=ae:32:45:0a:b4:07,dl_dst=46:83:0f:e4:8a:9c actions=output:"s1-eth2"
 cookie=0x0, duration=165.871s, table=0, n_packets=100, n_bytes=15393, priority=0 actions=CONTROLLER:65535
*** s2 ------------------------------------------------------------------------
 cookie=0x0, duration=150.010s, table=0, n_packets=5, n_bytes=434, priority=1,in_port="s2-eth1",dl_src=46:83:0f:e4:8a:9c,dl_dst=ae:32:45:0a:b4:07 actions=output:"s2-eth2"
 cookie=0x0, duration=150.003s, table=0, n_packets=4, n_bytes=336, priority=1,in_port="s2-eth2",dl_src=ae:32:45:0a:b4:07,dl_dst=46:83:0f:e4:8a:9c actions=output:"s2-eth1"
 cookie=0x0, duration=165.885s, table=0, n_packets=42, n_bytes=5779, priority=0 actions=CONTROLLER:65535
*** s3 ------------------------------------------------------------------------
 cookie=0x0, duration=165.899s, table=0, n_packets=69, n_bytes=10416, priority=0 actions=CONTROLLER:65535
*** s4 ------------------------------------------------------------------------
 cookie=0x0, duration=150.035s, table=0, n_packets=5, n_bytes=434, priority=1,in_port="s4-eth2",dl_src=46:83:0f:e4:8a:9c,dl_dst=ae:32:45:0a:b4:07 actions=output:"s4-eth1"
 cookie=0x0, duration=150.034s, table=0, n_packets=4, n_bytes=336, priority=1,in_port="s4-eth1",dl_src=ae:32:45:0a:b4:07,dl_dst=46:83:0f:e4:8a:9c actions=output:"s4-eth2"
 cookie=0x0, duration=165.915s, table=0, n_packets=71, n_bytes=10600, priority=0 actions=CONTROLLER:65535
mininet> 
```
这个流表结果是正常的，说明实验二中的环路广播抑制已经生效。可以看到，s1、s2 和 s4 上都已经安装了优先级为 1 的单播转发表项，分别匹配源 MAC、目的 MAC 和入端口，并将数据包定向输出到对应端口；这些表项的 `n_packets` 只有 4 到 5 次，与一次 `ping -c 4` 产生的少量 ICMP/ARP 通信规模基本一致，说明后续数据包**已经按照自学习结果在交换机中直接转发，没有出现异常的重复转发**。与此同时，各交换机仍**保留优先级为 0 的默认 table-miss 规则**，将未知流量送到控制器处理；其计数虽然存在，但没有像环路未处理时那样迅速增长到成百上千次。这表明广播 ARP 没有在环形拓扑中持续绕圈泛洪，**控制器对重复 ARP 广播的丢弃策略起到了作用，因此网络能够恢复正常通信**。
### 任务三：最小时延路径
传统的网络中，每个路由器只知道自己邻居的状态，所以决定最短路的方法有限，通常是以跳数（Hop）为准。而在SDN架构，由于控制器和各个网络节点解耦，它便可以实时监控每一条链路的性能（时延/带宽等），并构建出全局上更合理的最优路。本任务内容就是配置控制器，以时延为新的判断标准，确定最短路。
#### 代码修改
本实验在任务二的基础上，实现了基于链路时延的最短路径转发，而不是继续采用最少跳数策略。为完成这一目标，主要修改了 `.venv/lib/python3.14/site-packages/os_ken/topology/switches.py`、`controllers/network_awareness.py`，并新建了 `controllers/task3/shortest_forward.py`。

`controllers/task3/shortest_forward.py` 完整代码如下：

```python
from os_ken import cfg
from os_ken import log
from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import MAIN_DISPATCHER
from os_ken.controller.handler import set_ev_cls
from os_ken.ofproto import ofproto_v1_3
from os_ken.lib.packet import packet
from os_ken.lib.packet import ethernet, arp, ipv4

from controllers.network_awareness import NetworkAwareness

ETHERNET_MULTICAST = "ff:ff:ff:ff:ff:ff"
ARP = arp.arp.__name__


class ShortestForward(app_manager.OSKenApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'network_awareness': NetworkAwareness}

    def __init__(self, *args, **kwargs):
        super(ShortestForward, self).__init__(*args, **kwargs)
        self.network_awareness = kwargs['network_awareness']
        # 关键点1：将拓扑图的最短路径权重从 hop 切换为 delay
        # 后续 shortest_path() 会按链路时延而不是按跳数选路
        self.network_awareness.weight = 'delay'
        self.weight = 'delay'
        self.mac_to_port = {}
        self.sw = {}
        self.path = None

    def add_flow(self, datapath, priority, match, actions, idle_timeout=0, hard_timeout=0):
        dp = datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=dp, priority=priority,
            idle_timeout=idle_timeout,
            hard_timeout=hard_timeout,
            match=match, instructions=inst)
        dp.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        if eth_pkt is None:
            return

        arp_pkt = pkt.get_protocol(arp.arp)
        ipv4_pkt = pkt.get_protocol(ipv4.ipv4)
        pkt_type = eth_pkt.ethertype
        dst_mac = eth_pkt.dst
        src_mac = eth_pkt.src

        # 关键点2：ARP 报文沿用任务二的处理逻辑
        # 既负责基础二层转发，也负责处理广播 ARP 的环路问题
        if isinstance(arp_pkt, arp.arp):
            self.handle_arp(msg, in_port, dst_mac, src_mac, arp_pkt)

        # 关键点3：只有 IPv4 报文才进入基于时延的路径计算流程
        if isinstance(ipv4_pkt, ipv4.ipv4):
            self.handle_ipv4(msg, ipv4_pkt.src, ipv4_pkt.dst, pkt_type)

    def handle_arp(self, msg, in_port, dst, src, arp_pkt):
        dp = msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        dpid = dp.id

        if dst == ETHERNET_MULTICAST:
            # 关键点4：记录 (dpid, src_mac, dst_ip) -> in_port
            # 若同一广播 ARP 从其他端口再次进入该交换机，则直接丢弃
            arp_key = (dpid, src, arp_pkt.dst_ip)
            prev_port = self.sw.get(arp_key)
            if prev_port is not None and prev_port != in_port:
                return
            self.sw[arp_key] = in_port

        # 关键点5：保留任务一中的 MAC 自学习逻辑
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofp.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]
        if out_port != ofp.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            self.add_flow(dp, 1, match, actions)

        out = parser.OFPPacketOut(
            datapath=dp, buffer_id=msg.buffer_id,
            in_port=in_port, actions=actions, data=msg.data)
        dp.send_msg(out)

    def handle_ipv4(self, msg, src_ip, dst_ip, pkt_type):
        parser = msg.datapath.ofproto_parser

        # 关键点6：按 delay 权重计算从源主机到目的主机的最小时延路径
        dpid_path = self.network_awareness.shortest_path(src_ip, dst_ip, weight=self.weight)
        if not dpid_path:
            return

        self.path = dpid_path
        port_path = []
        # 关键点7：将节点路径转换成端口路径
        # 结果形式为 (in_port, dpid, out_port)，便于逐交换机下发流表
        for i in range(1, len(dpid_path) - 1):
            in_port = self.network_awareness.link_info[(dpid_path[i], dpid_path[i - 1])]
            out_port = self.network_awareness.link_info[(dpid_path[i], dpid_path[i + 1])]
            port_path.append((in_port, dpid_path[i], out_port))

        if not port_path:
            return

        self.show_path(src_ip, dst_ip, port_path)

        # 关键点8：在路径上的每台交换机上下发双向 IPv4 流表
        # 这样后续同类报文无需再次送控制器处理
        for in_port, dpid, out_port in port_path:
            self.send_flow_mod(parser, dpid, pkt_type, src_ip, dst_ip, in_port, out_port)
            self.send_flow_mod(parser, dpid, pkt_type, dst_ip, src_ip, out_port, in_port)

        # 关键点9：当前触发 packet_in 的这个数据包还没有被交换机转发
        # 因此需要额外发送一次 packet_out，将它从最后一跳交换机送出去
        last_in_port, last_dpid, last_out_port = port_path[-1]
        dp = self.network_awareness.switch_info[last_dpid]
        actions = [parser.OFPActionOutput(last_out_port)]
        out = parser.OFPPacketOut(
            datapath=dp, buffer_id=msg.buffer_id, in_port=last_in_port,
            actions=actions, data=msg.data)
        dp.send_msg(out)

    def send_flow_mod(self, parser, dpid, pkt_type, src_ip, dst_ip, in_port, out_port):
        dp = self.network_awareness.switch_info[dpid]
        match = parser.OFPMatch(
            in_port=in_port, eth_type=pkt_type, ipv4_src=src_ip, ipv4_dst=dst_ip)
        actions = [parser.OFPActionOutput(out_port)]
        # 空闲超时和硬超时用于让旧路径规则在一段时间后自动失效
        self.add_flow(dp, 1, match, actions, 10, 30)

    def show_path(self, src, dst, port_path):
        self.logger.info('path: %s -> %s', src, dst)
        path = src + ' -> '
        total_delay = 0.0
        for _, dpid, _ in port_path:
            path += 's{} -> '.format(dpid)

        dpid_path = [src]
        for _, dpid, _ in port_path:
            dpid_path.append(dpid)
        dpid_path.append(dst)

        # 关键点10：根据 topo_map 中每条交换机链路的 delay 权重累加总时延
        for i in range(1, len(dpid_path) - 2):
            u = dpid_path[i]
            v = dpid_path[i + 1]
            total_delay += self.network_awareness.topo_map[u][v].get('delay', 0)

        path += dst
        self.logger.info('%s', path)
        self.logger.info('total delay: %.3f ms', total_delay * 1000)


if __name__ == '__main__':
    cfg.CONF()
    cfg.CONF.set_override('observe_links', True)
    log.init_log()
    app_manager.AppManager.run_apps(["controllers.task3.shortest_forward"])
```

`controllers/network_awareness.py` 的主要修改如下：

```diff
--- a/controllers/network_awareness.py
+++ b/controllers/network_awareness.py
@@
 from os_ken.lib.packet import packet
 from os_ken.lib.packet import ethernet, arp
 from os_ken.lib import hub
 from os_ken.topology import event
 from os_ken.topology.api import get_host, get_link, get_switch
 from os_ken.topology.switches import LLDPPacket
 import os_ken.topology.switches
+from os_ken.controller.handler import HANDSHAKE_DISPATCHER
+# 为 Echo Reply 事件增加握手阶段的调度器支持
@@
          self.port_info = {}  # dpid: (ports linked hosts)
          self.topo_map = nx.Graph()
          self.topo_thread = hub.spawn(self._get_topology)
+        self.delay_thread = hub.spawn(self._get_delay)
+        self.echo_delay = {}
+        self.lldp_delay = {}
+        self.switches = None
+        # 新增一个并发线程周期性测量时延
+        # echo_delay: 保存控制器到交换机的往返时延
+        # lldp_delay: 保存交换机到交换机方向上的 LLDP 时延
+        # switches: 通过 lookup_service_brick 获取 switches 实例
@@
              if self.weight == 'hop':
                  self.show_topo_map()
              hub.sleep(GET_TOPOLOGY_INTERVAL)
+
+    def _get_delay(self):
+        hub.sleep(0.1)
+        while True:
+            self._send_echo_requests()
+            hub.sleep(SEND_ECHO_REQUEST_INTERVAL)
+            self._update_link_delay()
+            hub.sleep(GET_DELAY_INTERVAL)
+        # 周期性流程：先发 Echo，再更新链路 delay 权重
+
+    def _send_echo_requests(self):
+        for dp in list(self.switch_info.values()):
+            parser = dp.ofproto_parser
+            data = ('%.12f' % time.time()).encode('ascii')
+            req = parser.OFPEchoRequest(dp, data=data)
+            dp.send_msg(req)
+        # 向每台交换机发送带时间戳的 Echo Request
+        # 后续通过 Echo Reply 计算控制器到该交换机的 RTT
+
+    def _update_link_delay(self):
+        if self.switches is None:
+            self.switches = lookup_service_brick('switches')
+        if self.switches is None:
+            return
+
+        for src, dst, data in self.topo_map.edges(data=True):
+            if data.get('is_host'):
+                data['delay'] = 0
+                continue
+            # 主机到交换机的边不参与链路时延计算，直接记为 0
+
+            lldp_forward = self.lldp_delay.get((src, dst))
+            lldp_reverse = self.lldp_delay.get((dst, src))
+            echo_src = self.echo_delay.get(src)
+            echo_dst = self.echo_delay.get(dst)
+            if None in (lldp_forward, lldp_reverse, echo_src, echo_dst):
+                data['delay'] = 0
+                continue
+            # 若双向 LLDP 时延或两端交换机的 Echo 时延有任一缺失
+            # 暂时无法计算该链路 delay，先记为 0
+
+            delay = (lldp_forward + lldp_reverse - echo_src - echo_dst) / 2
+            data['delay'] = max(delay, 0)
+            # 按实验要求使用：
+            # (lldp_s12 + lldp_s21 - echo_s1 - echo_s2) / 2
+            # 若结果小于 0，则截断为 0
+
+    @set_ev_cls(ofp_event.EventOFPEchoReply, [MAIN_DISPATCHER, HANDSHAKE_DISPATCHER])
+    def echo_reply_handler(self, ev):
+        now = time.time()
+        try:
+            sent = float(ev.msg.data.decode('ascii'))
+        except (AttributeError, ValueError, UnicodeDecodeError):
+            return
+        self.echo_delay[ev.msg.datapath.id] = max(now - sent, 0)
+        # 收到 Echo Reply 后，计算控制器到交换机的往返时延
+
+    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
+    def lldp_packet_in_handler(self, ev):
+        msg = ev.msg
+        dpid = msg.datapath.id
+        try:
+            src_dpid, src_port_no = LLDPPacket.lldp_parse(msg.data)
+        except Exception:
+            return
+
+        if self.switches is None:
+            self.switches = lookup_service_brick('switches')
+        if self.switches is None:
+            return
+
+        for port in self.switches.ports.keys():
+            if src_dpid == port.dpid and src_port_no == port.port_no:
+                self.lldp_delay[(src_dpid, dpid)] = self.switches.ports[port].delay
+                break
+        # 将 switches 模块中记录的端口 LLDP 时延提取出来
+        # 保存成 (src_switch, dst_switch) -> lldp_delay 的形式
```

其中，`network_awareness.py` 的修改核心在于为拓扑图中的交换机链路补充 `delay` 权重，并持续更新该权重；`shortest_forward.py` 则在收到 `IPv4` 报文时，按 `delay` 权重计算最小时延路径，随后下发流表实现基于时延的转发。
#### 实验结果
> *控制器将带有时间戳的`LLDP`报文下发给`S1`，`S1`转发给`S2`，`S2`上传回控制器（即内圈红色箭头的路径），根据收到的时间和发送时间即可计算出**控制器经`S1`到`S2`再返回控制器的时延**，记为`lldp_delay_s12`。反之，**控制器经`S2`到`S1`再返回控制器的时延**，记为`lldp_delay_s21`。交换机收到控制器发来的Echo报文后会立即回复控制器，我们可以利用`Echo Request/Reply`报文求出**控制器到`S1`、`S2`的往返时延**，记为`echo_delay_s1`, `echo_delay_s2`。*
> *则`S1`到`S2`的时延 `delay = (lldp_delay_s12 + lldp_delay_s21 - echo_delay_s1 - echo_delay_s2) / 2`*


实验中使用 `topos/topo_1970.py` 提供的 9 节点拓扑，启动控制器 `controllers.task3.shortest_forward` 后进行测试。

先使用`dump`查看主机与IP的对应关系：
```bash
mininet> dump
<Host BBN: BBN-eth0:10.0.0.1 pid=237293> 
<Host HARVARD: HARVARD-eth0:10.0.0.2 pid=237295> 
<Host MIT: MIT-eth0:10.0.0.3 pid=237297> 
<Host RAND: RAND-eth0:10.0.0.4 pid=237299> 
<Host SDC: SDC-eth0:10.0.0.5 pid=237301> 
<Host SRI: SRI-eth0:10.0.0.6 pid=237303> 
<Host UCLA: UCLA-eth0:10.0.0.7 pid=237305> 
<Host UCSB: UCSB-eth0:10.0.0.8 pid=237307> 
<Host UTAH: UTAH-eth0:10.0.0.9 pid=237309> 
<OVSSwitch s1: lo:127.0.0.1,s1-eth1:None,s1-eth2:None pid=237314> 
<OVSSwitch s2: lo:127.0.0.1,s2-eth1:None,s2-eth2:None,s2-eth3:None pid=237317> 
<OVSSwitch s3: lo:127.0.0.1,s3-eth1:None,s3-eth2:None,s3-eth3:None pid=237320> 
<OVSSwitch s4: lo:127.0.0.1,s4-eth1:None,s4-eth2:None,s4-eth3:None,s4-eth4:None pid=237323> 
<OVSSwitch s5: lo:127.0.0.1,s5-eth1:None,s5-eth2:None,s5-eth3:None,s5-eth4:None pid=237326> 
<OVSSwitch s6: lo:127.0.0.1,s6-eth1:None,s6-eth2:None,s6-eth3:None pid=237329> 
<OVSSwitch s7: lo:127.0.0.1,s7-eth1:None,s7-eth2:None,s7-eth3:None pid=237332> 
<OVSSwitch s8: lo:127.0.0.1,s8-eth1:None,s8-eth2:None,s8-eth3:None pid=237335> 
<OVSSwitch s9: lo:127.0.0.1,s9-eth1:None,s9-eth2:None,s9-eth3:None,s9-eth4:None pid=237338> 
<RemoteController c0: 127.0.0.1:6633 pid=237284> 
```

执行 `pingall` 触发主机：

```bash
mininet> pingall
*** Ping: testing ping reachability
BBN -> X X X X X X X X 
HARVARD -> BBN MIT RAND SDC SRI UCLA UCSB UTAH 
MIT -> BBN HARVARD RAND SDC SRI UCLA UCSB UTAH 
RAND -> BBN HARVARD MIT SDC SRI UCLA UCSB UTAH 
SDC -> BBN HARVARD MIT RAND SRI UCLA UCSB UTAH 
SRI -> BBN HARVARD MIT RAND SDC UCLA UCSB UTAH 
UCLA -> BBN HARVARD MIT RAND SDC SRI UCSB UTAH 
UCSB -> BBN HARVARD MIT RAND SDC SRI UCLA UTAH 
UTAH -> BBN HARVARD MIT RAND SDC SRI UCLA UCSB 
*** Results: 11% dropped (64/72 received)
```

结果显示整体网络基本连通，仅有 `BBN` 在首次探测阶段存在丢包现象，`72` 个测试中成功 `64` 个，丢包率为 `11%`。这与 README 中提到的“沉默主机”现象一致，即**在控制器尚未完全学习到主机和路径信息之前，前几次转发可能失败，属于正常现象。**

随后执行 `SDC ping MIT -c 4`

```bash
mininet> SDC ping MIT -c 4
PING 10.0.0.3 (10.0.0.3) 56(84) bytes of data.
64 bytes from 10.0.0.3: icmp_seq=1 ttl=64 time=128 ms
64 bytes from 10.0.0.3: icmp_seq=2 ttl=64 time=126 ms
64 bytes from 10.0.0.3: icmp_seq=3 ttl=64 time=126 ms
64 bytes from 10.0.0.3: icmp_seq=4 ttl=64 time=127 ms

--- 10.0.0.3 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3004ms
rtt min/avg/max/mdev = 126.281/126.669/127.504/0.497 ms
```

这说明控制器已经能够根据测得的链路时延正确下发转发表项，使 `SDC` 与 `MIT` 之间稳定通信。

根据控制器输出，实验中计算得到的路径为：

```text
path: 10.0.0.3 -> 10.0.0.5
10.0.0.3 -> s8 -> s9 -> s5 -> s6 -> 10.0.0.5
total delay: 2.638 ms
```
> 因为控制器并不会对每一个 ping 报文都重复输出路径，而只会在某个方向的 IPv4 报文首次触发 PacketIn 时计算并打印一次路径。由于 ping 本身包含请求和应答两个方向的通信，而交换机在首次触发后就已经安装了双向流表，因此后续同类报文将直接由交换机转发，不再上送控制器。<u>*所以只能看到从MIT到SDC的path，而不能看到`ping`要求的SDC到MIT。*</u>

从拓扑文件预设链路时延来看，这条路径经过的核心链路 `s6-s5`、`s5-s9`、`s9-s8` 的时延分别约为 `17 ms`、`29 ms` 和 `17 ms`（在`topo_1970.py`中已经规定好了），单向时延总和约为 `63 ms`，因此往返时延理论上约为 `126 ms`。实验中测得 `SDC ping MIT` 的平均 `RTT = 126.669 ms`，与理论值非常接近，说明控制器虽然日志中打印的是反向路径，但其对应的实际双向转发路径与最小时延路径预期一致，也说明基于 `LLDP` 和 `Echo` 的链路时延测量与基于时延权重的路由计算是有效的。