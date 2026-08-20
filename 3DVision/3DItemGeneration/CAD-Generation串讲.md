下面我按你这份《文生CAD\_曲面生成\_Articulated\_统一时间轴与方向对比.md》的骨架，结合联网核验到的最新信息，把整个大领域按时间顺序讲一遍。讲解会尽量"一点一点"推进，每个阶段先讲"当时大家在解决什么问题"，再讲"出现了什么代表工作"，最后讲"这条线后来留下了什么"。

---

## 0. 先建立一个总框架：这不是一条线，而是三条线汇成一条河

你文档里的核心判断，用一句话说就是：

> 这个领域的研究对象从"形状" → "CAD 程序/结构" → "可执行、可验证的资产系统"。

三条线分别是：

1. **静态 CAD（主线 A）**：输出 CSG、sketch-extrude、B-Rep、STEP、CadQuery/Build123d 程序，解决"可编辑、可制造的 CAD 实体"问题。
2. **曲面/mesh 几何生成（主线 C）**：输出 SDF、NURBS、B-spline、mesh、PBR 资产，解决"复杂、光滑、高保真几何怎么表达和生成"的问题。
3. **Articulated object（主线 B）**：输出 part/link、joint、axis、limit、URDF，解决"能运动、能装配、能仿真"的问题。

它们的关系可以画成一条竖向栈：

```text
CAD program / history
      ↓ kernel 执行
B-Rep topology
      ↓ face geometry
NURBS / analytic surface / mesh
      ↓ assembly semantics
parts + connectors + joints + URDF
```

这意味着：**曲面生成是几何层，B-Rep 是静态 CAD 与曲面的交叉层，URDF/joint schema 是 articulated 层，而 CAD kernel 是程序层与几何层之间的执行接口。** 后面 2026 年的所有变化，几乎都是在补全这条栈。

---

## 1. 2017–2021：表示学习时代——"怎么表示一个形状"

这是整个领域的底座期。核心问题不是"文生 CAD"，而是：

> 一个三维形状，用什么数据结构表示，才能被神经网络学习？

### 1.1 曲面线：隐式 vs 显式

- **SurfNet（CVPR 2017）**：早期显式曲面生成，直接学 surface。
- **DeepSDF（CVPR 2019）**：把形状表示成连续 signed distance field（SDF），奠定了"隐式连续曲面"这一支。你文档里记录它的引用量约 4711，是这个时期影响力最大的工作之一。
- **ParSeNet（CVPR 2020）**：从点云拟合平面、圆柱、B-spline 等参数面，开始把"曲面"和"参数化 CAD 面"连起来。
- **Neural Splines（CVPR 2021）** 与 **NURBS-Diff（CAD 2022）**：一个把神经网络和样条拟合结合，一个让 NURBS 变得可微。这两篇说明：曲面开始从"视觉上的 mesh"转向"可优化、可进入 CAD 的参数曲面"。

这个阶段的成果**普遍没有 CAD history、制造意图或装配语义**——它们解决的是几何表达问题，不是设计问题。

### 1.2 静态 CAD 线：CSG 与 sketch-extrude 程序

- **CSGNet（CVPR 2018）**：图像/体素 → CSG program，用 CNN+RNN 自回归预测 primitive 和 Boolean 操作。它最早把"形状"表达成"可解释的 Boolean 程序"。
- **UCSG-Net（NeurIPS 2020）**：无监督、可微地重建 CSG tree。
- **Sketch2CAD（SIGGRAPH Asia 2020）**：人在环的草图 → CAD operation，把 feature-level 编辑引入 CAD 生成。
- **DeepCAD（ICCV 2021）**：把 CAD construction sequence 做成大规模表示学习任务，发布数据集。它相当于给后来的"文生 CAD"提供了语言和语料。

这一阶段的关键突破是：**几何被压缩成 primitive、Boolean、sketch、constraint、CAD sequence，设计意图第一次成为可学习的对象。**

---

## 2. 2022–2024：结构化 CAD 与 B-Rep 交叉——"几何 + 拓扑 + 设计意图"

这是三条线真正开始交汇的阶段。研究偏好从"怎么表示形状"变成"怎么同时恢复 geometry 与 topology/constraint"。

### 2.1 静态 CAD：history-first 与 B-Rep-first 分流

