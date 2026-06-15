## 问题现象

一次 Arch / EndeavourOS 更新后，`fcitx5-rime` 突然无法正常使用，表现为：

- 无法切换到中文输入法。
- 看起来像是 `rime` 坏了，但实际上不一定是整个输入法框架失效。
- 在 Wayland + KDE Plasma 环境下，症状容易被误判成环境变量、托盘或自动启动问题。

这次机器上的实际环境是：

- 桌面环境：KDE Plasma
- 会话类型：Wayland
- 输入法框架：`fcitx5`
- Rime 前端：`fcitx5-rime`
- 方案：`rime-ice-git`

## 为什么会出问题

这次真正的根因，不是 `fcitx5` 主程序损坏，也不是 `fcitx5-rime` 包缺失，而是：

- 系统升级后，`librime` 和 Lua 运行环境变化了。
- `rime-ice-git` 自带的 Lua 脚本 `search.lua` 与当前环境不兼容。
- 报错点在 `search.lua` 中对 `for` 循环变量的二次赋值。

实际日志中的关键错误类似于：

```text
/usr/share/rime-data/lua/search.lua:24: attempt to assign to const variable 'i'
LuaTranslation::Next error: attempt to call a string value
```

也就是说：

1. `fcitx5` 本身可以启动。
2. `Rime` 插件也能被加载。
3. 但 `rime-ice-git` 里的 Lua 组件在运行时炸了，导致输入法表现异常。

### 为什么这行代码会报错

触发错误的代码在：

```lua
for i = 1, utf8.len( tmp ) do
    local first_char = tmp:sub( 1, utf8.offset( tmp, 2 ) - 1 )
    if first_char == char then pos[i] = true end
    tmp = tmp:gsub( '^' .. first_char, '' )
    i = i + 1
end
```

真正有问题的是最后这一句：

```lua
i = i + 1
```

原因如下：

1. `i` 是 `for` 循环的控制变量。
2. 在当前 Lua / librime-lua 运行环境里，这种循环变量不能再被手动赋值。
3. 因此执行到 `i = i + 1` 时，就会报：

```text
attempt to assign to const variable 'i'
```

更重要的是，这一行本身也是多余的，因为：

```lua
for i = 1, utf8.len( tmp ) do
```

这种数值 `for` 循环，每轮结束后会自动递增 `i`，不需要手动再加一次。

所以这次问题的本质不是“用户配置写错了”，而是：

- `rime-ice-git` 自带脚本里存在一行不规范但过去未必立刻爆炸的旧写法
- 系统升级后，运行环境变严格了
- 于是这行代码从“潜在问题”变成了“直接报错”

删除这一行后，函数逻辑并不会因此丢失关键行为，反而恢复了与当前运行环境的兼容性。

## 应该怎么排查

排查时不要一上来就认定是“包没装好”，建议按下面顺序看。

### 1. 先确认包是不是都还在

```bash
pacman -Q | rg '^(fcitx5|librime|rime|fcitx)'
```

重点看这些包是否存在：

- `fcitx5`
- `fcitx5-rime`
- `librime`
- `librime-data`
- `rime-ice-git` 或你自己的 Rime 方案包

### 2. 看最近更新了什么

```bash
rg -n 'fcitx|rime' /var/log/pacman.log | tail -n 80
```

如果问题是“更新之后突然坏掉”，这里通常能直接看到最近升级过的相关组件。

### 3. 先判断 `fcitx5` 是否真的没启动

```bash
fcitx5-diagnose
pgrep -a fcitx5
```

如果 `fcitx5-diagnose` 里提示：

```text
Fcitx5 is not running.
```

不要立刻断言是自动启动问题。因为还有一种可能是：

- `fcitx5` 启动了又马上退出
- 或者图形会话里其实已经有一个实例，只是当前终端环境看不到

### 4. 在用户会话里查日志

这个步骤最关键：

```bash
journalctl --user -b --no-pager | rg -i 'fcitx|rime|lua_gears|search\.lua' | tail -n 80
```

