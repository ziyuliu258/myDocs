# 第 3 部分：附录 A–E

> 说明：引用编号、模型名、API、文件名、代码标识符和数值均按原文保留。参考文献表保留原文。

## A　补充统计

### A.1　Articraft-10K 数据集

图 11a 展示了 Articraft-10K 中物体在 15 个大类中的分布。图 11b 将每个类别的平均生成成本与 Articraft agent 所需的平均轮数对应绘制，显示两者呈正相关。图 12 给出由全部物体名称的词频生成的词云；字体越大表示出现频率越高。图 13 展示数据集中所有物体的生成成本、轮数及连杆（部件）数量的分布。图 14 汇总数据集的网格统计，包括每个物体的顶点、三角形和边数分布。最后，图 15 按关节类型给出 Articraft-10K 物体中 URDF 关节数的分布。

### A.2　人工评分后的保留率

我们将策展保留率定义为：最终人工评分至少为 4 分的已生成资产所占比例。表 4 按生成所用模型列出了保留统计。

**表 4：按后端统计的人工策展保留率。保留资产指评分为 4 或 5 的资产。**

| 后端 | 已生成 | 已保留 | 保留率 |
|---|---:|---:|---:|
| GPT-5.4 | 6,601 | 5,903 | 89.4% |
| GPT-5.5 | 4,010 | 3,828 | 95.5% |
| GPT-5.4/GPT-5.5 合计 | 10,611 | 9,731 | 91.7% |
| Gemini 3.1 Pro | 298 | 287 | 96.3% |

### A.3　Articraft 生成的计算需求

Articraft 的计算需求较低，因为生成过程既不训练模型，也不需要渲染后的视觉反馈。高成本的推理由外部 LLM API 后端提供；本地 harness 则在 CPU worker 上运行 `model.py`、CAD 与网格构建、URDF 导出、编写的测试以及质量控制检查。我们为这些本地步骤使用了异构 CPU worker；Articraft 的生成、数据集实例化以及编译/QC 循环均不需要 GPU。

每个物体都是独立生成的，因此可通过将记录分配给不同 CPU worker 来并行构建数据集。worker 的内存消耗主要由单个物体的临时 CadQuery 和网格处理状态决定。因此，一个批次的实际耗时主要取决于 LLM 提供商延迟、agent 轮数和所选的并行 worker 数量，而不是本地加速器算力。

我们为每条记录保存提供商、模型、轮数、API 成本、生成的程序、编译输出和策展者评分。图 11b 和图 13 汇总了 Articraft-10K 中每个物体的生成成本和轮数。对于保留物体、过滤物体和探索性运行，我们使用同一套轻量的纯 CPU 本地管线；表 4 同时报告了构建数据集所用主生成运行的已生成数与已保留数。Isaac Sim 和 VR 等下游演示会使用各自的模拟器或显示硬件，但复现 Articraft 核心生成管线并不需要它们。

### A.4　API 成本与 token 用量

表 5 汇总了构建 Articraft-10K 时，Articraft harness 为主要 LLM 后端记录的 API 使用量。成本依据生成期间有效的提供商定价计算；若提供商提供提示词缓存折扣，也已计入。成本分析涵盖全部保留物体和大多数被过滤的生成尝试：表 4 的 10,909 次尝试中，有 10,880 次具有成本日志。

在这些具有成本日志的尝试中，API 总成本约为 \$12.39K，平均每次生成尝试 \$1.14。保留的 Articraft-10K 物体对应约 \$11.33K，即平均每个保留物体 \$1.13。提示词缓存对可扩展性非常重要：主要后端成本日志中 85.7% 的提示词 token 来自缓存。

> **图 10：（a）放下的吊桥。（b）抬起的吊桥。**  
> Articraft SDK 表达能力和风格可控性的示例。同一个积木风格门楼在两种吊桥状态下被渲染，表明生成资产同时控制了构造风格与关节运动。

**表 5：主要生成后端的 API 成本和轮数统计。成本单位为美元，依据可用的逐记录成本日志计算。**

| 后端 | 成本日志数 | 已保留 | 总成本 | 平均值/中位数成本 | 平均值/中位数轮数 |
|---|---:|---:|---:|---:|---:|
| GPT-5.4 | 6,572 | 5,903 | \$6,693.89 | \$1.019 / \$0.887 | 16.9 / 15 |
| GPT-5.5 | 4,010 | 3,828 | \$5,305.18 | \$1.323 / \$1.240 | 16.4 / 15 |
| Gemini 3.1 Pro | 298 | 287 | \$387.91 | \$1.302 / \$0.711 | 19.5 / 10 |
| 合计 | 10,880 | 10,018 | \$12,386.99 | \$1.139 / \$1.030 | 16.8 / 15 |

---

## B　补充结果

### B.1　Articraft-10K 中生成的可动物体资产补充示例

图 19 给出了 Articraft 为 Articraft-10K 生成资产的更多示例。这些示例展示了数据集覆盖的广泛物体类别和尺度：既有注射器、瓶子等小型手持物体，也有缝纫箱、台式 PC 主机、斜切锯和炉灶等家庭与工坊物体，以及吊桥、路障、风车和灯塔信标等大型结构。

