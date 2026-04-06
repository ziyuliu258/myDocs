## 环境

### 系统环境

```bash
cat /etc/os-release
NAME="EndeavourOS"
PRETTY_NAME="EndeavourOS"
ID="endeavouros"
ID_LIKE="arch"
BUILD_ID=rolling
ANSI_COLOR="38;2;23;147;209"
HOME_URL="https://endeavouros.com"
DOCUMENTATION_URL="https://discovery.endeavouros.com"
SUPPORT_URL="https://forum.endeavouros.com"
BUG_REPORT_URL="https://forum.endeavouros.com/c/general-system/endeavouros-installation"
PRIVACY_POLICY_URL="https://endeavouros.com/privacy-policy-2"
LOGO="endeavouros"
```

```bash
uname -mr
6.19.9-arch1-1 x86_64
```

### 构建工具

```bash
pacman --version | head -n1
makepkg --version | head -n1
yay --version
gcc --version | head -n1
cmake --version | head -n1

makepkg (pacman) 7.1.0
yay v12.5.7 - libalpm v16.0.1
gcc (GCC) 15.2.1 20260209
cmake version 4.3.1

```

## 问题

### 问题一

如果直接按照官网的教程安装各种依赖，然后再从官方Github上拉取代码，很麻烦，而且在安到`python2-ipaddress`这一个依赖包时，会开始手动编译`python2`，速度奇慢。这应该是因为`python2`太古老了，最新的`pacman`/`aur`库都把直接的二进制包移除了，只能手动编译，就像在Intel芯片的MacOS上用`brew`感受一样糟糕。

### 问题二

如果放弃这个依赖关系，直接用`aur`源安装`frr`（因为`pacman`并没有直装的包），就会出现类似以下的报错。