- **Vitruvion（ICLR 2022）**：把 2D sketch 表达成 primitive + geometric constraint graph，再用 CAD solver 求解。强调"约束图"而非裸几何。
- **SkexGen（ICML 2022）**：把 sketch-extrude 序列解耦成 topology、geometry、extrusion 三个 codebook，让生成更可控。
- **SolidGen（TMLR 2023）**：不依赖 history，直接自回归生成 B-Rep 的 vertices、edges、faces。
- **SECAD-Net（CVPR 2023）**：不依赖 CAD history 标注，自监督地从 occupancy/体素重建 sketch-extrude。
- **BrepGen（SIGGRAPH 2024）**：hierarchical diffusion 生成 watertight B-Rep，支持 plane/cylinder/cone/sphere/torus/Bezier/NURBS 面。它是"直接生成工业 CAD 表示"的标志性工作。
- **Point2CAD（CVPR 2024 Spotlight）**：点云 → CAD B-Rep，做逆向工程。
- **TransCAD（ECCV 2024）**：点云 → loop-extrusion sequence，单阶段点云到 CAD history。
- **GenCAD（TMLR 2025）**、**Img2CAD（arXiv 2024）**：从图像生成 CAD commands 或 CAD B-Rep，开始强调"视觉条件 + 可执行 history"。
- **Text2CAD（NeurIPS 2024 Spotlight）**：文本 → CAD command sequence，把语言变成 CAD history 的条件。

到这里，静态 CAD 的路线已经分成两派：

```text
History-first：生成 sketch/extrude/Boolean，可编辑、可回放（DeepCAD/Text2CAD/GenCAD）
B-Rep-first：直接生成 vertices/edges/faces，几何自由但设计意图弱（SolidGen/BrepGen）
```

### 2.2 曲面线进入 B-Rep 与逆向 CAD

- **ComplexGen（SIGGRAPH 2022）**：点云 → B-Rep chain complex，恢复边、面和拓扑。
- **Surf-D（ECCV 2024）**：任意拓扑的曲面 diffusion 生成。
- **NeuroNURBS（arXiv 2024）**：专门学习 NURBS 曲面表示。

这一阶段最重要的变化是：曲面不再孤立，而是被放进 B-Rep 实体结构里，成为 `surface geometry + topology + entity references + CAD operation` 的一部分。

### 2.3 Articulated object：第一条正式时间线起点

- **NAP（NeurIPS 2023）**：第一次较系统地把 articulated object 表示成 **part geometry nodes + joint kinematic edges**，并用图扩散联合生成几何与运动结构。它的核心论点是：

> 几何和运动结构必须联合建模，不能先生成静态物体、再事后猜关节。