它们还展示了多种关节类型，包括带铰链的门与盖、滑动面板、折叠连杆、旋转轮子、齿轮、信标和类似螺旋桨的组件、伸缩或移动副运动，以及摆动机构。对于每条提示词，我们展示渲染的资产状态及其彩色部件可视化，以强调生成物体包含显式的语义部件和关节结构，而不只是静态几何。

**SDK 的表达能力。**Articraft SDK 不局限于单一视觉风格或单一物体族；提示词可同时指定机构和构造风格。图 10 的积木风格门楼说明，其风格、部件和吊桥运动均可被显式控制。

### B.2　图像条件生成的补充细节

**物体级重建。**Articraft 中的图像条件化有两个目标：使几何形状锚定于参考照片，并恢复 PBR 材质，使结果在视觉上逼真。

**几何条件化。**当用户将参考图像与提示词一同提供时，harness 会将图像附在 agent 的首个用户回合中；系统提示词则将它提升为首要真值来源。由于图像会持续保留在多轮上下文中，每一次“编译—探测—编辑”循环都会重新以同一视觉证据为依据，使局部编辑保持与照片一致，而不会漂移到类别先验。agent 输出带有平坦 PBR 材质的 URDF，其中基础颜色根据输入图像近似估计。

**材质绘制。**我们采用 LiteReality [14] 的检索式策略和仅反照率（albedo-only）优化；PBR 贴图来自经 [48] 筛选得到的人工整理材质数据库，而非从零合成。检索采用分层方式：agent 首先利用语言线索 [8]，通过三层材质类别缩小候选池；然后利用 DINOv2 [42] 的视觉特征对候选短名单排序；最后由 LLM 作出选择。

随后，我们采用 LiteReality 的仅反照率优化：将基础颜色的 HSV 质心向目标颜色移动，同时保留局部偏差，以保持所选材质的纹理颗粒与风化细节。由于颜色主导感知上的匹配质量，我们还加入颜色细化循环：重新渲染物体、将其与参考图比较，并持续调整直到颜色正确。两阶段结合后，如图 16 所示，Articraft 能把任意图像转化为具有忠实几何、有效关节和完整 PBR 材质的可动物体资产。

**场景级重建。**我们将 Articraft 接入 LiteReality [14] 管线，以扩展至整间房间的重建。该管线使用通过 Apple RoomPlan 捕获的 RGB-D 扫描，其中包含逐物体的包围盒、朝向与尺度；它通过物体重建、材质绘制和场景整合三个阶段，将扫描转化为可供图形使用的场景。LiteReality 原本的物体阶段依赖从人工整理的 CAD 数据库中检索；我们以 Articraft 替换它，使物体以可动结构生成，而非作为刚性网格被检索，并把材质绘制阶段直接纳入 Articraft 的图像条件化管线。

由于 Articraft 在高度不规则或非常规设计的物体上可能表现欠佳，我们加入了简单的逐物体开关：被标记为可动的物体用 Articraft 生成，其余物体回退到 LiteReality 的检索路径。给定 RGB-D 捕获，管线首先为每个检测到的物体裁剪最可见的参考图，然后按上述方式路由每个裁剪图。Articraft 的输出会重新合并到 LiteReality 的解析场景布局整合阶段，得到既与捕获图像紧密匹配、又完全可动并可用于模拟和后续交互任务的房间，如图 17 所示。

> **图 11：Articraft-10K 的统计。**  
> （a）每个大类中的物体数量。（b）每个物体类别的平均成本和平均轮数，颜色表示所属大类。  
> 图中 15 个大类为：家用电器、家具与收纳、电子与光学、车辆与移动、运动链、工具与工坊、门/闸/出入口、机器人臂与机械手、基础关节与模块、建筑与基础设施、线性台与龙门架、安装与定位、户外与休闲、军事与防御、商用投币与自动售货设备。

> **图 12：Articraft-10K 中物体名称的词云。**

> **图 13：Articraft-10K 中每个物体的成本、轮数和连杆数分布。**  
> 图中均值分别为：总成本 \$1.12、轮数 16.55、连杆数 5.10。

> **图 14：Articraft-10K 的网格统计。**  
> 分别展示顶点、三角形和边的统计分布。

### B.3　机器人模拟的补充细节

为验证所提框架对模拟的适用性，我们将生成的 URDF 文件直接导入 NVIDIA Isaac Sim。通过利用大语言模型（LLM），为每个组件自动分配阻尼系数、质量等物理属性。我们的评估表明，生成资产天然兼容基于物理的模拟环境。

在实际任务执行中，系统从 URDF 获取全局坐标，并使用标准的逆运动学和控制算法。值得注意的是，高保真且干净的碰撞网格可改善物理交互性能和碰撞精度。更多演示见项目网站。

### B.4　LLM 与推理强度消融的细节

图 7 中的消融实验对所有运行使用同一条受控提示词，以及相同的 Articraft harness 和 SDK。模型对比中，OpenAI GPT-5.5、Google Gemini 3.1 Pro 和 Anthropic Claude Opus 4.7 均以高推理强度运行。推理强度对比中，GPT-5.5 分别以低、中、高强度运行。该消融旨在展示固定提示词下几何和表面细节的定性差异，而非给出决定性的模型排名。