```bash
yay -S frr                                   
AUR Explicit (1): frr-10.6.0-1
AUR Dependency (1): rtrlib-0.8.0-2
Sync Make Dependency (1): python-sphinx-9.1.0-1
:: (1/2) 下载了 PKGBUILD: rtrlib
:: (2/2) 下载了 PKGBUILD: frr
  2 frr                              (构建文件已存在)
  1 rtrlib                           (构建文件已存在)
==> 清理哪些包的构建文件？
==> [N]没有 [A]全部 [Ab]中止 [I]已安装 [No]未安装 或 (1 2 3, 1-3, ^4)
==> 
  2 frr                              (构建文件已存在)
  1 rtrlib                           (构建文件已存在)
==> 显示哪些包的差异？
==> [N]没有 [A]全部 [Ab]中止 [I]已安装 [No]未安装 或 (1 2 3, 1-3, ^4)
==> 
==> 正在创建软件包：frr 10.6.0-1 (2026年03月29日 星期日 01时47分05秒)
==> 获取源代码...
  -> 正在下载 frr-10.6.0.tar.gz...
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
100 11.43M   0 11.43M   0      0  3.01M      0           00:03          1.50M
  -> 正在下载 frr-tmpfiles.conf...
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
100     56 100     56   0      0     59      0                              0
  -> 正在下载 frr-sysusers.conf...
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
100    185 100    185   0      0    217      0                              0
==> 警告： 正在跳过源文件 PGP 签名校验。
==> 正在验证 source 文件，使用sha256sums...
    frr-10.6.0.tar.gz ... 通过
    frr-tmpfiles.conf ... 通过
    frr-sysusers.conf ... 通过
==> 错误： arch 不能包含重复值
 -> 下载源文件时出错: /home/ziyu/.cache/yay/rtrlib 
    context: 下载源文件时出错: /home/ziyu/.cache/yay/rtrlib 
    context: exit status 12 
    
 
    

:: 安装后删除构建依赖？ [y/N] y
:: (1/2) 正在解析 SRCINFO: frr
:: (2/2) 正在解析 SRCINFO: rtrlib
正在解析依赖关系...
正在查找软件包冲突...

软件包 (12)                                 新版本     净变化     下载大小

extra/python-babel                          2.17.0-3   30.53 MiB  6.50 MiB
extra/python-imagesize                      1.4.1-7     0.05 MiB  0.01 MiB
extra/python-roman-numerals-py              3.1.0-2     0.04 MiB  0.01 MiB
extra/python-snowballstemmer                3.0.0.1-2   2.91 MiB  0.24 MiB
extra/python-sphinx-alabaster-theme         1.0.0-6     0.05 MiB  0.02 MiB
extra/python-sphinxcontrib-applehelp        2.0.0-5     0.26 MiB  0.03 MiB
extra/python-sphinxcontrib-devhelp          2.0.0-6     0.13 MiB  0.02 MiB
extra/python-sphinxcontrib-htmlhelp         2.1.0-5     0.18 MiB  0.04 MiB
extra/python-sphinxcontrib-jsmath           1.0.1-21    0.02 MiB  0.01 MiB
extra/python-sphinxcontrib-qthelp           2.0.0-5     0.17 MiB  0.03 MiB
extra/python-sphinxcontrib-serializinghtml  2.0.0-5     0.14 MiB  0.03 MiB
extra/python-sphinx                         9.1.0-1    23.72 MiB  2.97 MiB

下载大小：       9.92 MiB
全部安装大小：  58.21 MiB

:: 进行安装吗？ [Y/n] y
:: 正在获取软件包......
 python-sphinxcontrib-htmlhelp-2.1.0-5-any                                                 38.0 KiB   134 KiB/s 00:00 [-----------------------------------------------------------------------] 100%
 python-sphinxcontrib-applehelp-2.0.0-5-any                                                32.6 KiB   112 KiB/s 00:00 [-----------------------------------------------------------------------] 100%
 python-snowballstemmer-3.0.0.1-2-any                                                     241.9 KiB   518 KiB/s 00:00 [-----------------------------------------------------------------------] 100%
 python-sphinxcontrib-serializinghtml-2.0.0-5-any                                          30.8 KiB  63.2 KiB/s 00:00 [-----------------------------------------------------------------------] 100%
 python-sphinx-9.1.0-1-any                                                                  3.0 MiB  2.52 MiB/s 00:01 [-----------------------------------------------------------------------] 100%
 python-sphinxcontrib-qthelp-2.0.0-5-any                                                   30.5 KiB  37.8 KiB/s 00:01 [-----------------------------------------------------------------------] 100%
 python-sphinxcontrib-devhelp-2.0.0-6-any                                                  24.9 KiB  30.6 KiB/s 00:01 [-----------------------------------------------------------------------] 100%
 python-babel-2.17.0-3-any                                                                  6.5 MiB  4.28 MiB/s 00:02 [-----------------------------------------------------------------------] 100%
 python-sphinx-alabaster-theme-1.0.0-6-any                                                 16.7 KiB  85.4 KiB/s 00:00 [-----------------------------------------------------------------------] 100%
 python-imagesize-1.4.1-7-any                                                              14.0 KiB  61.8 KiB/s 00:00 [-----------------------------------------------------------------------] 100%
 python-roman-numerals-py-3.1.0-2-any                                                      13.6 KiB   127 KiB/s 00:00 [-----------------------------------------------------------------------] 100%
 python-sphinxcontrib-jsmath-1.0.1-21-any                                                   9.5 KiB  86.7 KiB/s 00:00 [-----------------------------------------------------------------------] 100%
 全部 (12/12)                                                                               9.9 MiB  4.81 MiB/s 00:02 [-----------------------------------------------------------------------] 100%
(12/12) 正在检查密钥环里的密钥                                                                                        [-----------------------------------------------------------------------] 100%
(12/12) 正在检查软件包完整性                                                                                          [-----------------------------------------------------------------------] 100%
(12/12) 正在加载软件包文件                                                                                            [-----------------------------------------------------------------------] 100%
(12/12) 正在检查文件冲突                                                                                              [-----------------------------------------------------------------------] 100%
:: 正在处理软件包的变化...
( 1/12) 正在安装 python-babel                                                                                         [-----------------------------------------------------------------------] 100%
( 2/12) 正在安装 python-imagesize                                                                                     [-----------------------------------------------------------------------] 100%
( 3/12) 正在安装 python-roman-numerals-py                                                                             [-----------------------------------------------------------------------] 100%
( 4/12) 正在安装 python-snowballstemmer                                                                               [-----------------------------------------------------------------------] 100%
python-snowballstemmer 的可选依赖
    python-pystemmer: for improved performance
( 5/12) 正在安装 python-sphinx-alabaster-theme                                                                        [-----------------------------------------------------------------------] 100%
( 6/12) 正在安装 python-sphinxcontrib-applehelp                                                                       [-----------------------------------------------------------------------] 100%
( 7/12) 正在安装 python-sphinxcontrib-devhelp                                                                         [-----------------------------------------------------------------------] 100%
( 8/12) 正在安装 python-sphinxcontrib-htmlhelp                                                                        [-----------------------------------------------------------------------] 100%
( 9/12) 正在安装 python-sphinxcontrib-jsmath                                                                          [-----------------------------------------------------------------------] 100%
(10/12) 正在安装 python-sphinxcontrib-qthelp                                                                          [-----------------------------------------------------------------------] 100%
(11/12) 正在安装 python-sphinxcontrib-serializinghtml                                                                 [-----------------------------------------------------------------------] 100%
(12/12) 正在安装 python-sphinx                                                                                        [-----------------------------------------------------------------------] 100%
python-sphinx 的可选依赖
    imagemagick: for ext.imgconverter [已安装]
    texlive-fontsextra: for the default admonition title icons in PDF output [已安装]
    texlive-latexextra: for generation of PDF documentation [已安装]
:: 正在运行事务后钩子函数...
(1/1) Arming ConditionNeedsUpdate...
==> 错误： arch 不能包含重复值
 -> 层级安装失败，正在合并到下一个层级。error:生成时出错: rtrlib - exit status 12
警告：python-sphinx-9.1.0-1 已经为最新 -- 重新安装
正在解析依赖关系...
正在查找软件包冲突...

软件包 (1)           旧版本   新版本   净变化  

extra/python-sphinx  9.1.0-1  9.1.0-1  0.00 MiB

全部安装大小：  23.72 MiB
净更新大小：     0.00 MiB

:: 进行安装吗？ [Y/n] y
(1/1) 正在检查密钥环里的密钥                                                                                          [-----------------------------------------------------------------------] 100%
(1/1) 正在检查软件包完整性                                                                                            [-----------------------------------------------------------------------] 100%
(1/1) 正在加载软件包文件                                                                                              [-----------------------------------------------------------------------] 100%
(1/1) 正在检查文件冲突                                                                                                [-----------------------------------------------------------------------] 100%
:: 正在处理软件包的变化...
(1/1) 正在重新安装 python-sphinx                                                                                      [-----------------------------------------------------------------------] 100%
:: 正在运行事务后钩子函数...
(1/2) Arming ConditionNeedsUpdate...
(2/2) Checking which packages need to be rebuilt
==> 错误： arch 不能包含重复值
 -> 生成时出错: rtrlib-exit status 12
==> 正在创建软件包：frr 10.6.0-1 (2026年03月29日 星期日 01时48分53秒)
==> 正在检查运行时依赖关系...
==> 缺失依赖关系：
  -> rtrlib
==> 错误： 无法解决所有的依赖关系。
 -> 生成时出错: frr-exit status 8
正在检查依赖关系...
:: python-jinja可选依赖于python-babel: for i18n support

软件包 (12)                           旧版本     净变化    

python-babel                          2.17.0-3   -30.53 MiB
python-imagesize                      1.4.1-7     -0.05 MiB
python-roman-numerals-py              3.1.0-2     -0.04 MiB
python-snowballstemmer                3.0.0.1-2   -2.91 MiB
python-sphinx-alabaster-theme         1.0.0-6     -0.05 MiB
python-sphinxcontrib-applehelp        2.0.0-5     -0.26 MiB
python-sphinxcontrib-devhelp          2.0.0-6     -0.13 MiB
python-sphinxcontrib-htmlhelp         2.1.0-5     -0.18 MiB
python-sphinxcontrib-jsmath           1.0.1-21    -0.02 MiB
python-sphinxcontrib-qthelp           2.0.0-5     -0.17 MiB
python-sphinxcontrib-serializinghtml  2.0.0-5     -0.14 MiB
python-sphinx                         9.1.0-1    -23.72 MiB

全部移去体积：  58.21 MiB

:: 打算删除这些软件包吗？ [Y/n] 
:: 正在处理软件包的变化...
( 1/12) 正在删除 python-sphinx                                                                                        [-----------------------------------------------------------------------] 100%
( 2/12) 正在删除 python-sphinxcontrib-serializinghtml                                                                 [-----------------------------------------------------------------------] 100%
( 3/12) 正在删除 python-sphinxcontrib-qthelp                                                                          [-----------------------------------------------------------------------] 100%
( 4/12) 正在删除 python-sphinxcontrib-jsmath                                                                          [-----------------------------------------------------------------------] 100%
( 5/12) 正在删除 python-sphinxcontrib-htmlhelp                                                                        [-----------------------------------------------------------------------] 100%
( 6/12) 正在删除 python-sphinxcontrib-devhelp                                                                         [-----------------------------------------------------------------------] 100%
( 7/12) 正在删除 python-sphinxcontrib-applehelp                                                                       [-----------------------------------------------------------------------] 100%
( 8/12) 正在删除 python-sphinx-alabaster-theme                                                                        [-----------------------------------------------------------------------] 100%
( 9/12) 正在删除 python-snowballstemmer                                                                               [-----------------------------------------------------------------------] 100%
(10/12) 正在删除 python-roman-numerals-py                                                                             [-----------------------------------------------------------------------] 100%
(11/12) 正在删除 python-imagesize                                                                                     [-----------------------------------------------------------------------] 100%
(12/12) 正在删除 python-babel                                                                                         [-----------------------------------------------------------------------] 100%
:: 正在运行事务后钩子函数...
(1/1) Arming ConditionNeedsUpdate...
 -> 无法安装以下软件包, 需要手动介入处理:
rtrlib - exit status 12
frr - exit status 8
```

