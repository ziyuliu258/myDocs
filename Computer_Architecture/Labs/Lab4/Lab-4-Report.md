# 计算机体系结构实验四实验报告
>[!Note]
>仓库地址：[https://github.com/ziyuliu258/XJTU-Computer-Architecture-Lab4](https://github.com/ziyuliu258/XJTU-Computer-Architecture-Lab4)

## 一、实验名称

Cache 基本性能分析：Simulator A Web 版 N 路组相联 Cache 模拟器

## 二、实验目的

本实验围绕 Cache 基本性能分析进行设计与验证，目标是通过自行实现 Cache 模拟器，加深对 Cache 各关键参数对系统性能影响的理解。

具体目标如下：

1. 理解 Cache 容量、相联度、替换算法及块大小对缺失率的影响规律。
2. 掌握 N 路组相联 Cache 的地址分解方式，理解 tag、index、offset 三个字段的计算方法。
3. 实现 LRU 替换策略与写分配写回策略，理解其工作原理和工程实现。
4. 以 SPEC 基准程序（022.li、047.tomcatv、078.swm256、085.gcc）的内存地址流为输入，量化分析不同参数组合下的读缺失率、写缺失率与总缺失率。
5. 通过参数扫描对比，分析不同程序访问模式对 Cache 性能的决定性影响。

## 三、实验内容与要求

根据实验文档，本实验中自行设计的模拟器 A 需要满足以下功能要求：

1. 能够模拟 Cache 的执行过程，以课堂讲授为参考。
2. 支持图形交互或者命令交互。本实验同时实现了命令行（`cache_sim.py`）和 Web 图形界面两种方式。
3. 模拟器至少支持以下 4 个参数：`trace_input_file`、`cache_size`、`cache_associativity`、`cache_block_size`。
4. Cache 大小至少支持 8 KB、16 KB、32 KB、64 KB；块大小至少支持 16 B、32 B、64 B、128 B；相联度至少支持 1、2、4、8。
5. Cache 替换算法使用 LRU，写失效策略选择写分配。
6. 使用本次实验提供的 4 个 trace 文件（022.li.din、047.tomcatv.din、078.swm256.din、085.gcc.din）作为输入。
7. 仅考虑 load data（type=0）和 store data（type=1），忽略 fetch instruction（type=2）。

## 四、实验环境

- 操作系统：Linux
- Python：3.13 及以上
- 包管理工具：`uv`
- 前端运行环境：Node.js 18 及以上、`npm`
- 后端框架：FastAPI + Pydantic
- 前端框架：React + TypeScript + Vite
- 端口：后端 8767，前端开发服务器 5173

## 五、总体设计

本实验采用前后端分离架构。后端负责 Cache 模拟的核心逻辑与参数扫描，前端负责 trace 输入、参数配置、运行控制和可视化展示。

后端由 `sim_a/` 和 `server/` 两部分组成。`sim_a/` 实现 N 路组相联 Cache 模拟、LRU 替换、写分配策略和统计信息生成；`server/` 使用 FastAPI 提供 HTTP 接口，前端提交 trace 数据后，后端在返回单次模拟结果的同时，自动执行三维参数扫描（分别对 Cache 大小、相联度、块大小做对比），一次请求返回全部对比数据。

前端由 `frontend/` 实现，采用 React 组件化组织界面。用户可以粘贴 trace 文本、上传 `.din` 文件，或直接点击示例按钮加载内置的四个 SPEC trace 程序，调整 Cache 参数后点击"运行模拟"，即可在右侧看到统计结果，在中间看到三组纯 CSS 分组柱状图（分别对比 Cache 大小、相联度、块大小的影响）。

![](../../../attachments/Pasted%20image%2020260705212810.png)

## 六、Cache 模拟器设计

### 6.1 地址分解

给定块大小 $B$（字节）、Cache 总容量 $C$（字节）、相联度 $W$，32 位地址分三个字段：

```
| <---  tag  ---> | <-- index --> | <-- offset --> |
                    log2(S) 位      log2(B) 位
```

各字段位宽计算如下：

| 字段 | 公式 | 含义 |
|------|------|------|
| offset 位宽 | $b = \log_2 B$ | 块内字节偏移 |
| 组数 | $S = C \div (W \times B)$ | 总组数 |
| index 位宽 | $s = \log_2 S$ | 组索引 |
| tag 位宽 | $t = 32 - s - b$ | 区分同组不同块 |

示例：16 KB Cache，2-way，32 B block → $S=256$ 组，$b=5$ 位，$s=8$ 位，$t=19$ 位。

地址解码核心实现：

```python
set_index = (address >> offset_bits) & (num_sets - 1)
tag       = address >> (offset_bits + index_bits)
```

### 6.2 LRU 替换策略

每组使用 Python 标准库 `collections.OrderedDict` 实现 O(1) 的 LRU：

- 字典**末尾** = MRU（最近使用），字典**首部** = LRU（最久未使用）
- 命中时：`pop(tag)` 后重新插入末尾，更新为 MRU
- 缺失且满时：`popitem(last=False)` 驱逐首部 LRU 块

```python
def access(self, tag, is_write):
    if tag in self._lines:
        dirty = self._lines.pop(tag)
        self._lines[tag] = dirty or is_write  # 移到 MRU
        return True, False   # hit
    evicted = len(self._lines) >= self.ways
    if evicted:
        self._lines.popitem(last=False)        # 驱逐 LRU
    self._lines[tag] = is_write
    return False, evicted                      # miss
```

### 6.3 写分配策略（Write-Allocate + Write-Back）

- **写命中**：直接更新 Cache 中的块，置脏位 `dirty=True`
- **写缺失**：先将块从内存装入 Cache（写分配），再执行写操作，置脏位
- **块被驱逐时**：若 `dirty=True`，需写回内存（由 `evictions` 计数器记录）

### 6.4 参数扫描

单次 `/api/simulate` 请求除返回指定配置的统计结果外，还自动执行以下三组扫描：

| 扫描维度 | 固定参数 | 变化参数 |
|----------|----------|----------|
| Cache 大小 | 2-way，32 B 块 | 8 / 16 / 32 / 64 KB |
| 相联度 | 16 KB，32 B 块 | 1 / 2 / 4 / 8 路 |
| 块大小 | 16 KB，2-way | 16 / 32 / 64 / 128 B |

## 七、后端设计与实现

### 7.1 API 接口

后端使用 FastAPI 提供两个接口：

| 接口 | 方法 | 功能 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/samples` | GET | 返回 4 个内置 trace 文件内容 |
| `/api/simulate` | POST | 执行模拟并返回统计结果与三维扫描数据 |

`/api/simulate` 请求体包含 `trace_data`（trace 文本）、`config`（Cache 配置）和 `run_sweep`（是否执行参数扫描）。响应体包含 `stats`（单次统计）、`sweep_by_size`、`sweep_by_assoc`、`sweep_by_block` 三组扫描结果。

### 7.2 Pydantic 数据模型

```python
class CacheConfig(BaseModel):
    cache_size: int = 16384    # 字节
    associativity: int = 2
    block_size: int = 32

class SimulateResponse(BaseModel):
    stats: CacheStats
    sweep_by_size: list[SweepPoint]
    sweep_by_assoc: list[SweepPoint]
    sweep_by_block: list[SweepPoint]
```

### 7.3 性能统计

后端返回以下统计指标：

- 读访问次数与读缺失次数、读缺失率
- 写访问次数与写缺失次数、写缺失率
- 总访问次数、总缺失次数、总缺失率
- 驱逐次数（块替换次数）

## 八、前端设计与实现

### 8.1 页面布局

前端页面采用三栏工作台布局，顶部有统计摘要 hero bar：

1. **左侧**：trace 输入区（粘贴/上传/示例按钮）+ Cache 参数选择 + 运行控制。
2. **中间**：缺失率分析图表，含三个标签页（Cache 大小、相联度、块大小效果）。
3. **右侧**：统计详情面板（stat chips 网格 + 读/写明细表）。

顶部 hero bar 实时显示总访问次数、总缺失率和驱逐次数三项关键指标。

![](../../../attachments/Pasted%20image%2020260705212914.png)

### 8.2 参数配置

ConfigPanel 提供四个下拉选择框：

- Cache 大小：8 KB / 16 KB / 32 KB / 64 KB
- 相联度：1-way / 2-way / 4-way / 8-way
- 块大小：16 B / 32 B / 64 B / 128 B
- 替换策略：LRU（固定，不可更改）

### 8.3 缺失率图表

图表模块（`MissRateChart`）使用纯 CSS 实现分组柱状图，无需引入外部图表库，与 lab2/lab3 技术栈保持一致。每组数据展示读缺失率、写缺失率、总缺失率三条柱，柱宽按当前组最大值归一化。

三个标签页（Cache 大小 / 相联度 / 块大小）点击切换，对应三组参数扫描结果。

![](../../../attachments/Pasted%20image%2020260705212949.png)

![](../../../attachments/Pasted%20image%2020260705213220.png)
![](../../../attachments/Pasted%20image%2020260705213243.png)

### 8.4 示例程序加载

页面启动时自动请求 `/api/samples`，将 4 个 SPEC trace 程序名显示为快速加载按钮。点击后 trace 文本直接填入输入框，无需手动上传文件。

![](../../../attachments/Pasted%20image%2020260705213256.png)
## 九、实验过程

### 9.1 环境配置

在项目根目录使用 `uv` 创建 Python 虚拟环境并安装后端依赖：

```bash
uv sync
```

进入前端目录安装 Node.js 依赖：

```bash
cd frontend && npm install
```

### 9.2 启动系统

后端启动命令：

```bash
uv run uvicorn server.app:app --host 127.0.0.1 --port 8767 --reload
```

前端启动命令：

```bash
cd frontend && npm run dev
```

启动后在浏览器访问 http://localhost:5173。

### 9.3 运行模拟

1. 点击 trace 输入面板中的示例按钮（或上传 `.din` 文件），加载 trace 数据。
2. 在 ConfigPanel 中选择 Cache 参数（大小、相联度、块大小）。
3. 点击"运行模拟"，等待后端完成单次模拟与三维参数扫描。
4. 在中间图表区切换三个标签页，观察不同参数维度对缺失率的影响。
5. 在右侧统计面板查看读/写缺失率、驱逐次数等详细数据。

![](../../../attachments/Pasted%20image%2020260705212659.png)
![](../../../attachments/Pasted%20image%2020260705212712.png)
![](../../../attachments/Pasted%20image%2020260705212729.png)
## 十、测试结果与分析

### 10.1 Cache 大小对缺失率的影响

**固定参数：2-way，块大小 32 B**

| Trace | 8 KB | 16 KB | 32 KB | 64 KB |
|-------|------|-------|-------|-------|
| 022.li.din | 2.43% | 1.43% | 0.93% | 0.76% |
| 047.tomcatv.din | 5.91% | 4.51% | 4.41% | 4.40% |
| 078.swm256.din | 0.56% | 0.54% | 0.54% | 0.54% |
| 085.gcc.din | 3.27% | 1.88% | 1.57% | 1.45% |

整体趋势：Cache 越大缺失率越低，但收益递减显著。022.li 从 8→16 KB 时降幅最大（2.43%→1.43%），此后改善幅度逐渐收窄。078.swm256 在 16 KB 时已接近饱和，扩大 Cache 几乎无收益，说明其工作集很小。047.tomcatv 的总缺失率受写缺失主导，Cache 大小对写缺失改善极为有限。

![](../../../attachments/Pasted%20image%2020260705213605.png)

### 10.2 相联度对缺失率的影响

**固定参数：Cache 16 KB，块大小 32 B**

| Trace | 1-way | 2-way | 4-way | 8-way |
|-------|-------|-------|-------|-------|
| 022.li.din | 2.51% | 1.43% | 1.28% | 1.25% |
| 047.tomcatv.din | 5.34% | 4.51% | 4.41% | 4.41% |
| 078.swm256.din | 0.64% | 0.54% | 0.54% | 0.54% |
| 085.gcc.din | 3.18% | 1.88% | 1.71% | 1.67% |

从直接映射（1-way）提升至 2-way 时改善最为显著：022.li 降低 43%，085.gcc 降低 41%。4-way 之后收益迅速递减，8-way 相对 4-way 几乎无差别。078.swm256 和 047.tomcatv 在 2-way 时已趋于饱和。

![](../../../attachments/Pasted%20image%2020260705213833.png)

### 10.3 块大小对缺失率的影响

**固定参数：Cache 16 KB，2-way**

| Trace | 16 B | 32 B | 64 B | 128 B |
|-------|------|------|------|-------|
| 022.li.din | 2.40% | 1.43% | 0.94% | 0.67% |
| 047.tomcatv.din | 8.72% | 4.51% | 2.38% | 1.32% |
| 078.swm256.din | 1.05% | 0.54% | 0.28% | 0.15% |
| 085.gcc.din | 2.97% | 1.88% | 1.52% | 1.83% |

047.tomcatv 受益最大（16→128 B 时降幅 85%），因为矩阵转置的写操作有顺序性，大块可大幅预取相邻写地址。085.gcc 在 128 B 时缺失率反升（64 B 为最优），因为块过大导致组数减少（64 组），冲突缺失增加且无效预取污染 Cache。

![](../../../attachments/Pasted%20image%2020260705214057.png)

### 10.4 右侧统计面板

![](../../../attachments/Pasted%20image%2020260705214109.png)

## 十一、实验中遇到的问题与解决方法

### 11.1 参数扫描超时

初始方案在前端循环发送多次 `/api/simulate` 请求（每个参数组合一次），导致 4 traces × 4 大小 × 4 相联度 × 4 块大小 = 256 次 HTTP 请求，响应时间不可接受。

解决方法是将三维扫描逻辑移至后端：单次 `/api/simulate` 请求内，后端连续执行12次（4+4+4）额外扫描并一次性返回全部数据，消除了网络往返开销。对于 trace 数据量最大的程序，一次完整请求在本地约需 2 秒。

### 11.2 纯 CSS 柱状图的宽度归一化

初始实现将柱宽直接用百分比映射到缺失率绝对值，导致当某个程序整体缺失率极低时（如 078.swm256），所有柱都极短，视觉上几乎看不出差异。

解决方法是对每组图表内部做归一化：以当前可见组内最大 `total_miss_rate` 为基准，其余各柱按比例缩放，使图表在不同量级下都能清晰展示相对大小关系。

## 十二、测试与验证

后端快速验证：

```bash
uv run python cache_sim.py data/022.li.din -s 16384 -a 2 -b 32
```

前端构建检查：

```bash
cd frontend && npm run build
```

API 接口验证：

```bash
uv run uvicorn server.app:app --host 127.0.0.1 --port 8767
curl http://127.0.0.1:8767/api/health
curl http://127.0.0.1:8767/api/samples | python3 -m json.tool | head -10
```

验证内容包括：

- `CacheSimulator` 地址分解逻辑（不同块大小/组数下 tag/index 计算）
- LRU 驱逐顺序（命中后移到 MRU，缺失时驱逐 LRU）
- 写分配缺失计数（写缺失时 `write_misses` 和 `evictions` 同步递增）
- `/api/simulate` 返回的三维扫描数据格式
- 前端 TypeScript 类型检查（`npm run build` 零错误）

## 十三、实验结果分析

通过对四个 SPEC 基准程序、四种 Cache 大小、四种相联度、四种块大小的系统测试，得出以下结论：

**Cache 大小**：越大缺失率越低，但存在明显的边际递减。8→16 KB 的改善远大于 32→64 KB。当 Cache 大于程序工作集时，继续扩大收益趋近于零。

**相联度**：1-way → 2-way 的提升是"性价比"最高的优化，能消除大量冲突缺失。4-way 以上收益迅速递减。综合硬件代价与性能，4-way 是现代 L1 Cache 的典型选择。

**块大小**：对顺序/流式访问程序（047.tomcatv、078.swm256）效果显著，大块充分利用空间局部性。对随机访问程序（085.gcc）存在最优值，过大的块会减少组数、增加冲突并引入无效预取，导致性能反降。

**程序访问模式**是决定 Cache 效果的根本因素：047.tomcatv 的读/写缺失率相差 130 倍（矩阵转置跨步写），078.swm256 读缺失率仅 0.02%（极强时间局部性），085.gcc 对各维度参数均较敏感（复杂指针访问）。没有一组参数对所有程序都最优，Cache 设计本质上是三类缺失（容量、冲突、冷启动）之间的折中权衡。

## 十四、实验总结

本实验完成了 Cache Simulator A 的设计与实现。模拟器支持 N 路组相联 Cache 的完整执行过程，能够通过 Web 页面展示统计数据和三维参数对比图表，并支持 trace 文本粘贴、文件上传和示例程序一键加载。

在实现过程中，最有价值的设计决策有两个：一是将 LRU 的数据结构选为 `OrderedDict`，以 O(1) 操作实现高效替换；二是将三维参数扫描移至后端一次性完成，避免了前端多轮请求的延迟问题。

通过对四个 SPEC 程序的量化分析，原本教科书上抽象的"Cache 越大越好"变成了具体的数字规律——078.swm256 在 16 KB 时已饱和，047.tomcatv 的写缺失对 Cache 大小几乎免疫，085.gcc 在 128 B 大块时缺失率反而升高。这种"通过数据说话"的分析方式，正是计算机体系结构研究的核心方法论。