> 一架紧凑的折叠式四旋翼无人机。中央机身承载四个带铰链的机臂；每个机臂末端有电机舱和旋翼；另外具有简单的着陆滑橇和一个小型机鼻摄像头。请使其细节丰富且逼真。每个旋翼均绕其电机轴连续旋转；每个机臂均在机身根部通过旋转铰链折叠；摄像头绕一条水平旋转轴俯仰。

### B.5　失败案例与验证权衡

Articraft 的轻量设计意味着验证必须在覆盖率与成本之间权衡。为了让合成数据生成保持低成本且可扩展，harness 聚焦于高价值的结构检查，例如检测悬浮部件和非预期重叠。虽然 SDK 支持在许多关节姿态下检查物体，但穷举姿态采样会显著增加运行时间。因此，我们使用软提示词引导 agent 编写少量有针对性的测试，而不是对每一种运动配置进行穷举验证。

> **图 15：Articraft-10K 中每个物体的 URDF 关节数分布。**  
> 按移动副（Prismatic）、旋转副（Revolute）、连续关节（Continuous）和固定关节（Fixed）分组；图中平均数依次为 1.26、1.68、0.77 和 0.39。

> **图 16：Articraft 生成的更多图像条件可动物体 3D 资产示例。**  
> 示例提示词包括：“game boy”、“pixar lamp”、“artist's manikin”、“Nintendo DS Lite”、“penny-farthing”、“A wooden cabinet”、“Chinese carved fan”和“Fidget spinner”。

这种设计使生成保持高效，但也使一些失败模式落在默认验证范围之外。图 18 给出了若干示例。

第一类失败是：尽管通过了局部结构检查，整体形状质量仍然较差。例如，在 “screwcap bottle” 案例中，瓶身外壳有明显畸形。测试套件无法检测该问题，因为所生成外壳仍编译为连通网格，不引入未允许的部件间重叠，并且满足为瓶盖、瓶颈和旋转轴编写的局部测试。换言之，这些检查验证的是结构一致性和选定的几何关系，却不能完全判断类别级的视觉可信度或整体表面质量。“skateboard” 和 “revolving door” 案例也会出现类似失败：物体虽可避免悬浮部件和非预期重叠，但视觉上仍不令人满意。

第二类失败来自于那些难以用当前 SDK 紧凑表达的机构或形状。例如，“trigger spray bottle” 案例捕获了喷头机构的若干部件，但扳机的形状与运动难以干净建模，且扳机可能在运动过程中与瓶身重叠。这些案例表明，某些类别将受益于更丰富的机构专用抽象或额外的姿态检查。

> **图 17：Articraft 无缝整合进 LiteReality [14] 管线。**  
> Articraft 取代原有基于检索的物体阶段，动态生成可动物体资产；这些资产与重建的场景上下文良好对齐。

> **图 18：Articraft 的失败案例。**  
> 所示提示词包括：“screwcap bottle”、“skateboard”、“revolving door”、“trigger spray bottle”、“rice cooker”和“refrigerator with hinged doors”。

最后，在更复杂的类别中还会偶发一些失败。即使外观和关节运动看似合理，agent 仍可能遗漏内部结构，或未将应为空心的形状掏空，例如 “rice cooker” 和 “refrigerator with hinged doors” 案例。这些错误反映了当前“低成本验证”与“更强语义/功能检查”之间的取舍：harness 能高效强制许多结构约束，但尚不能完整捕获各类别关于真实感和完整性的全部特定要求。

**表 6：在 Lightwheel 基准的 14 个类别上，对 Particulate 与 Particulate-Articraft 的逐类别评估结果。**  
原表中，绿色底纹类别不在 Particulate 的训练数据中；枣红色数值表示较优值。Articraft-10K 数据集在此前分布外类别上带来更显著的改进。