这是因为`frr`需要依赖包`rtrlib`，而`aur`的`rtrlib`的打包的构建信息有问题，在其`aur`仓库[页面](https://aur.archlinux.org/packages/rtrlib)上也有人反映过。

## 解决

### 完整执行步骤

先把包下载到本地，先不安装到系统中。

```bash
yay -G rtrlib # 随便找个目录
cd rtrlib
```

然后修改打包构建信息

```bash
vim PKGBUILD # 自选编辑器，或者用nano，vscode，nvim之类的
```

搜索其中`arch=(x86_64 i686 aarch64 armv7h armv7h)`这一行，会发现最后的`armv7h`架构标签重复了，这就是为什么上面会有提示“arch不能包含重复值”。去掉其中重复的一个`armv7h`；然后是要在`prepare()`中指定`CMAKE`的版本，也就是如下这么添加：

```bash
prepare() {
    cd ${srcdir}/${pkgname}-${pkgver}
    cmake \
        -DCMAKE_C_FLAGS:STRING="${CFLAGS}" \
        -DCMAKE_CXX_FLAGS:STRING="${CXXFLAGS}" \
        -DCMAKE_EXE_LINKER_FLAGS:STRING="${LDFLAGS}" \
        -DCMAKE_SHARED_LINKER_FLAGS:STRING="${LDFLAGS}" \
        -DCMAKE_INSTALL_PREFIX=/usr \
        -DCMAKE_INSTALL_LIBDIR:STRING=lib \
        -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \ # 添加这一行
        .
}
```

最后保存退出。随后手动安装

```bash
makepkg -si
```

`rtrlib`安装成功后，就可以删掉这个临时的`rtrlib`目录，然后继续执行`yay -S frr`。这个时候应该就可以成功了。