如果是 Rime Lua 组件报错，通常能直接在这里看到根因，而不是继续在环境变量上兜圈子。

### 5. 看 Rime 方案和用户目录

```bash
ls -la ~/.local/share/fcitx5/rime
ls -la ~/.local/share/fcitx5/rime/build
```

目的是确认：

- 用户词库目录还在不在
- 方案是否被正常编译
- `build` 目录里是否存在 `rime_ice.schema.yaml` 等文件

## 这次问题是怎么定位出来的

这次排查中，最终确认了几件事：

- `fcitx5`、`fcitx5-rime`、`librime` 都已安装。
- `Rime` addon 在 `fcitx5-diagnose` 里是存在的。
- KDE Wayland 已配置 `fcitx5-wayland-launcher`。
- 用户日志里可以看到 `Loaded addon rime`，说明 `rime` 插件本身被加载了。
- 随后紧接着出现 `search.lua` 的 Lua 错误。

因此可以排除：

- 包没装
- `fcitx5-rime` 缺库
- profile 里没加 `rime`
- 单纯的 KDE 自动启动失效

最终锁定为：

- `rime-ice-git` 提供的 Lua 脚本与更新后的环境不兼容

## 怎么解决

### 方案一：用户目录覆盖修复脚本

这是这次采用的最小修复方案，不改系统包，只在用户目录放覆盖文件。

创建文件：

```text
~/.local/share/fcitx5/rime/lua/search.lua
```

把系统里的：

```text
/usr/share/rime-data/lua/search.lua
```

复制一份到用户目录，然后把有问题的这一行删掉：

```lua
i = i + 1
```

原因是这行对当前 Lua 运行环境不兼容，而且在这个 `for` 循环里本身就是多余的。

### 方案二：重新登录图形会话

改完后建议：

1. 注销当前 KDE Plasma 会话
2. 重新登录
3. 测试 `Ctrl+Space`

这样最稳，因为 `fcitx5`、Rime 和 Wayland 输入法前端都会被完整重启。

### 方案三：如果还不行，先临时停用 `rime-ice-git`

如果你急着恢复可用输入法，而不是继续深挖，可以先卸载有问题的方案包：

```bash
yay -Rns rime-ice-git
```

然后改用较基础的内置方案，例如：

- `luna_pinyin`
- 或其他不依赖这套 Lua 扩展的方案

这样通常能先恢复输入法可用性。

## 修复后如何验证

可以用下面几种方式验证：

### 1. 看 `fcitx5` 是否在图形会话中运行

```bash
pgrep -a fcitx5
```

### 2. 再查一次日志

```bash
journalctl --user -b --no-pager | rg -i 'fcitx|rime|lua_gears|search\.lua' | tail -n 80
```

如果修复成功，之前那类 `search.lua` / `lua_gears` 错误应该不再继续刷。

### 3. 实际输入测试

重点看：

- 是否能切到 `rime`
- 是否能正常上屏中文
- 候选词是否正常显示

## 经验总结

这类问题的经验是：

1. `fcitx5-rime` 出问题时，不要先假设是环境变量错了。
2. 先区分是 `fcitx5` 主框架没起来，还是 `Rime` 插件/方案出错。
3. 在 Wayland + Plasma 下，`journalctl --user` 往往比 `fcitx5-diagnose` 更接近真实根因。
4. 如果错误落在 `rime-ice-git`、Lua 脚本、第三方方案扩展上，优先考虑“方案兼容性问题”，而不是重装整个输入法框架。
5. 用户目录覆盖修复通常比直接改系统文件更稳，也更容易回退。

## 这次最终结论

这次故障的本质是：

- Arch 更新后，`rime-ice-git` 的 Lua 扩展脚本和当前系统环境不兼容
- 不是 `fcitx5` 主程序坏了
- 不是 `fcitx5-rime` 包缺失
- 通过在用户目录覆盖修复 `search.lua`，可以以最小代价恢复