| 模型 | 指标 | 搅拌机 | 咖啡机 | 洗碗机 | 电热水壶 | 微波炉 | 烤箱 | 抽油烟机 | 冰箱 | 水槽 | 台式搅拌机 | 炉具 | 灶台 | 烤面包机 | 小烤箱 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Particulate [22] | mIoU (rest) | 0.708 | 0.435 | 0.811 | 0.674 | 0.802 | 0.521 | 0.303 | 0.633 | 0.508 | 0.284 | 0.543 | 0.373 | 0.509 | 0.490 |
|  | gIoU (rest) | 0.501 | 0.038 | 0.689 | 0.390 | 0.632 | 0.203 | -0.088 | 0.498 | 0.425 | -0.071 | 0.292 | -0.007 | 0.199 | 0.134 |
|  | PC (rest) | 0.121 | 0.278 | 0.088 | 0.207 | 0.115 | 0.234 | 0.273 | 0.072 | 0.047 | 0.281 | 0.141 | 0.195 | 0.214 | 0.252 |
|  | gIoU (art.) | 0.456 | 0.033 | 0.640 | 0.330 | 0.580 | 0.179 | -0.088 | 0.452 | 0.423 | -0.083 | 0.274 | -0.012 | 0.181 | 0.110 |
|  | PC (art.) | 0.171 | 0.321 | 0.177 | 0.276 | 0.116 | 0.242 | 0.276 | 0.075 | 0.158 | 0.482 | 0.147 | 0.203 | 0.220 | 0.254 |
|  | OC (art.) | 0.019 | 0.012 | 0.027 | 0.018 | 0.000 | 0.005 | 0.002 | 0.001 | 0.003 | 0.038 | 0.001 | 0.001 | 0.001 | 0.002 |
| Particulate-Articraft | mIoU (rest) | 0.546 | 0.457 | 0.820 | 0.666 | 0.812 | 0.645 | 0.512 | 0.699 | 0.436 | 0.441 | 0.692 | 0.506 | 0.580 | 0.650 |
|  | gIoU (rest) | 0.360 | 0.070 | 0.704 | 0.374 | 0.658 | 0.435 | 0.232 | 0.577 | 0.289 | 0.179 | 0.567 | 0.225 | 0.383 | 0.397 |
|  | PC (rest) | 0.121 | 0.261 | 0.083 | 0.213 | 0.107 | 0.167 | 0.174 | 0.066 | 0.091 | 0.196 | 0.084 | 0.158 | 0.136 | 0.177 |
|  | gIoU (art.) | 0.331 | 0.065 | 0.652 | 0.313 | 0.608 | 0.407 | 0.214 | 0.526 | 0.286 | 0.146 | 0.518 | 0.214 | 0.356 | 0.347 |
|  | PC (art.) | 0.181 | 0.311 | 0.175 | 0.277 | 0.108 | 0.185 | 0.176 | 0.074 | 0.112 | 0.338 | 0.098 | 0.238 | 0.178 | 0.177 |
|  | OC (art.) | 0.020 | 0.009 | 0.029 | 0.018 | 0.000 | 0.010 | 0.001 | 0.002 | 0.005 | 0.034 | 0.002 | 0.000 | 0.001 | 0.002 |

**表 7：图 7 中 LLM 与推理强度消融的运行统计。**  
token 数为记录的提供商日志中的提示词/输出 token 的四舍五入值；视觉元素数从已实例化的 URDF 文件测得。

| 提供商 | 模型 | 推理强度 | 轮数 | 成本 | 视觉元素数 | 提示词/输出 token |
|---|---|---|---:|---:|---:|---:|
| OpenAI | `gpt-5.5-2026-04-23` | low | 17 | \$0.60 | 39 | 362K / 4.8K |
| OpenAI | `gpt-5.5-2026-04-23` | med | 15 | \$1.08 | 51 | 398K / 11.1K |
| OpenAI | `gpt-5.5-2026-04-23` | high | 22 | \$1.37 | 78 | 961K / 19.2K |
| Google | `gemini-3.1-pro-preview` | high | 26 | \$3.14 | 13 | 1.54M / 5.3K |
| Anthropic | `claude-opus-4-7` | high | 26 | \$1.97 | 43 | 1.61M / 27.6K |

> **图 19：Articraft 生成的更多可动物体资产。**  
> 结果覆盖广泛的物体类别与尺度，从日常小物件到机械组件、家具、电器以及大尺度户外结构。  
> 图中提示词包括：“barrier gate”、“simple drying rack”、“old windmill”、“adjustable weight bench hinged backrest”、“gear assemblies”、“folding kick scooter”、“pet door flap”、“wheelbarrow”、“classic occ bottle articulated cap”、“extension ladder”、“single-leaf drawbridge”、“playground swing”、“display freezer sliding glass lids”、“orchestra style music stand”、“desktop PC tower”、“barrier”、“syringe”、“cannon”、“miter saw arm assembly”、“lighthouse rotating beacon assembly”、“sewing box with hinged lid”和“stove top with oven”。

---

## C　Agent 提示词与运行时细节

### 输入构造

每次运行时，Articraft 向模型发送一个提供商特定的系统提示词，随后发送两条用户消息。第一条用户消息不是任务提示词，而是一个紧凑的工作区与文档数据包。该数据包告知模型：`model.py` 是唯一可编辑的工件；全部 SDK 文档位于只读的 `docs/` 下；当需要精确 API 文本时，应调用 `read_file`。该消息还预加载三份简短参考：SDK quickstart、`probe_model` 参考和测试参考。

第二条用户消息包含实际生成请求：一小段运行时指导，随后是物体提示词，以及存在时的参考图像。

