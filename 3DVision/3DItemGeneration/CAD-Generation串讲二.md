# CAD Generation 串讲（二）：从表示学习到可验证资产系统

> 面向汇报与追问的知识框架：不靠堆论文名，而是用“任务线、系统层、时间线”组织 CAD 生成、几何生成与可动资产生成。

## 目录

1. [三条任务线](#一三条任务线)
2. [系统层级](#二系统层级)
3. [时间线与核心分叉](#三时间线与核心分叉)
4. [2025–2026：可动资产与 Agent](#四20252026可动资产与-agent)
5. [将框架落到自己的研究](#五将框架落到自己的研究)
6. [汇报速记与辨析](#六汇报速记与辨析)

你的问题不是“没有调研”，而是信息已经超过了工作记忆能直接调用的容量。尤其在 AI 辅助整理之后，常见状态是：论文名很熟，但被追问“它和另一个工作差在哪”时，脑中没有一条可直接调用的链。

这份串讲不要求背论文，而是按仓库已有的组织方式建立一个**可用于汇报和追问的脑内模型**：研究对象正从“形状”走向“CAD 程序/结构”，再走向“可执行、可验证的资产系统”。

## 一、三条任务线

CAD Generation 并不是一条单线。先记住三条主线：

你脑子里先只保留 **三条河**：

```text
                    3D Generation
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
   Static CAD      Geometry/Surface   Articulated Object
   静态工程设计       复杂几何生成          可运动资产
```

### 1. 静态工程设计（Static CAD）

它回答：

> **这个东西是怎么“设计出来”的？**

关心：

- sketch

- constraint

- extrude

- Boolean

- fillet/chamfer

- feature history

- B-Rep

- STEP

- CadQuery / Build123d program

最终目标是：

**editable / parametric / manufacturable CAD。**

代表工作你先记：

```text
CSGNet
  ↓
DeepCAD
  ↓
SkexGen
  ↓
Text2CAD
  ↓
Arko-T / STEP-LLM
  ↓
CADSmith / FutureCAD / Zero-to-CAD
```

### 2. 几何与曲面（Geometry / Surface）

它回答的不是“这个东西怎么设计”，而是：

> **这么复杂的几何形状怎么表示、怎么生成？**

关心：

- SDF

- mesh

- spline

- NURBS

- B-Rep face

- topology

- Flow Matching / Diffusion

代表链：

```text
DeepSDF
  ↓
ParSeNet / Neural Splines
  ↓
ComplexGen
  ↓
BrepGen
  ↓
HoLa / DTGBrepGen
  ↓
Flatten The Complex / DualBrep
```

这条线容易和 CAD 搞混。

你要永远记住：

> **会生成一个漂亮 B-Rep / NURBS，不等于理解 CAD design intent。**

比如它可以生成一个完美的圆孔。

但它可能不知道：

> 这个孔应该始终与矩形中心 coincident。

这就是 geometry 和 design 的区别。

### 3. 可动对象（Articulated Object）

它回答：

> **这个东西里面哪些部分能动，它们怎么动？**

核心表示不是单纯 mesh，而是：

```text
part / link
parent-child
joint type
joint axis
joint origin
joint limit
URDF
```

你自己的文档里已经把这一条单独拆出来了。

代表链你先这样记：

```text
NAP
 ↓
ArtFormer
 ↓
Articulate-Anything
 ↓
URDF-Anything
 ↓
SPARK / ArtLLM
 ↓
LAM / ArtiCAD / Articraft
```

这三条河到了 **2026** 开始汇合。

这才是你真正感兴趣的地方。

## 二、系统层级

这一张系统图甚至比论文名更重要：

这一张甚至比论文名字重要：

```text
Natural Language / Image
          ↓
CAD Program / Feature History
          ↓
      CAD Kernel
          ↓
    B-Rep Topology
          ↓
Face Geometry
NURBS / analytic surfaces / mesh
          ↓
Parts / Connectors
          ↓
Joints / Articulation
          ↓
URDF / Simulation
          ↓
Physics Validation
```

这里每一层对应完全不同的问题。

比如：

### 典型工作分别位于哪里？

#### Text2CAD

主要在：

```text
Text
 ↓
CAD history
```

#### BrepGen

主要在：

```text
latent
 ↓
B-Rep
```

#### NURBGen

主要在：

```text
Text
 ↓
NURBS / analytic surface
 ↓
B-Rep
```

#### URDF-Anything

主要在：

```text
Point cloud
 ↓
part segmentation + joints
 ↓
URDF
```

#### CADSmith

主要在：

```text
Text
 ↓
CAD program
 ↓
kernel execution
 ↓
validation
 ↓
repair
```

#### Articraft

进一步是：

```text
Text
 ↓
program
 ↓
parts + joints
 ↓
compile / probe / tests
 ↓
repair
```

这样以后别人随便丢一个论文名，你第一反应不是：

> “完了，我看过没？”

而是：

> **“它在哪一层？”**

这就是领域专家最重要的反射。

## 三、时间线与核心分叉

### 第一时代：2017–2021——表示与程序化构造

问题是：

> **3D 到底怎么让神经网络表示？**

所以这时候做的是 representation。

#### DeepSDF

记一句：

> **shape = continuous signed distance field。**

它影响很大，但：

**不是 CAD generation。**

因为没有：

- feature history

- constraint

- editable program

#### CSGNet

第一次开始出现：

```text
shape
 ↓
primitive
 ↓
Boolean program
```

重要意义：

> **3D shape 可以被表达成“程序”。**

这个思想后来非常关键。

#### DeepCAD

这篇你必须熟。

它的重要性不是单纯“用了 Transformer”。

真正意义是：

> **把 CAD construction history 当成 sequence。**

于是：

```text
Sketch
Extrude
Sketch
Extrude
...
```

开始变成像语言一样可以学习的 token sequence。

这就是后面 Text2CAD 的祖宗。

所以：

```text
CSGNet：shape → Boolean program
DeepCAD：CAD → construction sequence
```

区别要秒答。

### 第二时代：2022–2024——History-first 与 B-Rep-first

这时候开始出现一个非常关键的分叉：

#### 核心分叉：History-first vs. B-Rep-first

这条是汇报 CAD generation 时必须能讲清楚的基本分叉。

##### History-first

目标：

```text
生成设计过程
```

比如：

```python
sketch circle
constraint coincident
extrude 20
fillet edge
```

优点：

**可编辑、有参数、有 construction semantics。**

代表：

- DeepCAD

- SkexGen

- Text2CAD

- TransCAD

##### B-Rep-first

目标：

```text
直接生成最终 CAD 边界
vertices
edges
faces
```

代表：

- SolidGen

- BrepGen

优点：

> geometry representation 更强。

缺点：

> **不天然知道这个东西是怎么设计出来的。**

所以：

```text
History-first
  = design process 强

B-Rep-first
  = final geometry 强
```

这是整个 CAD generation 至今仍然存在的基本 tension。

#### Vitruvion：设计意图为什么重要？

你之前问 design intent，我特别希望你把它放回这里。

Vitruvion 做：

```text
2D primitives
+
constraints
```

比如：

```text
circle
rectangle
coincident
parallel
equal
tangent
```

真正关键的不是：

> 画出来像不像。

而是：

> **改变一个参数以后，其他 geometry 是否按照约束一起变化。**

所以：

```text
Geometry
≠
Design Intent
```

这一点后来直接通向：

- constraint generation

- design alignment

- parametric editability

- edit robustness

所以 Vitruvion 是你未来那个方向的重要祖先。

#### Text2CAD：自然语言进入 CAD

DeepCAD：

```text
CAD sequence → representation/generation
```

Text2CAD：

```text
Natural language
       ↓
CAD command sequence
```

这时候才正式进入：

**Text-to-CAD**

但是它有一个非常大的限制：

它的 CAD language / operation space 相对受限。

这就是为什么到了 2025–2026，大家突然大量转向：

```text
LLM
 ↓
Python CAD code
 ↓
CadQuery / Build123d / FreeCAD
```

因为大语言模型本身就会写程序。

于是：

> **为什么还要重新设计一个很小的 CAD token vocabulary？**

这是整个范式变化的重要原因之一。

#### B-Rep 生成线：几何与拓扑的联合生成

这一条你不用每篇都记。

你只记 evolution：

```text
SolidGen
 ↓
BrepGen
 ↓
HoLa / DTGBrepGen
 ↓
AutoBrep / BrepGPT
 ↓
Flatten The Complex
 ↓
DualBrep
```

核心问题一直是：

> **怎么同时生成 geometry + topology？**

因为一个 B-Rep 不是一堆面而已。

它有：

```text
Vertex
 ↓
Edge
 ↓
Wire
 ↓
Face
 ↓
Shell
 ↓
Solid
```

同时 face 里面又可能是：

```text
plane
cylinder
cone
sphere
NURBS
...
```

所以 direct B-Rep generation 是一个**几何生成问题**。

以后老板问：

> “DualBrep 和 Arko-T 什么区别？”

你甚至不用回忆论文。

直接回答：

> **DualBrep 是 B-Rep/geometry-first；Arko-T 是 program/history-first。一个生成最终几何结构，一个生成可执行的参数化设计程序。**

够了。

## 四、2025–2026：可动资产与 Agent

### 可动对象：从形状到功能对象

#### NAP

首先记 NAP。

NAP 最重要的一句话：

> **articulated object = part geometry nodes + joint kinematic edges。**

也就是说柜子不是：

```text
一个 mesh
```

而是：

```text
Cabinet body
    │
    ├── revolute → door
    │
    └── prismatic → drawer
```

这一下把研究对象从：

**shape**

变成：

**functional object。**

#### ArtFormer

它开始像 language model 那样：

```text
part
part
part
...
```

逐步长出 part tree。

每个 part 有：

- geometry latent

- bbox

- parent

- joint

所以：

> NAP 更像 graph generative prior；  
> ArtFormer 更像 autoregressive part-tree generator。

### URDF-Anything：从观测重建数字孪生

这篇你一定要会。

它不是：

> text → 新设计一个柜子。

而是：

```text
已有真实物体 point cloud
         ↓
3D MLLM
         ↓
part segmentation
+
joint JSON
         ↓
URDF
```

所以它属于：

**Reconstruction / Digital Twin**

而不是：

**From-scratch CAD generation**

这一点非常容易混。

### 2026 的变化：从一次生成到反馈闭环

这个才是你现在最需要知道的。

整个领域开始意识到：

> **只生成一次不够。**

因为 LLM 生成 CAD code 后：

```text
syntax correct
```

不代表：

```text
geometry correct
```

geometry correct 又不代表：

```text
mechanically correct
```

mechanically correct 又不代表：

```text
design intent correct
```

于是出现：

**Agent + Environment + Feedback**

这就是 2026 最大变化。

### CADSmith：典型的 CAD Agent

你记成：

```text
Planner
 ↓
Coder
 ↓
Executor
 ↓
Validator
 ↓
Refiner
 ↺
```

重点不是 multi-agent 这个包装。

真正关键是：

> **CAD kernel 开始进入 feedback loop。**

以前：

```text
LLM → code
```

现在：

```text
LLM
 ↓
code
 ↓
OpenCASCADE
 ↓
measurement / validity / render
 ↓
LLM
 ↓
repair
```

于是 CAD generation 从：

**prediction**

变成：

**search / interaction / repair。**

### Arko-T 与 CADSmith：模型和系统的区别

你这样记。

#### Arko-T

核心：

> **我训练一个更懂 structured parametric design 的模型。**

输出：

```text
Build123d program
```

强调：

- features

- parameters

- constraints

- history

- attachments

但是推理本身主要是：

```text
one-shot generation
```

#### CADSmith

核心：

> **模型不一定第一次生成对，我给它 execution feedback 修。**

所以：

```text
Arko-T
= better CAD model

CADSmith
= better CAD agent/system
```

非常重要。

### FutureCAD：B-Rep grounding

这篇你可以只记一个问题：

> **LLM 说“给这条 edge 做 fillet”，它到底知道是哪条 edge 吗？**

这是：

**B-Rep grounding**

也就是把 language / operation 和：

```text
face
edge
primitive
```

真正对应起来。

因此：

```text
FutureCAD
=
program generation
+
B-Rep grounding
```

它解决的是：

> **语言如何指向 CAD kernel 里的具体几何实体。**

### Zero-to-CAD

把它放在：

> **更大规模、更开放操作空间的 agentic program synthesis**

这一格即可。

不用背特别多。

重点是它代表整个趋势：

```text
specialized CAD token model
        ↓
general VLM / LLM
        ↓
CAD program
        ↓
tool execution
```

### LAM、ArtiCAD 与 Articraft：CAD Agent 和可动对象的汇合

这是：

**CAD Agent + Articulated Object 的汇合**

这三篇要强行分开。

#### LAM

记：

> **Language → articulated object code**

并且有：

```text
Shape generator
Articulation coder
VLM critic
Fixer
```

所以它强调：

**geometry + articulation + visual repair。**

#### ArtiCAD

记一个词：

**Connector-first**

也就是：

> 不先随便生成几个 part，再想怎么拼。

而是：

```text
先定义：
part A 在哪里连接 part B
connector coordinate frame 是什么
joint 是什么
       ↓
再生成 geometry
```

这是非常 CAD / mechanical-design-native 的思想。

#### Articraft

这篇对你现在最重要。

你自己的实验方案现在事实上已经把它作为骨架了。仓库里的整合方案明确写的是：

> **Articraft SDK 作为 articulated 语义骨架，build123d/CadQuery 做几何，Skill 负责领域知识，Multi-Agent 负责设计/诊断，Harness 负责冻结 spec、采样、碰撞、MuJoCo 和隐藏复核。**

Articraft 你只需要记住两个词：

**SDK + Harness**

它不是单纯：

```text
LLM → URDF
```

而是：

```text
LLM writes model.py
      ↓
compiler
      ↓
hard tests / probes
      ↓
failure feedback
      ↓
LLM repairs
```

因此它其实和你刚才问我的 MuJoCo 问题直接连起来了。

## 五、将框架落到自己的研究

你现在仓库已经不只是 literature survey 了。

`实验/` 下面已经有：

- 3D生成模型评测验收协议

- Unified 3D Agent SDK / Skill / Harness

- 实验数据集选择

- 评测标准解释

说明你现在实际上正在从“survey”走向“system formulation”。

而你目前的系统可以压缩成：

```text
                    User Spec
                       ↓
                   Spec Agent
                       ↓
              Test Design / Review
                       ↓
                  Coding Agent
                       ↓
          Build123d / Articraft SDK
                       ↓
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
   CAD Kernel      Kinematics      Physics
     tests            tests          tests
        ↓              ↓              ↓
 OpenCASCADE      joint sampling     MuJoCo
        └──────────────┼──────────────┘
                       ↓
                  Harness
                       ↓
               structured failure
                       ↓
                Diagnosis Agent
                       ↓
                    repair
                       ↺
```

你自己的整合文档也已经把层次划成了：

```text
Agent
 ↓
Skill
 ↓
SDK
 ↓
Harness
 ↓
OCCT / MuJoCo / simulator
```

而且明确要求 Harness 承担可信执行，而不是让 Agent 自己决定“我通过了”。

这其实已经是一个很完整的 conceptual framework。

## 六、汇报速记与辨析

### 12 个核心锚点（anchors）

不要背 80 篇。

先做到有人提这些，你可以立刻讲一句：

| 工作              | 你必须脱口而出的关键词                            |
| ----------------- | ------------------------------------------------- |
| **CSGNet**        | shape → Boolean program                           |
| **DeepCAD**       | CAD construction sequence representation          |
| **Vitruvion**     | primitive + constraint graph / design intent      |
| **SkexGen**       | topology / geometry / extrusion disentanglement   |
| **Text2CAD**      | text → CAD command history                        |
| **BrepGen**       | direct B-Rep diffusion                            |
| **NAP**           | part nodes + joint edges                          |
| **URDF-Anything** | point cloud → segmentation + URDF                 |
| **Arko-T**        | text → structured Build123d design                |
| **CADSmith**      | program generation + kernel validation + repair   |
| **FutureCAD**     | CAD program + B-Rep grounding                     |
| **Articraft**     | articulated SDK + hard harness + iterative repair |

#### 先用四代生成范式定位它们

| 阶段 | 代表工作 | 生成的随机变量 / 表示 | 真正的生成机制 | 关键缺口 |
| --- | --- | --- | --- | --- |
| 程序解析与 sequence latent | CSGNet、DeepCAD | CSG 树；CAD command history 或其 latent | RNN 解码；latent-GAN + Transformer 解码 | 操作空间窄，难表达完整设计意图 |
| 分解且可控的参数化生成 | Vitruvion、SkexGen、Text2CAD | primitive/constraint；拓扑/几何/拉伸码；文本条件 history | 两阶段自回归；VQ codebook + prior；cross-attended decoder | 多数仍是受限的 sketch-and-extrude 语言 |
| 直接几何与运动结构生成／重建 | BrepGen、NAP、URDF-Anything | B-Rep 树；part-joint 图；观测条件 URDF | 层次扩散；图扩散；3D MLLM 自回归 | 不天然保留可编辑的 feature history，或强依赖观测 |
| LLM 程序合成与执行闭环 | Arko-T、CADSmith、FutureCAD、Articraft | CAD / articulated-asset 程序及其运行时状态 | 微调 seq2seq；agentic repair；B-Rep grounding；SDK + harness | 可靠性取决于 kernel、grounding 与测试覆盖 |

阅读下面各段时，优先回答五件事：**它生成什么变量？如何 factorize？用什么网络 / 采样方式？何时调用执行器？输出究竟能否编辑、验证或仿真？** 这样才能把“方法名”变成可比较的技术链路。

#### 1. CSGNet

**技术链路：形状（2D 图像或体素）→ CNN 编码 → RNN 逐 token 解码 → CSG 程序执行。** CSGNet 的目标是**逆向解析**给定形状，而不是从无条件噪声采样形状：CNN 将输入形状压成特征，RNN 以 top-down 方式依次预测“画什么 primitive、其离散参数是什么、与已有子树做 union / subtract / intersect、何时停止”，从而生成一棵后序的 CSG 程序树；执行该程序即可复原形状。训练可直接使用合成的程序—形状对；没有程序标注时，则执行预测程序，用 IoU 类 reward 做 policy gradient。它的重要性是把“神经网络输出形状”转为“网络输出可执行程序”，但 primitive 库及参数是离散而有限的，且没有草图约束、特征引用或工业 B-Rep 语义。[论文](https://arxiv.org/abs/1712.08290)

#### 2. DeepCAD

**技术链路：CAD history → command / parameter token → Transformer 自编码器 → 连续 latent → latent-GAN 采样 → Transformer 解码为 history。** 它将 Fusion 360 的建模历史规范成 sketch、line/arc/circle、extrude 等命令序列：命令类型和量化后的参数分别嵌入，Transformer encoder 把变长序列压为一个 design latent，Transformer decoder 再自回归重建每个命令与参数。完成自编码训练后，论文在 latent 空间训练 GAN 来拟合设计分布；随机采样 latent 后经 decoder 得到可由 CAD kernel 重放的 construction sequence。因而 DeepCAD 的“生成器”不是直接对 token 逐步无条件采样，而是 **GAN 先产生全局 latent、Transformer 再展开历史**。其代价是操作集合以 sketch-and-extrude 为主，参数离散化，复杂 feature reference 与约束语义仍很有限。[论文](https://arxiv.org/abs/2105.09492)

#### 3. Vitruvion

**技术链路：可选的图像／草图前缀 → primitive Transformer → primitive 序列；再以该序列为条件 → constraint Transformer → 约束序列 → CAD solver。** 它把参数化草图严格分解为两步：第一个自回归 Transformer 生成线、圆、圆弧等 primitive 及初始坐标；第二个自回归模型在已生成 primitive 的索引上预测约束类型与引用对象，例如 parallel、tangent、coincident 和尺寸约束。最后将 `(primitives, constraints)` 交给常规草图求解器，而不是让网络直接回归最终几何；因此可通过已有的 CAD 约束图导入、求解和编辑。这个 factorization 解释了它为何是 design intent 的代表：网络既要画出几何，还要指出“哪些几何之间应保持何种关系”。它能做图片条件化、前缀补全和 autoconstrain，但不覆盖 3D feature history。[项目页](https://lips.cs.princeton.edu/vitruvion/)

#### 4. SkexGen

**技术链路：construction sequence → 三个 Transformer encoder + VQ codebook → code-prior 选码 → 三个自回归 decoder → sketch-and-extrude sequence。** SkexGen 并不是把 topo、geometry、extrude 标签直接拼接再预测：它把草图的**拓扑**与**几何**分别编码、量化到两个 disentangled codebook，把 extrusion 与布尔实体操作编码到第三个 codebook；各分支 decoder 在给定相应 code 的条件下自回归生成自己的子序列。随后另一个自回归 Transformer 学习三类量化 code 的有效组合；无条件生成时先从这个 prior 采样 code，再分别解码，编辑时可固定 topology code、替换 geometry 或 extrusion code，以保持某一因素不变。两条分支（sketch 与 extrude）独立训练，这正是它获得可控设计探索的机制，而非普通单一 latent 的 sequence VAE。[项目页](https://samxuxiang.github.io/skexgen/)

#### 5. Text2CAD

**技术链路：文本 prompt → 预训练 BERT + adaptive layer → cross-attended Transformer decoder → 自回归 CAD 子序列 → kernel 重放。** 该工作沿用 DeepCAD 风格的顺序 CAD 表示，但将文本作为条件：BERT 编码 prompt，经过可训练的 adaptive layer 后输入 decoder；decoder 在已生成的 CAD token 前缀和文本特征的共同条件下逐步预测下一个 sketch / extrusion token，直至 stop。其关键工程前提是数据：先由 LLaVA-NeXT 生成形状描述，再由 Mixtral-50B 生成从 beginner 到 expert 的多粒度操作描述，为约 17 万 DeepCAD 模型配对约 66 万文本。换言之，它不是“LLM 直接写 CadQuery”，而是**文本条件的、受限 CAD token language 自回归模型**；输出可参数化重放，但能力边界受 DeepCAD 的 token 化操作空间和训练数据所限。[项目页](https://sadilkhan.github.io/text2cad-project/)

#### 6. BrepGen

**技术链路：B-Rep → structured latent geometry tree → 分层 Transformer diffusion 反演 → duplicate-node merge → B-Rep。** 它先把实体、face、edge、vertex 组织为层次树；每个节点存 primitive 的全局 bounding box 与由局部曲面／曲线编码器得到的几何 latent。难点在拓扑：共享 edge 或 vertex 在树中被**重复复制**，使不规则图拓扑转化为更适合生成的树结构。生成时不是一次性输出邻接矩阵，而是从 root 向 leaf 依次由 Transformer diffusion 反向去噪各层节点特征，并检测、合并相同的复制节点来恢复共享关系。结果可以包含自由曲面与双曲率面，直接输出 B-Rep；但它产生的是最终边界及拓扑，不产生“先画哪张草图、为何该边被倒角”的 feature history，因此不能替代 history-first 设计程序。[论文](https://arxiv.org/abs/2401.15563)

#### 7. NAP

**技术链路：articulated object → 补齐到固定大小完全图 → forward diffusion → Graph Denoiser 反向去噪 → 最小生成树抽取 → SDF 解码 / URDF。** NAP 将每个刚体 part 表成节点属性 `[存在标志、rest-pose、bbox 尺寸、shape latent]`，其中 shape latent 由预训练 SDF decoder 解出零件表面；每个关节边存存在标志、以 Plücker 坐标表示的轴线、平移/旋转范围等，并假定无运动闭环的树与 screw joint。为处理不同零件数，它将对象 padding 成至多 `K` 个节点的**完全图**，在节点与边属性上加噪；生成从随机完整图开始，graph denoising network 在每一步让节点与边消息交互、联合预测干净的几何和运动结构。去噪结束后再依据边置信度运行 minimum-spanning-tree，抽出有效的运动学树并解码部件几何。因此“图表示后怎么生成”的答案是：**图扩散，不是树自回归；MST 是生成后的结构抽取**。它能做 Part2Motion / Motion2Part 等条件补全，但原文也承认未硬性保证无自碰撞或可直接物理仿真。[论文](https://proceedings.neurips.cc/paper_files/paper/2023/file/655846cc914cb7ff977a1ada40866441-Paper-Conference.pdf)

#### 8. URDF-Anything

**技术链路：单／多视图观测 → 点云 + 指令文本 → 3D MLLM 自回归输出 `[SEG]` 与关节 token → part masks + kinematic JSON → URDF。** 它不是 NAP 式从先验采样完整对象，而是一个端到端的 reconstruction 模型：视觉观测先形成点云，文本指令与点云特征共同输入 3D 多模态语言模型；模型自回归预测零件与运动学描述。专用 `[SEG]` token 与点云特征直接交互，产生细粒度 part segmentation，同时关节类型、轴、origin/limit 等参数在同一生成过程被预测，以减少“分割是一套系统、关节是另一套系统”造成的不一致。最后根据分割后的视觉几何及运动学参数装配 URDF，供仿真器执行。它的核心贡献是**观测条件下联合分割—运动学推断**，而不是从文字重新设计 B-Rep/CAD 程序；几何质量也受输入观测可见性与分割质量制约。[论文](https://arxiv.org/abs/2511.00940)

#### 9. Arko-T

**技术链路：单零件文本 → 4B 微调 Transformer → Build123d 参数化程序 → CAD kernel 执行 → editable design state。** Arko-T 将目标从“代码能跑”提高到“设计状态可编辑”：其输出程序必须显式保留命名参数、feature、构造次序和可检查的实体。模型以 Qwen3.5-4B 初始化，使用约 130 万条 `(prompt, Build123d program)` 对；数据一半由既有 CAD construction sequence 转换而来、一半来自合成/程序数据，并经代码归一化以暴露参数与 construction logic。训练分两阶段：先做监督微调建立文本到程序能力，再引入 execution-grounded supervision，利用 kernel 是否产出有效实体及设计状态检查来约束学习。推理仍是**单次 seq2seq 程序生成后执行**，没有 CADSmith 那样把失败反馈交回 agent 的外部修复循环；它的贡献是以专门训练和设计状态定义提升可编辑性。[论文](https://arxiv.org/abs/2606.30429)

#### 10. CADSmith

**技术链路：prompt → Planner JSON spec → RAG-augmented Coder 生成 CadQuery → sandbox Executor → 内外两层修复循环。** Planner 先抽取部件、尺寸、约束等结构化规格；Coder 从 CadQuery API 文档和示例的检索上下文生成 Python。若执行器报 API/几何异常，Error Refiner 带着 traceback 与错误模式库在**内环**修代码；代码能跑后，Executor 从 OpenCASCADE 提取 bbox、体积、面/边/顶点数与 solid validity，并生成三视图。独立的 VLM Judge 将 prompt、代码、kernel 精确量测和渲染一起判断；几何或视觉规格不符时，Refiner 依据其结构化反馈进入**外环**重构。重点是 kernel 度量负责毫米级可验证性、VLM 负责全局形态，两者互补；但这仍是有限轮数的 agentic search，验证信号不完备时可能接受“尺寸对但结构仍错”的近似解。[论文](https://arxiv.org/abs/2603.26512)

#### 11. FutureCAD

**技术链路：文本 → SFT+RL LLM 生成 CadQuery feature program 与文字 query → transient B-Rep + query → BRepGround → 目标 face/edge → kernel 执行下一 feature。** 它面对的不是一般的文本到代码，而是 fillet、chamfer、shell 等操作必须引用“此时此刻 B-Rep 的哪条边/哪个面”。LLM 在程序中不硬写脆弱的 entity ID，而生成如“顶部圆柱面与侧壁相交的环形边”这样的查询；每步 feature 执行前，BRepGround 用 BERT 编码查询、用 UV-Net 编码 transient B-Rep 的 face/edge（分别采样为 2D/1D UV grid），再以 Transformer 融合并选出目标 primitive，交还 kernel。训练包含约 14 万真实 CAD 模型、SFT 获得基础程序能力，再以 RL 改善泛化与程序有效率。因而它真正连接了 history-first 与 B-Rep-first：**程序生成决策 feature，grounding 模块在瞬时 B-Rep 上解析引用。** [论文](https://arxiv.org/abs/2603.11831)

#### 12. Articraft

**技术链路：文本 spec → LLM 编写 `model.py`（SDK）→ Harness 编译/运行/探测 → 结构化失败反馈 → edit–execute–repair。** Articraft 不训练一个端到端的关节图生成器，而是把资产创建改写成受限环境中的程序合成：领域 SDK 提供 part 定义、几何组合、joint 声明与 test authoring 等高层原语，使 LLM 不必手写 URDF 或管理复杂依赖。Harness 在受限 workspace 执行代码，导出并检查对象，运行硬性探测／测试，再把可操作的错误反馈给 LLM 迭代修改；因此 agent 输出的并非一次性 mesh 或关节 JSON，而是一段**可复现的资产构建程序 + 测试**。该系统被用于构建跨 245 类、超过 10K 个资产的 Articraft-10K；它比 NAP 更强调可执行与验证，比 CADSmith 多出 part-joint 语义与面向可动资产的测试，但质量仍受 SDK 表达力、测试覆盖率与 agent 修复能力限制。[论文](https://arxiv.org/abs/2605.15187)

这 12 篇是你的**骨头**。

其它论文全往骨头上挂。

比如老板突然：

> DualBrep？

你：

> “BrepGen 那条 direct B-Rep generation 线的更新工作，geometry/topology generation，不是 design-history agent。”

老板：

> SPARK？

你：

> “URDF-Anything 那条 observation-to-articulated-asset 线，单图恢复 part geometry + articulation，更偏 sim-ready reconstruction。”

老板：

> ArtiCAD？

你：

> “Articraft/LAM 相邻的 code-first articulated generation，但核心思想是 connector-first assembly planning。”

你就开始有“专家感”了。

### 五组最容易混淆的区别

这是我认为你下次汇报前最值得训练的。

#### DeepCAD vs. Text2CAD

```text
DeepCAD：学 CAD sequence representation
Text2CAD：language-conditioned CAD sequence generation
```

#### Text2CAD vs. BrepGen

```text
Text2CAD：history-first
BrepGen：B-Rep-first
```

#### Arko-T vs. CADSmith

```text
Arko-T：训练更懂 CAD 的 generator
CADSmith：执行反馈驱动的 agent
```

#### CADSmith vs. Articraft

```text
CADSmith：static CAD
Articraft：articulated asset + SDK/tests
```

#### URDF-Anything vs. Articraft

```text
URDF-Anything：
real observation → recover articulation

Articraft：
language/spec → synthesize new articulated asset
```

这五组你能稳定说出来，你已经不会显得“论文名字全混在一起”。

### 阅读与记忆模板

以后每看到一篇论文，**只记录六个问题**：

```text
1. Input 是什么？
2. Output 到底是什么表示？
3. 它解决的是哪一层？
4. 是 generator 还是 agent？
5. feedback 来自哪里？
6. 它相对哪篇前驱多做了一步？
```

比如 CADSmith：

```text
Input:
text

Output:
CadQuery program / CAD solid

Layer:
program + kernel validation

Generator or agent:
agent

Feedback:
execution + OCCT geometry + VLM render

Previous step:
Text2CAD / code generation

New step:
execute → validate → repair
```

**这样一篇论文只占你脑子六个 slot。**

而不是记十页 architecture。

### 结语：用压缩框架取代论文堆叠

你不是“没有调研懂”，而是把太多信息交给 AI 扩充后，还没有完成属于自己的压缩。现在要做的就是 compression。

下一轮最适合直接进入**口试模式**：我可以像你老板一样连续扔论文名和问题，比如“BrepGen 和 Text2CAD 为什么不是竞争关系？”“为什么 Articraft 还需要 MuJoCo？”“FutureCAD 到底 ground 什么？”——你先答，我再把你的回答修成真正能在汇报里脱口而出的版本。
