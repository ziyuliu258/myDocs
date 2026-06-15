## 背景

这条记录用于说明本机为什么可以通过网线直连开发板，并让开发板通过本机 WiFi 出网。

开发板固定使用的地址是：

```text
192.168.137.30
```

本机有线网卡作为开发板的网关，地址是：

```text
192.168.137.1/24
```

## 本机设置命令

之前在本机执行过下面这条命令：

```bash
sudo nmcli connection add type ethernet ifname enp4s0 con-name Board-Sharing ipv4.method shared ipv4.addresses 192.168.137.1/24
```

这条命令会创建一个 NetworkManager 连接：

```text
连接名：Board-Sharing
网卡：enp4s0
IPv4 模式：shared
本机地址：192.168.137.1/24
```

## 关键点

`ipv4.method shared` 是核心配置。

它会让 NetworkManager 把 `enp4s0` 当作下游共享网口使用。本机在这个网段里作为网关，开发板通过网线接入后，可以把本机的 `192.168.137.1` 当作默认网关。

当前本机如果 WiFi 是默认出网接口，例如 `wlan0`，那么开发板的流量会通过本机转发出去。这个配置不需要写死共享哪个 WiFi，它跟随本机当前的默认出网连接。

## 当前连接内容

可以用下面命令查看：

```bash
nmcli con show Board-Sharing
```

关键字段应类似：

```text
connection.id:                          Board-Sharing
connection.type:                        802-3-ethernet
connection.interface-name:              enp4s0
connection.autoconnect:                 yes
ipv4.method:                            shared
ipv4.addresses:                         192.168.137.1/24
GENERAL.STATE:                          activated
IP4.ADDRESS[1]:                         192.168.137.1/24
IP4.ROUTE[1]:                           dst = 192.168.137.0/24, nh = 0.0.0.0
```

也可以看当前路由：

```bash
ip route show
```

应能看到类似：

```text
192.168.137.0/24 dev enp4s0 proto kernel scope link src 192.168.137.1
```

## 为什么现在插上就能用

因为 `Board-Sharing` 是 NetworkManager 保存的持久连接，并且默认会自动连接：

```text
connection.autoconnect: yes
```

所以插上网线后，NetworkManager 会自动激活这个连接，把 `enp4s0` 配成 `192.168.137.1/24`，并启动共享网络需要的 DHCP/DNS/转发逻辑。

开发板如果已经固定为：

```text
IP：192.168.137.30/24
网关：192.168.137.1
```

那么本机和开发板就在同一个网段里，可以直接 SSH 连接：

```bash
ssh HwHiAiUser@192.168.137.30
```

## 开发板侧对应配置

开发板侧以前需要处理的是固定有线口 IP 和网关，避免 NetworkManager 自动改掉地址。

常见配置目标：

```text
开发板 eth0：192.168.137.30/24
默认网关：192.168.137.1
DNS：按需配置，例如 114.114.114.114 或 8.8.8.8
```

如果开发板也由 NetworkManager 管理，可以使用类似命令：

```bash
sudo nmcli con mod "Wired connection 1" ipv4.method manual ipv4.addresses 192.168.137.30/24 ipv4.gateway 192.168.137.1
sudo nmcli con mod "Wired connection 1" ipv4.dns "114.114.114.114 8.8.8.8"
sudo nmcli con down "Wired connection 1"
sudo nmcli con up "Wired connection 1"
```

实际连接名可能不是 `"Wired connection 1"`，需要先在开发板上用 `nmcli` 查看。

## 常用操作

手动启用本机共享连接：

```bash
sudo nmcli con up Board-Sharing
```

手动关闭本机共享连接：

```bash
sudo nmcli con down Board-Sharing
```

删除这个连接：

```bash
sudo nmcli con delete Board-Sharing
```

重新创建这个连接：

```bash
sudo nmcli connection add type ethernet ifname enp4s0 con-name Board-Sharing ipv4.method shared ipv4.addresses 192.168.137.1/24
```

## 排查命令

查看当前活动连接：

```bash
nmcli con show --active
```

查看有线网卡地址：

```bash
ip addr show enp4s0
```

查看到开发板是否可达：

```bash
ping 192.168.137.30
```

查看 SSH 是否可用：

```bash
ssh HwHiAiUser@192.168.137.30
```