```text
SYSTEM:
<提供商特定的 Articraft 系统提示词>

USER MESSAGE 1:
# 工作区文档（只读）

虚拟工作区将 `model.py` 暴露为可编辑资产脚本，并将 `docs/` 暴露为只读 SDK 指南。
`docs/sdk/references/quickstart.md` 是预加载的 SDK 入口和参考索引。
需要精确文本时，请通过这些虚拟路径调用 `read_file(path=...)`。

## docs/sdk/references/quickstart.md
# SDK 快速入门

## 用途
使用此页面开始新的 Articraft SDK 脚本。它定义所需脚本契约、
创作工作区规则，以及一个最小端到端示例。

## 虚拟工作区
- `model.py` 是唯一可写文件。
- `docs/sdk/references/quickstart.md` 是始终加载的入口。
- `docs/` 下的所有内容都是只读 SDK 指南。
- 在 `model.py` 中从 `sdk` 导入。
- 仅在需要时通过 `read_file(path=...)` 加载精确参考文本。

## 已挂载的参考布局
在 `docs/sdk/references/` 中始终可用：
- `quickstart.md`
- `errors.md`
- `core-types.md`
- `articulated-object.md`
- `placement.md`
- `probe-tooling.md`
- `testing.md`
- `geometry/fans-and-rotors.md`
- `geometry/hinges.md`
- ...

## 脚本契约
每个生成的脚本应定义：
- `build_object_model() -> ArticulatedObject`
- `run_tests() -> TestReport`
- `object_model = build_object_model()`

## docs/sdk/references/probe-tooling.md
# 探测工具
`probe_model` 是仅检查工具，用于针对当前 `object_model`
运行一段简短 Python 代码。

## docs/sdk/references/testing.md
# 测试
`TestContext` 记录阻塞性失败、非阻塞警告和显式允许项。
生成模型应以 `return ctx.report()` 结束 `run_tests()`。

USER MESSAGE 2:
<runtime_task_guidance>
- 编辑前先读取当前 `model.py`。
- 每次只做一个小而连贯的修改。
- 将视觉真实感视作交付物的一部分：令物体清晰呈现为请求的对象，
  具有可信的比例、轮廓、颜色/材质和主要可见表面处理。
- 运行 `compile_model` 检查最新版本。
- 若编译结果干净，且你无法指出一个具体的剩余缺陷，即结束。
</runtime_task_guidance>

<object prompt>
[可选参考图像]
```

### 系统指令

系统提示词将 Articraft 定义为：在受限虚拟工作区中运行、会使用工具的创作 agent。其主要要求是：几何真实、使主要面向用户的机构可动、不出现悬浮部件、没有非预期重叠。提示词还要求模型将编译、QC 和编写的测试视为传感器；仅将示例用作可复用的构造思路；通过工具施加代码更改，而不是在自然语言回复中返回代码。

提供商变体主要在编辑工具上不同：OpenAI 使用 `apply_patch`，Gemini、Anthropic 和 OpenRouter 使用 `replace` 与 `write_file`。所有变体都提供 `read_file`、`find_examples`、`compile_model` 和 `probe_model`。以下复现 OpenAI 系统提示词变体。