这篇论文不一定是最强的文生系统，但它是 articulated 方向"从 0 到 1"的表示层工作。联网核验可见官方页面：[NAP: Neural 3D Articulated Object Prior](https://proceedings.neurips.cc/paper_files/paper/2023/hash/655846cc914cb7ff977a1ada40866441-Abstract.html)。

- **Articulate-Anything（ICLR 2025）** 和 **ArtFormer（CVPR 2025）** 在 2024 年底/2025 年出现，分别走"VLM actor–critic + mesh retrieval"和"part tree + geometry latent + Transformer"路线，把 text/image/video 引入 articulated 生成。

---

## 3. 2025：多模态、高保真与 Flow Matching 入场

到了 2025 年，研究偏好明显变成：**怎样从真实或开放输入（图像、文本、视频、点云）得到完整资产**。

### 3.1 静态 mesh/PBR：Flow Matching 先在这里证明自己

- **TripoSG（arXiv 2025）**：SDF-VAE latent 上的大规模 Rectified Flow Transformer，从图像生成高保真 mesh，成为通用 shape prior 的代表。
- **TRELLIS.2（CVPR 2026）**：O-Voxel + compact VAE + 4B Conditional Flow Matching，图像 → PBR-textured 3D asset，支持任意拓扑与材质。

你文档里的判断很关键：**Flow Matching 不是第四条对象路线，它是一种连续几何采样方法**。它在 2025 年先证明能做 mesh/PBR，2026 年才进入 B-Rep 和 articulated。

### 3.2 曲面/B-Rep 生成继续加码

- **CADDreamer（CVPR 2025）**：单视图 → 可编辑曲面 CAD。
- **DTGBrepGen（CVPR 2025）**：拓扑与几何解耦生成 B-Rep。
- **HoLa（SIGGRAPH 2025）**：text/image/point/sketch 多模态 condition + holistic latent，生成 B-Rep。
- **BrepGPT（arXiv 2025）**：Voronoi half-patch 自回归 B-Rep。
- **AutoBrep（arXiv 2025）**：统一拓扑与几何的自回归 B-Rep。
- **NURBGen（AAAI 2026）**：Qwen3-4B LoRA，文本 → 面级 NURBS/analytic JSON → B-Rep。它代表"LLM 直接生成高保真曲面参数"的路线。
- **CAD-Tokenizer（ICLR 2026）**：为 CAD/曲面特征设计专用 tokenizer，解决"CAD 语言单元"问题。

### 3.3 Articulated：观测驱动 + URDF 接口

- **ATOP（arXiv 2025）**：静态分割 mesh + motion text → 关节运动参数，用多视图 motion evidence 让静态部件可动。
- **FreeArt3D（SIGGRAPH Asia 2025）**：multi-state RGB → textured articulated mesh，用 frozen TRELLIS 先验 + per-instance optimization。
- **URDF-Anything（NeurIPS 2025）**：point cloud + text → part masks + URDF，3D MLLM 自回归生成 link-joint JSON。这是"观测 → 运动学结构"的代表。
- **ArtiWorld（arXiv 2025）**：把 articulated object 放到场景级，scene + rigid assets → articulated scene。
- **ArticFlow（arXiv 2025）**：action-conditioned Flow Matching，生成 mechanism point sets 的形态与动作响应。
- **SPARK（CVPR 2026 Oral）**：单 RGB → part meshes + URDF，VLM 提供 part/joint guidance，Rectified Flow 共同生成 part mesh latents，再用 FK/render refine。这是"真实观测 → sim-ready URDF"的标志性工作，联网可核验：[SPARK CVPR 2026 Oral](https://cvpr.thecvf.com/virtual/2026/oral/40344)。

这一阶段 articated 的共同点是：**text/image/video/point cloud 作为运动和功能语义入口，URDF 作为最终仿真接口**。

---

## 4. 2026：Agentic CAD 与可信验证成为主线

这是你文档里最看重、也最值得你押注的阶段。核心变化是：

> 不再只预测一个 mesh 或序列，而是生成一个**可以被执行、检查、修复的程序系统**。

### 4.1 静态 CAD：程序生成 + kernel 验证

- **STEP-LLM（DATE 2026）**：文本 → STEP entities，DFS reserialization + RAG-SFT + GRPO，直接生成工业交换格式。
- **CADSmith（arXiv 2026）**：Planner/Coder/Executor/Validator/Refiner 多 agent，CadQuery + OpenCASCADE 几何验证。联网核验：[CADSmith arXiv](https://arxiv.org/abs/2603.26512)。
- **FutureCAD（arXiv 2026）**：文本 → CAD program + B-Rep primitive grounding，把 LLM 程序与 B-Rep primitive 语义对齐。
- **Zero-to-CAD（arXiv 2026）**：Autodesk 的大规模 agentic CAD synthesis，覆盖丰富 CAD 操作。
- **Arko-T（arXiv 2026）**：文本 → Build123d program → solid，结构化 design state + 执行过滤，保留参数化 construction intent。联网核验：[Arko-T arXiv](https://arxiv.org/abs/2606.30429)。

### 4.2 B-Rep：Flow Matching 正式进入拓扑+几何联合生成

- **Flatten The Complex（SIGGRAPH 2026）**：compositional k-cell particles + Rectified Flow Transformer，联合生成 vertices/edges/faces。联网核验：[Flatten The Complex](https://arxiv.org/abs/2601.17733)。
- **DualBrep（SIGGRAPH 2026）**：SDF+UDF dual fields + latent Flow Matching，neural rebuilder 显式化 watertight B-Rep/STEP。Autodesk 出品，联网核验：[DualBrep arXiv](https://arxiv.org/abs/2606.31579)。
- **B-repLer（SIGGRAPH 2026）**：source B-Rep + text → edited B-Rep，Flow Matching 做自由曲面 CAD 的生成式编辑。
- **BrepGaussian（arXiv 2026）**：multi-view → CAD，Gaussian Splatting + B-Rep 曲面重建。

这些工作说明：**Flow Matching 在 2026 年已经不是"mesh 生成器"，而是进入 B-Rep 的 geometry-topology 联合生成。**

### 4.3 Articulated：从"预测关节"变成"生成可验证的 CAD 装配程序"

这是和你研究方向最直接相关的一段，我讲细一点。

- **ArtLLM（CVPR 2026）**：point cloud → articulation blueprint → mesh。3D LLM 先联合预测 part/joint layout，再由 XPart 生成部件几何。
- **LAM（CVPR 2026）**：text → link hierarchy + geometry/joint code。Link Designer、Geometry/Articulation Coder、VLM Checker/Fixer，渲染和运动序列做视觉自修复。
- **ArtiCAD（arXiv 2026）**：text/image → FreeCAD parts + typed joints + URDF。Design/Generation/Assembly/Review 多 agent，Connector contract 先规划装配关系再生成零件。联网核验：[ArtiCAD arXiv](https://arxiv.org/abs/2604.10992)。
- **Articraft（arXiv 2026）**：text/image → model.py + mesh/URDF/tests。受限 SDK + compile/probe/test harness + LLM repair，强调低成本、可批量、可信验证。联网核验：[Articraft arXiv](https://arxiv.org/abs/2605.15187)。

你文档里对这三家的对比很精炼，我转述一下：

| 工作      | 主要反馈                                       | 优势                                  | 局限                                  |
| --------- | ---------------------------------------------- | ------------------------------------- | ------------------------------------- |
| LAM       | render、motion sequence、VLM critique          | 文本到 geometry+articulation 统一生成 | 视觉检查仍可能不够精确                |
| ArtiCAD   | connector/frame、局部渲染、装配审查、rollback  | 先规划装配关系，再生成零件            | 多 agent 流程复杂，验证粒度需工程化   |
| Articraft | compile、geometry probe、object-specific tests | 受限 SDK、低成本、容易批量生成        | 视觉反馈较弱，复杂自由曲面受 SDK 限制 |

---

## 5. 把时间轴拉通后，你能看到的四个趋势

### 趋势 1：研究对象在迁移

```text
3D shape generation
   → CAD representation
   → CAD/URDF execution
   → simulation/manufacturing/robotics asset pipeline
```

### 趋势 2：表示在"结构化"

从 primitive、latent、mesh，逐渐变成 CAD sequence、STEP/B-Rep entity graph、NURBS/analytic JSON、Build123d/CadQuery/FreeCAD program、part/link/joint schema、connector/frame contract、URDF 与测试定义。**共同价值是：可执行、可检查、可编辑、可复用。**

### 趋势 3：生成范式在"系统化"

从"模型一次输出"变成：

```text
generate → compile/execute → measure/render/simulate → diagnose → repair
```

你文档里特别强调：**最有价值的不是 agent 数量，而是反馈是否可定位、不可被模型篡改、可以触发局部修复。**

### 趋势 4：Flow Matching 的角色在固定下来

它不替代 schema/program，而是成为**连续几何生成器**：TripoSG/TRELLIS.2 做 mesh/PBR，ArticFlow/SPARK 做 part/mechanism，Flatten The Complex/DualBrep/B-repLer 做 B-Rep 与自由曲面。

---

## 6. 对你 articulated CAD 方向的含义

按你文档的最终判断，最值得押注的不是"更大的模型直接生成一个 mesh"，而是：

> **结构化、可执行、可验证的 3D 生成：语言/图像/点云 → typed program/schema → CAD/URDF kernel → 几何/运动/物理验证 → 局部修复。**

曲面生成在这个体系里最好的位置是**几何专家层**：负责 NURBS、B-Rep faces、implicit surface 或 mesh 的表达与生成，但不独自承担设计意图、装配关系和运动学语义。

你现有的"最小可信 Harness"方案正好对应 2026 年的主线，建议的系统栈可以保持为：

```text
Spec / Connector / Joint Schema
      ↓
Part Geometry Generator
  (Build123d / CadQuery / NURBS / B-Rep / mesh)
      ↓
Assembly + URDF
      ↓
CAD kernel / collision / motion / physics harness
      ↓
Agent diagnosis + local repair
```

---

## 7. 如果需要"一点一点"继续读，我建议的顺序

按你文档第 10.3 节的连续阅读顺序，我可以下次再逐篇展开讲：

```text
DeepCAD
  → SkexGen
  → Text2CAD
  → TransCAD / Point2CAD
  → BrepGen / HoLa / NURBGen
  → TripoSG / SPARK / Flatten The Complex / DualBrep
  → NAP / ArtFormer
  → URDF-Anything / ArtLLM
  → CADSmith
  → LAM / ArtiCAD / Articraft
```

你想让我接着讲的话，可以选其中任意一段或任意一篇，例如：
- 讲透 **BrepGen / DualBrep / Flatten The Complex** 的 B-Rep 生成技术差异；
- 对比 **LAM / ArtiCAD / Articraft** 三个 agentic articulated 系统；
- 或者把 **SPARK** 作为"观测 → URDF"的范本详细拆解。