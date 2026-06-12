# 网易云音乐问题诊断与解决方案总结

## 问题概述

网易云音乐在 Arch Linux 系统上遇到三个主要问题：

1. **画面比例不对** - 需要 150%-200% 缩放才能正常使用
2. **无法联网** - 应用无法连接到网易云音乐服务器
3. **个性推荐页面无法加载** - 显示"网络不给力哦，请检查你的网络设置"

## 问题根本原因分析

### 1. 画面比例问题

**原因：**
- 网易云音乐是从 .deb 包转换而来的应用（版本 1.2.1-9）
- 应用使用 Qt5 框架，但没有正确处理高分辨率显示器的 DPI 缩放
- 系统显示器为超宽屏（5879x1867 像素），DPI 为 96x96
- 启动脚本中缺少 Qt DPI 缩放相关的环境变量

### 2. 无法联网问题

**根本原因（多层次）：**

#### 第一层：缺失库文件
- 应用依赖 `libQt5WebChannel.so.5` 和 `libqcef.so.1`（Chromium Embedded Framework）
- 这些库文件虽然包含在应用的 `/opt/netease/netease-cloud-music/libs/` 目录中
- 但启动脚本的 `LD_LIBRARY_PATH` 设置不完整，导致应用无法找到这些库文件
- 直接运行二进制文件会报错：`error while loading shared libraries: libQt5WebChannel.so.5: cannot open shared object file`

#### 第二层：启动脚本问题
- 原始启动脚本 `/opt/netease/netease-cloud-music/netease-cloud-music.bash` 没有正确设置环境变量
- 需要通过 `/usr/bin/netease-cloud-music`（符号链接）来启动应用，而不是直接运行二进制文件

#### 第三层：硬件加速问题
- 应用启用了硬件加速（`hardware-acceleration=1`）
- 在某些系统上，硬件加速会导致 OpenGL 相关的错误
- 这可能影响应用的网络功能和页面加载

### 3. 个性推荐页面无法加载

**原因：**
- 个性推荐页面使用 CEF（Chromium Embedded Framework）渲染
- 硬件加速导致 GPU 渲染出现问题
- 可能与应用的缓存或配置有关

## 解决方案

### 步骤 1：修复画面比例问题

**修改启动脚本** `/opt/netease/netease-cloud-music/netease-cloud-music.bash`

添加以下环境变量：
```bash
export QT_AUTO_SCREEN_SCALE_FACTOR=1
export QT_SCALE_FACTOR=1.5
```

**说明：**
- `QT_AUTO_SCREEN_SCALE_FACTOR=1` 启用 Qt 自动 DPI 缩放
- `QT_SCALE_FACTOR=1.5` 设置 1.5 倍缩放（可根据需要调整为 1.2、1.3、2.0 等）

**结果：** ✓ 画面比例问题已解决

### 步骤 2：修复无法联网问题

**修改启动脚本** `/opt/netease/netease-cloud-music/netease-cloud-music.bash`

确保 `LD_LIBRARY_PATH` 正确包含应用的 libs 目录：
```bash
export LD_LIBRARY_PATH="${HERE}"/libs:${LD_LIBRARY_PATH}
```

**关键点：**
- 必须通过启动脚本 `/usr/bin/netease-cloud-music` 来运行应用
- 不要直接运行二进制文件 `/opt/netease/netease-cloud-music/netease-cloud-music`
- 启动脚本会正确设置所有必要的环境变量

**结果：** ✓ 应用能启动并连接到网易云音乐服务器

### 步骤 3：禁用硬件加速

**修改配置文件** `~/.config/netease-cloud-music/netease-cloud-music.ini`

```ini
[setting]
hardware-acceleration=0
```

**说明：**
- 禁用硬件加速可以避免 GPU 渲染相关的问题
- 虽然可能会影响性能，但能确保应用的稳定性

**结果：** ✓ 应用运行更稳定

### 步骤 4：网络配置

**修改配置文件** `~/.config/netease-cloud-music/netease-cloud-music.ini`

添加网络相关配置：
```ini
[ServiceNetwork]
proxy-type=0
proxy-host=
proxy-port=0
proxy-user=
proxy-password=

[ServiceHttpServer]
enable-http-server=0
```

**说明：**
- `proxy-type=0` 表示不使用代理
- 如果需要使用代理，可以修改这些设置

## 最终状态

| 问题 | 状态 | 解决方案 |
|------|------|--------|
| 画面比例不对 | ✓ 已解决 | 添加 Qt DPI 缩放环境变量 |
| 无法联网 | ✓ 已解决 | 修复启动脚本和库文件路径 |
| 个性推荐页面无法加载 | ⚠️ 部分解决 | 禁用硬件加速（仍有问题） |

## 应用启动方式

**正确的启动方式：**
```bash
/usr/bin/netease-cloud-music
```

或在应用菜单中直接启动。

**错误的启动方式（会导致库文件错误）：**
```bash
/opt/netease/netease-cloud-music/netease-cloud-music
```

## 系统信息

- **操作系统：** Arch Linux
- **应用版本：** netease-cloud-music 1.2.1-9
- **显示器：** 超宽屏 (5879x1867 像素)
- **DPI：** 96x96
- **依赖库：** gtk2, gtk3, vlc, taglib1, qt5-base, qt5-declarative, qt5-svg, qt5-tools, qt5-translations, qt5-wayland, qt5-x11extras

## 关键文件

- 启动脚本：`/opt/netease/netease-cloud-music/netease-cloud-music.bash`
- 配置文件：`~/.config/netease-cloud-music/netease-cloud-music.ini`
- 符号链接：`/usr/bin/netease-cloud-music` → `/opt/netease/netease-cloud-music/netease-cloud-music.bash`
- 应用库文件：`/opt/netease/netease-cloud-music/libs/`

## 已知限制

1. **个性推荐页面** - 仍然无法加载，可能是应用本身的问题或网易云音乐服务的问题
2. **硬件加速** - 禁用后可能影响应用性能
3. **其他功能** - 大部分功能正常，但某些特定功能可能仍有问题

## 参考资源

- 网易云音乐官网：https://music.163.com/
- AUR 包信息：netease-cloud-music 1.2.1-9
- Qt5 文档：https://doc.qt.io/qt-5/

---

**文档生成时间：** 2026-05-30
**诊断工具：** Claude Code