```text
<role>
- 你是 Articraft Agent。你通过工具编辑绑定的代码文件，生成可动物体 3D 对象。
- 你在沙盒化虚拟工作区中工作，其中仅有一个可写文件：`model.py`。
  只读的 `docs/` 树包含规范 SDK 指南。不得检查、修改或依赖这个虚拟
  工作区之外的任何内容。不得尝试管理资产路径、编译、实例化、服务或运行时
  基础设施；Articraft 会自动处理这些事项。
- 成功意味着：资产通过验证，并且清晰呈现为所请求的对象。
- 每项决策均由四个硬性要求驱动：

  1. 真实几何（REALISTIC GEOMETRY）——这是最主要的质量标准。
     选择最符合真实形态的 SDK 表示。仅在简单基本体确实正确时使用它们；
     若形状需要，则使用 loft、sweep、布尔运算、wire 或 CadQuery 几何。
     现实中为空心的物体（杯子、碗、外壳、壳体）应建模为空心，而非实心。
     使用真实世界的绝对尺寸（例如椅面高度约 0.45 m、烤架高度约 1 m），
     不要猜测任意的小尺度。除非提示词明确要求无颜色原型或抽象研究，
     否则为主要可见表面分配合理的颜色与材质，且不要让主要可见表面保持
     通用占位材质。应让工具与物体相匹配，并优先保证视觉真实感和机械可信度。

  2. 使主要机构可动（ARTICULATE THE PRIMARY MECHANISMS）——
     建模主要的、面向用户的关节运动。除非次要关节在视觉或机械上显著，
     否则不要虚构它们。对电器、电子设备、仪器及其他控制件较多的物体，
     当真实物体将按钮、旋钮、开关、按键、操纵杆、踏板和其他明显可见的
     用户控制件呈现为独立可动部件时，应使它们可动。若真实物体显然有独立
     可见的控制件，静态地将控制面板融合在一起通常是错误选择。每个纳入的
     关节都应有符合真实机构的运动范围。

  3. 不得有悬浮部件（NO FLOATING PARTS）——每个部件都必须在物理上
     相连或被安装；每个部件本身也必须呈现为受支撑的总成，而非由互不相连的
     悬浮子部件组成。若一个特征看起来独立，请提供现实中承载它的结构：
     连接桥、支架、壁、轴、铰链筒、凸台、框架接触或外壳连接。
     有意悬浮（例如飞行中的无人机螺旋桨）必须在测试中明确说明其理由。

  4. 不得有非预期重叠（NO UNINTENTIONAL OVERLAPS）——当部件应彼此
     区分时，应优先采用真实的间隔；但当局部隐藏重叠能提升嵌套、夹持、
     压缩或就位插入的机械真实感时，可以接受。尽可能让有意重叠保持局部且
     限定到特定元素，绝不能借它掩盖错误的关节原点、轴或运动范围。
     若设计确实需要重叠，应通过测试中的限定允许项明确说明理由，而非强行
     制造人为分离。
- 将编译输出、QC 和测试视作传感器，而不是优化目标。
- 示例只可用于可复用思路；不得完整模仿其结构。
- 不得直接在 assistant 回复中给出代码；只能通过工具施加代码更改。
- 除非硬性阻塞使继续进行不可能，否则不要向用户请求反馈、确认或继续许可；
  应自主完成任务。
</role>

<link_naming>
- link 名称属于交付物质量标准的一部分：应简洁、具有语义，并以物体的
  内在参考系为依据，而非任意标签或状态标签。
- 为每个 link 提供极简语义名：理想情况下仅用部件名称；只有在需要区分
  相似部件时，才加入简短的内在位置或形状提示。
- 每个 link 名称应是单个下划线连接的字符串，最多 5 个词。
- 不得在 link 名称中编码关节状态。避免 `open`、`closed`、`extended`、
  `pulled_out`、`ajar`、`tilted` 或 `rotated` 等状态词。
- 优先选择说明部件是什么、并在有帮助时说明其形状的名称。
- 仅当物体具有有意义的规范朝向或其他明确的物体内在参考系时，才使用位置词。
- 当相似部件可被可靠区分时，优先使用物体内在空间线索，如
  `front_handle` 或 `side_support`。
- 对于对称或朝向含混的物体，不要擅自构造 `left`、`right`、`front` 或
  `back` 区别。一些物体只有部分内在参考系：人形物体可有 `left_arm`，
  但对称橱柜的两扇门通常不应命名为 `left_door` 和 `right_door`。
- 若仅有部分内在参考系有意义，就只使用那一部分。例如若 `front` 与 `back`
  有意义、而 `left` 与 `right` 含混，则需要时使用 `front_*` 或 `rear_*`，
  不要强行添加侧向标签。
- 若重复部件在语义上相同且无法通过内在属性区分，则复用同一基础名称并添加
  数字后缀，如 `door_0`、`door_1`。对于二维重复布局，可接受
  `key_0_0`、`key_0_1` 一类名称。
</link_naming>

<tools>
- 可用工具：`read_file`、`apply_patch`、`compile_model`、`probe_model`
  和 `find_examples`。
- `read_file` 是读取精确虚拟工作区文件文本的 JSON 工具。
- `apply_patch` 是 FREEFORM 工具；应发送原始 patch 文本，而非 JSON。
- `compile_model` 运行编译 + QC，并返回结构化的 `<compile_signals>`。
- `probe_model` 是只读 Python 检查工具；不允许写文件、变更对象或启动子进程。
- `find_examples` 在经整理的 SDK 示例中搜索模式。应根据当前 SDK 文档改造
  结果，不能机械复制示例代码；标为 `[weakly relevant]` 的条目仅可作灵感。
- 每次 patch 前，必须用 `read_file(path="model.py")` 读取当前精确文件文本。
- 应优先进行数个小型 `apply_patch` 编辑，而不是一次巨型 patch 或整文件重写。
- 修改现有可编辑代码，而不是假设从空白开始。
</tools>

<modeling>
GEOMETRY
- 将 `build_object_model()` 和 `run_tests()` 保持为顶层入口点。
- 在 `model.py` 中直接从 `sdk` 导入公开创作 API。
- 不要从文档主题名猜测 Python 子模块。例如使用
  `from sdk import place_on_face`，而不是
  `from sdk.placement import place_on_face`。
- 当它们足以可信表达形态时，优先使用 Articraft 原生基本体和放置辅助函数；
  这比纯 CadQuery 更简单。
- 仅对需要更低层形状控制的高级部分使用 CadQuery，例如空心壳、连续曲面、
  loft、sweep、布尔切割细节，或否则会显得像占位符的形状。
- 可以自由混用方法；除非整个物体都需要 CadQuery，否则不要把整个物体切换到
  CadQuery。
- 应匹配物体可见的构造逻辑。若一个面应呈现为连续制造件，应将其保留为带开口
  或切口的连通面，而非用分离、悬浮的构件重建。只有当可见形态确实应由离散
  构件组成时，才采用基于构件的构造。
- 编写网格支撑的 visual 时，使用受管理的逻辑名称，例如
  `mesh_from_geometry(..., "door_panel")` 或
  `mesh_from_cadquery(..., "door_panel")`；不要推理文件系统路径。
- 只编写视觉几何；不要在 `sdk` 中编写碰撞几何。
- 保持正确的关节原点、轴、限制和关节运动行为。

TESTING
- 使用 `sdk.TestContext`，返回 `ctx.report()`，并让 `compile_model` 负责
  基线合理性/QC 检查。
- 优先使用 `TestContext(object_model)`；新代码中不要传入资产根目录。
- 只将 `run_tests()` 用于提示词特定的精确检查、针对性姿态检查和显式允许项。
- 首先将重叠发现视为分类问题：判断报告的相交是应由受限
  `ctx.allow_overlap(...)` 覆盖的有意设计嵌入，还是应通过调整几何、安装或
  姿态来修复的非预期碰撞。可接受的有意情形包括代理几何嵌套、被捕获的销或轴、
  就位的饰条和柔顺压缩。
- 每个 `ctx.allow_overlap(...)` 都应至少配对一项精确证明检查，例如
  `expect_within(...)`、`expect_overlap(...)`、
  `expect_gap(..., max_penetration=...)`、`expect_contact(...)`，
  或一项决定性的姿态检查。
</modeling>
```

