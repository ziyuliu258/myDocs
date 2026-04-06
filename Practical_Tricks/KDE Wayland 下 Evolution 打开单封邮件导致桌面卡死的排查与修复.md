## 问题现象

在 `KDE Plasma + Wayland` 环境下，`Evolution` 本身可以正常启动，也可以正常浏览邮件列表，但只要双击打开某一封具体邮件的详情窗口，整个桌面交互就会被拖死，表现为：

- `Evolution` 的详情窗口还能看到，但几乎无法正常操作。
- KDE 桌面、面板、其他窗口基本都点不动。
- 只有把这个邮件详情窗口关掉，再彻底退出 `Evolution`，桌面才会恢复。

这类现象很容易被误判成：

- `KDE` 自己卡死了
- 显卡驱动坏了
- 系统资源爆了

但这次实际情况并不是简单的整机性能问题。

## 这次环境里的关键信息

- 桌面环境：`KDE Plasma`
- 会话类型：`Wayland`
- 邮件客户端：`Evolution 3.58.3`
- `WebKitGTK`：`2.50.6`

## 为什么判断不是普通的“系统卡”

这次排查里有几个关键特征：

- 打开邮件列表本身是正常的。
- 关闭自动预览后，进入列表依然正常。
- 只有双击打开某一封具体邮件的详情窗口时才稳定触发问题。

这说明问题不在：

- 邮件文件夹索引本身
- IMAP 同步本身
- 普通的列表渲染

而是在“单封邮件详情页”的渲染路径上。

## 日志里看到的关键信号

用户会话日志里可以看到：

```text
kwin_wayland: Invalid framebuffer status: "GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT"
kwin_wayland: Failed to create an offscreen framebuffer
kwin_wayland: The requested buffer size is too big, ignoring
org.gnome.Evolution: 已到超时限制
```

这说明：

1. `Evolution` 在打开那封邮件时卡在渲染或 UI 路径里。
2. 这个渲染结果还进一步触发了 `Wayland/KWin` 的图形缓冲区异常。
3. 所以表面上看起来像“整个 KDE 桌面都死了”，但触发源头仍然是 `Evolution` 打开单封邮件时的图形渲染路径。

## 排查过程中确认过的几件事

### 1. 关闭预览只能缓解一部分问题

先把：

```bash
gsettings set org.gnome.evolution.mail show-mails-in-preview false
```

以及各文件夹的 `PreviewVisible` 关闭后，进入邮件列表已经不再卡死。

这说明：

- 自动预览确实会放大问题
- 但根因不只是“预览窗格”，因为双击单封邮件仍然会卡

### 2. 本地界面状态里曾有异常尺寸值

这次还发现 `Evolution` 的某些分栏尺寸状态不正常，例如：

```text
org.gnome.evolution.mail paned-size = 1155893
```

这明显不是正常 UI 尺寸。把这些值恢复到正常范围后，列表视图变稳定了，但仍然不能彻底解决“打开具体邮件详情窗口卡死”的问题。

也就是说：

- 本地状态损坏是问题的一部分
- 但不是最后的根因

### 3. 根因更像是 Wayland 下的渲染兼容问题

由于问题只在“打开单封邮件详情窗口”时触发，并且同时伴随 `kwin_wayland` 的 framebuffer / buffer size 异常，这次更合理的判断是：

- 某封邮件内容触发了 `Evolution + WebKitGTK + Wayland/GL` 这一条渲染路径的兼容问题
- 最终把 `KWin` 的图形交互也一并拖住了

## 最终有效的解决方案

这次真正有效的方案，不是改系统全局环境变量，而是只改 `Evolution` 的用户级桌面启动器，让它启动时走更保守的渲染路径：

```desktop
Exec=env GDK_BACKEND=x11 WEBKIT_DISABLE_COMPOSITING_MODE=1 LIBGL_ALWAYS_SOFTWARE=1 evolution %U
```

含义分别是：

- `GDK_BACKEND=x11`
  - 强制 `Evolution` 走 `X11/XWayland`，绕开当前 Wayland 下的坏路径。
- `WEBKIT_DISABLE_COMPOSITING_MODE=1`
  - 禁用 `WebKit` 合成模式，减少触发图形合成相关问题的概率。
- `LIBGL_ALWAYS_SOFTWARE=1`
  - 强制使用软件渲染，避免显卡驱动或 GL 合成路径继续参与这个问题。

## 这次实际修改的是哪里

最终生效的是用户级桌面文件：

[`/home/ziyu/.local/share/applications/org.gnome.Evolution.desktop`](/home/ziyu/.local/share/applications/org.gnome.Evolution.desktop)

其中当前的关键配置是：

```desktop
Exec=env GDK_BACKEND=x11 WEBKIT_DISABLE_COMPOSITING_MODE=1 LIBGL_ALWAYS_SOFTWARE=1 evolution %U
```

这种改法的优点是：

- 只影响 `Evolution`
- 不影响别的程序
- 不会修改系统级环境变量
- 不会污染 shell 登录环境

## 这次没有动的东西

为了避免影响其他程序，这次没有改：

- `/etc/environment`
- `~/.zshrc`
- `~/.profile`
- KDE / Plasma 的系统级图形配置
- 全局 `GDK_BACKEND`
- 全局 `LIBGL_ALWAYS_SOFTWARE`

也就是说，环境变量只在 `Evolution` 这个应用启动时生效，其他程序不受影响。

## 如果以后还遇到类似问题，建议的排查顺序

### 1. 先确认问题发生在“列表”还是“单封邮件详情”

- 如果只是进入列表就卡，先关掉自动预览。
- 如果列表没事，但双击单封邮件会卡，重点怀疑详情页渲染路径。

### 2. 看用户会话日志

```bash
journalctl --user -b --no-pager | rg -i 'evolution|kwin|webkit|framebuffer|buffer size|timeout'
```

如果同时看到：

- `Evolution` 超时
- `kwin_wayland` 的 framebuffer / buffer size 报错

那就很像这次这种 Wayland 图形路径兼容问题。

### 3. 先做低风险修复

例如：

```bash
gsettings set org.gnome.evolution.mail show-mails-in-preview false
```

必要时再重置相关分栏尺寸和 `state.ini` 中的预览状态。

### 4. 如果问题只在单封邮件详情窗口触发

优先考虑：

- 改 `Evolution` 的桌面启动器，让它走 `X11/XWayland`
- 关闭 `WebKit` 合成
- 必要时强制软件渲染

而不是一上来就改全局系统变量。

## 结论

这次问题的本质不是“整个 KDE 桌面莫名其妙坏掉”，而是：

- `Evolution` 在打开某封具体邮件详情时触发了渲染异常
- 这个异常又在 `Wayland/KWin` 图形路径里被放大
- 最终表现成“除了那个详情窗口外，整个桌面都像冻结了一样”

最稳妥的修复方式是：

- 保守化 `Evolution` 自己的启动环境
- 把兼容性 workaround 限定在应用级，而不是系统级

这次采用的用户级桌面文件 override 就属于这种最小影响方案。