### C.1　暴露给 agent 的代表性 SDK 能力

agent 在 `model.py` 中从 `sdk` 导入公开 API 来编写资产；它不直接输出网格文件或 URDF。表 8 汇总这一创作接口中的代表性部分。列表并不穷尽，但说明模型可使用的结构化几何、关节和测试 API 的广度。

**表 8：Articraft 面向程序化资产创作而暴露的代表性 SDK 能力。**

| 类型 | 描述 | 示例 API |
|---|---|---|
| 对象模型 | 具有命名 visual、材质、原点和可选惯性属性的语义部件图。 | `ArticulatedObject`, `Part`, `Visual`, `Material`, `Origin` |
| 基础形状 | 用于方盒、圆柱、圆锥、穹顶、球、胶囊体，以及导入或生成网格的轻量实体。 | `Box`, `Cylinder`, `ConeGeometry`, `Sphere`, `Mesh` |
| 关节 | 含父/子 link、轴、原点、限制、动力学和 mimic 关系的运动学关节。 | `ArticulationType`, `MotionLimits`, `MotionProperties`, `Mimic` |
| 放置 | 将几何安装在面或任意表面上的辅助函数，同时显式保持齐平、凸出和对齐关系。 | `place_on_face`, `place_on_surface`, `proud_for_flush_mount` |
| 线材 | 曲管、导轨、把手、走线及自定义扫掠轮廓。 | `WirePath`, `tube_from_spline_points`, `sweep_profile_along_spline` |
| 车轮与轮胎 | 包含轮辋、轮毂、辐条、孔、胎面和胎侧的详细车轮、轮胎总成。 | `WheelGeometry`, `WheelSpokes`, `WheelBore`, `TireGeometry` |
| 铰链 | 门、盖、翻板和连续铰链条的外露铰链硬件。 | `BarrelHingeGeometry`, `PianoHingeGeometry`, `HingeHolePattern` |
| 控制件 | 带裙边、抓握部、指示器、轴孔、帽和浮雕的旋钮式控制件。 | `KnobGeometry`, `KnobGrip`, `KnobIndicator`, `KnobBore` |
| 面板与格栅 | 开口、穿孔面板、槽孔模式、通风百叶、框架、套筒和安装细节。 | `ExtrudeWithHolesGeometry`, `PerforatedPanelGeometry`, `VentGrilleGeometry` |
| 支架与安装件 | 用于叉架、叉形耳、轭架、枢轴和可见安装结构的带销支撑硬件。 | `ClevisBracketGeometry`, `PivotForkGeometry`, `TrunnionYokeGeometry` |
| 曲面 | 用于制造型曲面的 loft、sweep、管、车削体、超椭圆轮廓和壳体分割。 | `LoftGeometry`, `SweepGeometry`, `section_loft`, `partition_shell` |
| 测试 | 用于姿态、包含关系、间隙、接触、有意重叠及提示词特定不变量的编写式检查。 | `TestContext`, `expect_*`, `allow_overlap`, `ctx.pose` |

### C.2　Agent 轨迹示例

公开的轨迹可将“编辑—执行—修复”循环审计到单次工具调用的粒度。图 20 给出一个 GPT-5.5 运行的人工整理摘录；该运行生成了一个人工评分为 5 星的可移动工具箱，具有内凹式车轮、前部铰链门和可伸缩后部拉手。摘录展示模型如何读取工作区、检索示例、从 harness 接收结构化反馈、用探测工具检查几何，并将修复决策转换为显式测试和受限重叠允许项。

- **记录。**OpenAI `gpt-5.5-2026-04-23`；人工评分为 5；提示词要求生成一个高大的可移动工具箱，带内凹车轮、前部铰链门和可伸缩后部拉手。
- **调用的工具。**`read_file` ×11、`find_examples` ×1、`compile_model` ×5、`probe_model` ×5、`apply_patch` ×7。
- **第 1–5 轮：工作区落地。**agent 读取 `model.py`，以及关于核心类型、可动物体、CadQuery、旋钮和控制件、车轮/轮胎几何的 SDK 参考。
- **第 6–10 轮：示例检索和第一次构造。**`find_examples` 检索车轮和轮胎模式；最初的 patch 实例化工具箱主体、内凹车轮、门关节和拉手机构。
- **第 11–18 轮：结构化编译反馈。**`compile_model` 返回带类型的失败、警告、注释和响应规则；无效的连续关节限制、悬浮车轮、拉手重叠和几何断连警告被呈现为彼此独立的修复目标。
- **第 19–23 轮：针对性检查。**`probe_model` 代码片段检查 AABB、部件摘要和辅助函数可用性。agent 使用这些测量以及轻量 `catalog()` 探测，选择下一次修复所需的精确几何辅助函数。
- **第 24–25 轮：范围受限的修复和验收。**`apply_patch` 添加后部导向衬套，恢复精确 visual 名称，并为车轴捕获和伸缩杆限定有意重叠。最终 `compile_model` 返回 `status=success`、`failures=0`、`warnings=0`、`notes=7`。

```text
<compile_signals>
<summary>
status=failure failures=1 warnings=0 notes=3
这是连续第 4 次编译失败。
</summary>

<failures>
- [isolated_part] 检测到悬浮的断连组件。
部件 `pull_handle` 与以 `body` 为根的已接地主体断开；
nearest_grounded_part=`body`；approx_gap=0.006m。
</failures>

<notes>
- [allowed_overlap] allow_overlap(`body`, `wheel_0`)，
  elem_a=`axle_stub_0`，elem_b=`rim`：
  固定车轴短轴有意被捕获在车轮孔中。
</notes>

<response_rules>
- 在调整编写的精确检查之前，应将编译器拥有的“悬浮/断连部件”发现视为首要证据。
- 当前处于修复循环中；相比于再次进行小幅放置或容差调整，一段简短的
  `probe_model` 代码很可能提供更多信息。
</response_rules>
</compile_signals>
```

下列代码摘录保留原样；其含义是：允许车轴短轴嵌在车轮孔内，允许伸缩杆穿过后部导向衬套，并验证拉手在运动后向上移动至少 `0.25`。

```python
ctx.allow_overlap(
    body, wheel_0, elem_a="axle_stub_0", elem_b="rim",
    reason="The axle stub is intentionally captured inside the wheel bore.",
)

for guide_name in ("handle_guide_0", "handle_guide_1"):
    for rod_name in ("handle_rod_0", "handle_rod_1"):
        ctx.allow_overlap(
            body, pull_handle, elem_a=guide_name, elem_b=rod_name,
            reason="The rods intentionally pass through rear guide bushings.",
        )

rest_handle_pos = ctx.part_world_position(pull_handle)
with ctx.pose({handle_joint: HANDLE_TRAVEL}):
    extended_handle_pos = ctx.part_world_position(pull_handle)

ctx.check(
    "pull handle extends upward",
    rest_handle_pos is not None
    and extended_handle_pos is not None
    and extended_handle_pos[2] > rest_handle_pos[2] + 0.25,
)
```

> **图 20：一个 5 星可移动工具箱资产的 GPT-5.5 轨迹摘录。**  
> 该轨迹展示了多样的工具使用，并突出 harness 为指导修复而提供的结构化反馈。

**上下文压缩。**对于较长运行，harness 可在下一次模型调用前压缩较早的对话历史。压缩不会在每一轮都执行。它会由两种条件之一触发：硬性上下文窗口压力，或软性的修复平台规则——重复编译失败、足够的上下文压力以及足够可压缩的历史。该策略保留不可变的运行前缀和最新的原始尾部，并将较早的中间历史替换为关于任务要求、约束、工具发现、编译状态和后续步骤的紧凑摘要。

OpenAI 使用 Responses API 的压缩端点；Gemini 使用单独的 JSON 摘要提示词。当前实现中，Anthropic 运行不使用提供商侧压缩。

**表 9：当前 harness 使用的上下文压缩阈值。**  
硬压缩在所列压力阈值的 `0.9` 倍处触发。在重复编译失败平台期，软压缩可更早触发。

| 提供商/模型族 | 压力阈值 | 压缩机制 |
|---|---:|---|
| OpenAI GPT-5.4/5.5 [40, 41] | 272k 提示词 token | 通过 Responses API 压缩较早的输入项。 |
| OpenAI GPT-5.2 和 GPT-5.2/5.3-Codex [36, 37, 39] | 280k 提示词 token | 通过 Responses API 压缩较早的输入项。 |
| Gemini 3.1 Pro [12] / Gemini 2.5 | 700k 提示词 token | 由 Gemini 压缩提示词产生 JSON 摘要。 |
| Anthropic | — | 当前实现中不使用提供商侧压缩。 |

---

## D　补充相关工作

**可动物体重建。**已有多项工作研究过重建可动物体的问题。Shape2Motion [51] 从 3D 点云出发，将其分割为部件及其关节。[23] 的工作利用规范空间解决类似问题；CAPTRA [52] 还进一步随时间跟踪部件运动。A-SDF [33] 提出有关于节的有符号距离函数版本，用于建模可动物体。DITTO [15] 从展示不同姿态的一对图像重建可动物体 3D 对象；PARIS [27] 则以自监督方式完成此事。与这些工作不同，我们的目标是根据文本提示词生成一个新的可动物体。

---

## E　社会影响

Articraft 可通过降低为动画、游戏、教育、机器人模拟和具身 AI 研究制作可动物体 3D 资产的成本，产生积极社会影响。所生成的资产可帮助研究人员构建更多样的模拟环境，并在无需人工制作每一个物体的情况下研究操作、规划和交互。

同时，可扩展资产生成也可能被滥用于创建用于欺骗性视觉内容的合成环境或物体、未经授权复制专有设计，或进行不安全的具身 agent 训练。生成的几何和关节也可能含有错误，并传播到下游模拟器或机器人中，尤其是在安全关键的操作场景下。因此，我们主要将 Articraft 视为研究工具，并建议实际部署时：在目标领域验证生成资产；尊重物体与数据集的许可约束；当生成资产用于较高风险场景时，施加适当的访问控制或监测。
