# Unified 3D Agent SDK / Skill / Harness 整合方案

> 版本：v1.0
> 目标：整合现有开源 3D generation SDK/Skill/Harness 成果，形成一个 **unified SDK + Skill 集 + 可信 Harness** 的 Agent 系统底座，同时支持静态 CAD 与 articulated 3D 资产生成。
> 前置文档：
> - 《CAD_Skill_SDK_调研总结.md》
> - 《文生CAD_曲面生成_Articulated_统一时间轴与方向对比.md》
> - 《基于最小可信Harnes的Multi-Agent_Articulated_Assets生成系统方案-v1.md》
> - 《3D生成模型评测验收协议.md》

---

## 1. 结论先行

**可复用的开源资产已经足够，不需要从零造轮子。** 正确姿势是：

```text
以 Articraft SDK（articulated 语义）为骨架
 + build123d/CadQuery（静态 CAD 几何）为肌肉
 + text-to-cad/agentcad（执行、测量、验证、预览工具）为神经末梢
 + 你已有的 Spec/Review/Coding/Diagnosis 多 Agent 方案为大脑
 + 你已有的 Harness（冻结 spec、采样、碰撞、MuJoCo、隐藏复核）为免疫系统
```

**四个直接复用建议（按优先级）：**
1. **Articraft 开源仓库**（Apache 2.0）：直接复用其 `RigidBodyAssembly / JointDOF / TestContext / compiler / agent harness / simulate`。这是目前唯一开源的 articulated SDK + harness 完整实现。
2. **text-to-cad 的 Skill + scripts 工具层**（MIT）：复用其 `gen / export / inspect / snapshot / artifact` 工具接口和 `cad / urdf / sdf / dxf / step-parts / cad-viewer` Skill 组织方式。
3. **agentcad**（Apache 2.0）：复用其 `run / measure / check-spec / inspect / diff / parts / view` CLI + MCP 作为静态 CAD 的测量与验证工具。
4. **LAM 开源仓库**（Apache 2.0）：复用其多 Agent 划分（Shape Generator / Articulation Coder / VLM Critic / Fixer）与 VLM 视觉检查的 prompt 设计。

---

## 2. 开源可复用资产盘点（2026-08 联网核实）

### 2.1 可直接复用的 Agentic 成果

| 项目 | 仓库 | License | Stars | 可复用内容 | 复用位置 |
|---|---|---|---|---|---|
| **Articraft** | [articraftresearch/Articraft](https://github.com/articraftresearch/Articraft) | Apache 2.0 | 73 | articulated SDK（RigidBodyAssembly/JointDOF/TestContext）、compiler（编译+QC反馈）、agent harness（受限 workspace/tools/repair loop）、USDZ 导出、simulate | 核心骨架：SDK + Harness |
| **LAM** | [gaoypeng/LAM](https://github.com/gaoypeng/LAM) | Apache 2.0 | 6 | 多 Agent 代码（linker/shape/articulation generator + vlm_critic + fixer + feedback fusion）、URDF grid visualizer、LAMBench 数据管线 | 视觉检查 Agent 与修复循环 |
| **CADSmith** | [jabarkle/CADSmith](https://github.com/jabarkle/CADSmith) | 无 license | 29 | Planner/Coder/Executor/Validator/Refiner 五 Agent、OCCT 几何测量、VLM Judge 三视图审查 | 静态 CAD 验证与修复参考 |
| **Articulate-Anything** | [vlongle/articulate-anything](https://github.com/vlongle/articulate-anything) | 无 license | 213 | mesh retrieval + VLM actor-critic + link placement/joint prediction 代码 | 检索式关节化的参考实现 |
| **FutureCAD** | [JohanStackk/FutureCAD](https://github.com/JohanStackk/FutureCAD) | 无 license | 8 | LLM 程序生成 + B-Rep primitive grounding 的 code/dataset | 静态 CAD 程序生成的参考 |
| **Zero-to-CAD** | [ADSKAILab/Zero-To-CAD-1m](https://huggingface.co/ADSKAILab/Zero-To-CAD-1m) | Apache 2.0（数据集） | — | 百万级 CAD 程序合成数据集 + Qwen3-VL 模型 | 训练/微调底座模型 |

### 2.2 可直接复用的 Skill / CLI / Harness 工具

| 项目 | 仓库 | License | 可复用内容 | 复用位置 |
|---|---|---|---|---|
| **text-to-cad** | [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) | MIT | `skills/`（cad, urdf, sdf, srdf, dxf, step-parts, cad-viewer, gcode, implicit-cad, sendcutsend, bambu-labs）；每个 skill 自带 `scripts/`（gen/export/inspect/snapshot/artifact）工具层 | Skill 组织方式 + 工具接口设计 |
| **agentcad** | [jdilla1277/agentcad](https://github.com/jdilla1277/agentcad) | Apache 2.0 | `run/measure/check-spec/inspect/diff/parts/view` CLI + MCP server + viewer.html | 静态 CAD 测量/验证/可视化工具 |
| **CLI-Anything FreeCAD** | [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) | Apache 2.0 | 258 个 FreeCAD 命令的 CLI/MCP harness | 需要 FreeCAD 特征树/复杂装配时 |
| **PartCAD** | [openvmp/partcad](https://github.com/openvmp/partcad) | Apache 2.0 | 组件/装配/物料管理、STEP 包管理 | 标准件库与装配版本管理 |
| **OpenSCAD MCP** | [fboldo/openscad-mcp-server](https://github.com/fboldo/openscad-mcp-server) | MIT | SCAD → PNG → 批评 → 修改 迭代闭环 | CSG 类简单件的视觉反馈闭环 |
| **agent3dify** | [neka-nat/agent3dify](https://github.com/neka-nat/agent3dify) | — | CadQuery Builder 子 Agent（图像→CadQuery + 渲染验证器） | 图像条件 CAD 参考 |

### 2.3 底层建模 SDK

| SDK | 定位 | 在统一架构中的角色 |
|---|---|---|
| **build123d** | Python 参数化 B-Rep（OCCT） | 默认几何底座（Articraft、text-to-cad、agentcad 均已采用） |
| **CadQuery** | Python 参数化 CAD | 兼容模式 + 论文复现 |
| **FreeCAD Python API** | 完整 CAD 应用 | 企业/特征树场景 |
| **OpenSCAD** | CSG DSL | 简单规则件 |
| **ezdxf** | 2D DXF | 激光/CNC 图纸 |

### 2.4 关键结论

- **ArtiCAD 未发现开源代码**（只有项目页），其 Connector-first 思想需要自己实现。
- **CADSmith 无 license**，只能参考架构，不能直接复制代码。
- **Articulate-Anything 无 license**，同样只能参考。
- **Articraft / LAM / agentcad / text-to-cad / PartCAD / CLI-Anything 都是 Apache 2.0 或 MIT**，可以安全复用与再发布。

---

## 3. 目标系统：Unified 3D Agent 架构

### 3.1 总架构图

```text
用户输入（文本 / 参考图 / 点云 / 场景）
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  Agent 层（多 Agent，按职责划分，吸收 LAM/ArtiCAD/CADSmith）    │
│                                                         │
│  Spec Agent ──→ Spec Review/Test Design Agent            │
│      │                  │                               │
│      ▼                  ▼                               │
│  Coding Agent ──→ Harness（执行与验证）                   │
│      │                  │                               │
│      └── 诊断 Agent（多轮失败时触发）                      │
└─────────────────────────────────────────────────────────┘
        │ 工具调用（只通过 Harness 暴露的受限接口）
        ▼
┌─────────────────────────────────────────────────────────┐
│  Unified Skill 层（面向 Agent 的领域知识包）                │
│                                                         │
│  cad / articulated / urdf / sdf / mesh / dxf /           │
│  step-parts / cad-viewer / inspect / repair              │
└─────────────────────────────────────────────────────────┘
        │ 每个 Skill 定义：能做什么、怎么做、怎么验收
        ▼
┌─────────────────────────────────────────────────────────┐
│  Unified SDK 层（程序化建模接口）                         │
│                                                         │
│  ┌────────────────────────────┐  ┌──────────────────┐   │
│  │ Geometry SDK               │  │ Assembly/Joint    │   │
│  │ (build123d / CadQuery /    │  │ SDK（RigidBody /  │   │
│  │  MeshGeometry / NURBS)     │  │  Connector / URDF)│   │
│  └────────────────────────────┘  └──────────────────┘   │
│  ┌────────────────────────────┐  ┌──────────────────┐   │
│  │ Test/Probe SDK             │  │ Export SDK        │   │
│  │ (TestContext / expect_*)   │  │ (STEP/USDZ/URDF/  │   │
│  │                            │  │  GLB/STL/3MF)     │   │
│  └────────────────────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  Harness 层（可信执行）                                   │
│                                                         │
│  受限 workspace · 编译 · 测量 · 检查 · 渲染 · 仿真 ·      │
│  冻结 spec/tests · 采样/最坏姿态搜索 · 隐藏复核 · 日志      │
│                                                         │
│  实现来源：Articraft compiler + agentcad measure/inspect  │
│           + text-to-cad scripts + 自研物理/隐藏复核       │
└─────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  内核与运行时                                           │
│  OCCT/OCP（B-Rep 内核） · build123d/CadQuery ·          │
│  MuJoCo/SAPIEN/Isaac（物理） · OpenUSD/trimesh/open3d    │
└─────────────────────────────────────────────────────────┘
        │
        ▼
输出资产包：STEP / USDZ / URDF / mesh / tests / trace / manifest
```

### 3.2 分层职责（吸收你现有方案的边界）

| 层 | 职责 | 可以做什么 | 不可以做什么 |
|---|---|---|---|
| Agent 层 | 规划、写 spec、写代码、诊断 | 修改 spec/code，提议测试 | 不直接碰文件系统、不决定最终通过 |
| Skill 层 | 领域知识 | 定义工作流、验收清单、参考文档 | 不执行代码 |
| SDK 层 | 程序化建模接口 | 被 Agent 写的代码 import | 不主动运行 |
| Harness 层 | 可信执行与验证 | 编译、测量、采样、仿真、冻结、复核、发布 | 不参与设计决策 |

---

## 4. Unified SDK 设计

### 4.1 设计原则

1. **单一几何底座**：默认 build123d（OCCT B-Rep），CadQuery 作为兼容模式。
2. **articulated 语义一等公民**：吸收 Articraft SDK 的 `RigidBodyAssembly / rigid_body / joint / articulation` 设计。
3. **静态与 articulated 共用同一几何内核**：静态零件就是没有 joint 的 articulated 对象。
4. **Connector 合约**：吸收 ArtiCAD 思想，在 SDK 中提供 `Connector`（带命名、局部坐标系、语义标签、joint 参数），让"先规划装配关系，再生成几何"成为 SDK 原生能力。
5. **测试即代码**：吸收 Articraft `TestContext` + 你方案里的声明式测试定义，SDK 同时支持代码式测试（`ctx.expect_gap(...)`）和声明式测试（由 Harness 展开）。
6. **导出与建模解耦**：`export_*` 独立 import（Articraft 的做法），避免加载 OpenUSD 拖慢建模循环。

### 4.2 SDK 模块清单

```text
unified3d/
├── geometry/                     # 几何底座
│   ├── solids.py                 # build123d 封装（Box/Cylinder/... + 通用 helpers）
│   ├── mesh.py                   # MeshGeometry（三角网格 + 布尔/扫掠/放样/壳体）
│   └── nurbs.py                  # NURBS 曲面（复用 build123d/NURBGen 思路，预留）
├── assembly/                     # 装配与关节
│   ├── rigid_body.py             # RigidBody / RigidBodyAssembly（吸收 Articraft）
│   ├── connector.py              # Connector 合约（吸收 ArtiCAD）
│   ├── joint.py                  # JointDOF / JointAxis / limits
│   └── articulation.py           # articulation tree（根/闭链/omitted closing joint）
├── testing/                      # 测试与探针
│   ├── test_context.py           # TestContext：distance/overlap/support/pose/motion
│   ├── expect.py                 # expect_gap/expect_within/expect_overlap/allow_overlap
│   └── probes.py                 # probe_model：nearest_neighbors/containment/distance 测量
├── export/                       # 导出
│   ├── step_export.py            # STEP（静态 CAD 主工件）
│   ├── usdz_export.py            # USDZ（articulated 可动预览，吸收 Articraft）
│   ├── urdf_export.py            # URDF（仿真接口，含 inertial/collision）
│   ├── mesh_export.py            # STL/3MF/GLB/OBJ
│   └── manifest.py               # manifest.json（单位/坐标系/版本/hash）
├── validate/                     # 验证
│   ├── geometry_validator.py     # B-Rep 合法、水密、自相交、尺寸/体积/拓扑
│   ├── assembly_validator.py     # connector frame 一致、joint 参数合法
│   └── physics_validator.py      # 碰撞、间隙、接触、包含、稳定性（MuJoCo）
└── materials/                    # 材质与质量
    ├── material.py
    └── inertial.py
```

### 4.3 核心 API 草图（统一 static + articulated）

```python
# 静态零件：无 joint 的 assembly
from unified3d import Assembly, Connector, JointDOF, JointAxis, TestContext

m = Assembly("hinge_bracket")
base = m.rigid_body("base")
base.add(Box(0.08, 0.05, 0.01), name="plate")

# Connector 合约：先声明连接关系（ArtiCAD 思想）
conn = Connector(
    name="hinge_mount",
    frame=base.at((0.04, 0.0, 0.005)),
    semantic="hinge",
    joint_dofs=(JointDOF(JointAxis.ROT_Z, limits=(0.0, 1.57)),),
)

# articulated：joint 连接两个 body（Articraft 思想）
lid = m.rigid_body("lid")
lid.add(Box(0.08, 0.05, 0.005), name="panel")
m.joint("base_to_lid", conn.frame, lid.at(), dofs=conn.joint_dofs)
m.articulation("main", root="base", joints=["base_to_lid"])

# 测试
m.validate()
ctx = TestContext(m)
ctx.expect_gap("lid.edge", "base.edge", within=(0.0, 0.001))
report = ctx.report()
assert report.passed
```

---

## 5. Unified Skill 集设计

### 5.1 Skill 划分

按"领域能力"而非"软件"划分。每个 Skill 一个目录，含 `SKILL.md`（工作流+验收）+ `references/`（参考）+ 可选 `scripts/`（工具）。

| Skill | 职责 | 复用来源 |
|---|---|---|
| **cad** | 静态 CAD 生成与验证（STEP-first） | text-to-cad cad + agentcad |
| **articulated** | articulated 资产生成（SDK 的 part/joint/test 工作流） | Articraft SDK + LAM agents |
| **urdf** | URDF/SDF/SRDF 机器人描述文件 | text-to-cad urdf/sdf/srdf |
| **mesh** | mesh 生成与修复（程序化 mesh、水密化、简化） | Articraft mesh + trimesh/open3d |
| **dxf** | 2D 图纸/切割文件 | text-to-cad dxf + ezdxf |
| **step-parts** | 标准件检索（螺钉/轴承/电机） | text-to-cad step-parts + PartCAD |
| **cad-viewer** | 本地可视化审查（A/B、多视图、运动 keyframe） | text-to-cad cad-viewer + agentcad viewer |
| **inspect** | 测量、check-spec、diff、几何验证 | agentcad + text-to-cad inspect |
| **repair** | 修复循环（普通修复→诊断→回滚） | LAM fixer + CADSmith refiner + 你方案 |
| **simulate** | 物理仿真与稳定性 | Articraft simulate + MuJoCo |

### 5.2 每个 SKILL.md 的固定结构

```markdown
---
name: xxx
description: ...
---
# 目标
# 何时使用 / 何时不使用
# 默认假设（单位、坐标、输出格式）
# 必需工作流（步骤化，含验证关卡）
# 非协商项（Non-negotiables）
# 参考文档（progressive references，按需加载）
# 报告格式
```

这套结构直接复用 text-to-cad 的 SKILL.md 格式，它已经被验证适合 coding agent。

---

## 6. Unified Harness 设计

### 6.1 Harness 工具接口（受限 action space）

吸收 Articraft 的受限 workspace + text-to-cad/agentcad 的工具接口 + 你方案的冻结/复核机制：

| 工具 | 类型 | 作用 | 实现来源 |
|---|---|---|---|
| `read_file` | 只读 | 读模型代码/SDK 文档 | Articraft |
| `apply_patch` / `replace` / `write_file` | 编辑 | 修改模型代码 | Articraft |
| `find_examples` | 只读 | 检索示例片段 | Articraft |
| `compile` | 执行 | 执行代码，返回 failures/warnings/notes | Articraft compiler |
| `measure` | 执行 | 尺寸/体积/拓扑/特征测量 | agentcad measure |
| `check_spec` | 执行 | 对照 spec.json 逐项验收 | agentcad check-spec + 你方案的声明式测试 |
| `probe` | 执行 | 几何探针（距离/重叠/包含/姿态） | Articraft probe |
| `snapshot` | 执行 | 多视图/运动 keyframe 渲染 | text-to-cad snapshot + agentcad render |
| `simulate` | 执行 | MuJoCo/Isaac 物理测试（碰撞/稳定/接触/间隙） | 你方案 Harness + Articraft simulate |
| `diff` | 执行 | 版本对比 | agentcad diff |
| `inspect` | 执行 | 拓扑深检（壳体/自由边/合法性） | agentcad inspect |
| `view` | 执行 | 本地 viewer 审查 | agentcad view / Articraft viewer |

### 6.2 Harness 可信机制（你方案已有，保留并强化）

1. **冻结 spec 与测试**：Spec/Test 一旦冻结，Coding Agent 无权修改。
2. **采样计划归 Harness**：Agent 只能写"测什么"，Harness 决定"怎么充分测"（关键姿态、低差异采样、最坏姿态搜索）。
3. **连续运动碰撞检测**：全关节行程采样 + 连续碰撞检测。
4. **反例不可删除**：失败证据追加写，Agent 只读。
5. **隐藏复核**：公开测试全部通过后，Harness 用一组 Agent 不可见的隐藏测试复核；只有 Harness 能宣布通过。
6. **失败路由**：普通错误→Coding Agent；多轮失败→诊断 Agent；spec 问题→新 spec 版本完整重跑；测试可疑→隔离。

### 6.3 Harness 与开源工具的分工

| 能力 | 复用开源 | 自研 |
|---|---|---|
| 编译 + QC 反馈 | Articraft compiler | — |
| 几何测量/check-spec/diff | agentcad | — |
| 渲染/快照 | text-to-cad scripts + agentcad | — |
| 冻结/采样/最坏姿态/隐藏复核/权限 | — | 你方案 v1 的 Harness |
| 物理仿真 | Articraft simulate（MuJoCo） | 连续碰撞检测、自碰撞 |
| 诊断数据（多视角+点云+轨迹） | LAM 的 VLM critic 输入格式 | 诊断 Agent |

---

## 7. Agent 层整合：吸收 LAM / ArtiCAD / CADSmith 的划分

### 7.1 Agent 角色映射

| 你方案 v1 | 吸收来源 | 职责 |
|---|---|---|
| Spec Agent | ArtiCAD Design Agent | 写 spec：link/joint/connector/硬约束 |
| Spec 审查与测试设计 Agent | ArtiCAD Review + Articraft authored tests | 审查 spec + 把硬约束转成声明式测试 |
| Coding Agent | LAM Shape/Articulation Coder + Articraft | 写 model.py |
| 诊断 Agent | LAM Fixer + CADSmith Refiner | 判断问题归属（spec/实现/测试） |
| （新增）视觉审查 Agent | LAM VLM Critic + CADSmith VLM Judge | 可选：渲染/运动序列的语义审查 |

### 7.2 关键设计决策

- **默认不用视觉反馈做硬验证**（吸收 Articraft 的低成本路线），视觉审查作为**可选诊断 Agent 的输入**，不进入通过判定。
- **Connector-first**（吸收 ArtiCAD）：Spec Agent 必须输出 Connector 合约，Coding Agent 必须按 Connector 生成几何，Assembly 阶段是确定性 frame alignment 而非 LLM 现猜。
- **测试先于实现**（你方案 v1）：测试定义随 spec 冻结，Coding Agent 只能读。

---

## 8. 与开源仓库的落地集成路径

### 8.1 推荐集成方式

```text
unified3d-agent/
├── unified3d/                    # 第 4 节 SDK（自建，吸收 Articraft API 设计）
│   └── vendor/                   # 以 git submodule 或依赖方式引入
│       ├── articraft-sdk/        # 吸收其 assembly/testing/export/compiler
│       ├── agentcad/             # pip 依赖
│       └── text-to-cad/          # 只取 scripts 工具层，不取技能包整体
├── skills/                       # 第 5 节 Skill 集
├── harness/                      # 第 6 节 Harness
├── agents/                       # 第 7 节 Agent 层
├── specs/                        # 冻结 spec 与测试定义存储
├── runs/                         # 运行记录（trace/反例/资产包）
└── benchmarks/                   # 第 9 节评测协议
```

### 8.2 依赖与 license 合规

| 依赖 | 方式 | License | 注意事项 |
|---|---|---|---|
| Articraft | submodule / 源码吸收 | Apache 2.0 | 保留 NOTICE |
| text-to-cad | 提取 scripts + SKILL 结构 | MIT | 保留版权声明 |
| agentcad | pip 依赖 | Apache 2.0 | 直接使用 |
| build123d / cadquery-ocp | pip 依赖 | Apache 2.0 | 直接使用 |
| CLI-Anything FreeCAD | 可选集成 | Apache 2.0 | 需要 FreeCAD 时 |
| PartCAD | pip 依赖 | Apache 2.0 | 标准件管理 |
| CADSmith / Articulate-Anything / FutureCAD | **只参考架构，不复制代码** | 无 license | 避免合规风险 |
| LAM | 参考 prompt 与 agent 划分 | Apache 2.0 | 可安全吸收 |

---

## 9. 实施路线图

### Phase 1：底座打通（1–2 周）
- [ ] 以 Articraft SDK 为骨架，跑通 `text prompt → model.py → USDZ + URDF` 最小闭环。
- [ ] 接入 agentcad 的 `run/measure/inspect/diff` 作为静态 CAD 工具。
- [ ] 统一输出目录结构（asset_bundle：STEP/USDZ/URDF/mesh/tests/manifest）。

### Phase 2：Harness 加固（2–3 周）
- [ ] 移植你方案 v1 的冻结 spec/test、权限管理、反例追加写。
- [ ] 实现声明式测试 → Harness 展开（采样计划、关键姿态、最坏姿态搜索）。
- [ ] 接入 MuJoCo 物理验证（吸收 Articraft simulate + 你方案的连续碰撞检测）。
- [ ] 实现隐藏复核。

### Phase 3：Agent 层（2–3 周）
- [ ] Spec Agent + 审查/测试 Agent（Connector-first 输出）。
- [ ] Coding Agent（受限 workspace，Articraft harness 已有）。
- [ ] 诊断 Agent（吸收 LAM Fixer 思路，输入多视角+点云+轨迹）。
- [ ] 视觉审查 Agent（可选，VLM 三视图 + motion keyframe，只做诊断不做硬判定）。

### Phase 4：Skill 集与评测（1–2 周）
- [ ] 按第 5 节写 `cad / articulated / urdf / mesh / inspect / repair / simulate` 的 SKILL.md。
- [ ] 接入《3D生成模型评测验收协议.md》：PartNet-Mobility（articulated）+ DeepCAD/CADmium（静态）。
- [ ] 实现评测脚本，跑基线（Articulate-Anything、LAM 或同 backbone 单次生成）。

### Phase 5：规模化与数据闭环（持续）
- [ ] 引入 Zero-to-CAD 百万程序数据集做 SFT/初始化。
- [ ] 生成资产 + trace 回写训练集，形成数据飞轮。

---

## 10. 风险与对策

| 风险 | 对策 |
|---|---|
| Articraft SDK 尚在 0.x，API 可能变 | 用 git submodule 固定 commit；核心语义抽象成自己的接口层 |
| 视觉反馈成本高 | 默认走代码/测量/仿真验证；视觉审查只在诊断时按需触发 |
| MuJoCo/Isaac 环境重 | Harness 本地 CPU 跑 MuJoCo；Isaac 仅做最终验收 |
| FreeCAD 特征树与 build123d 不互通 | 统一以 build123d/STEP 为主真源；FreeCAD 仅企业场景接入 |
| 开源 license 风险 | CADSmith/Articulate-Anything/FutureCAD 无 license，只参考不复制 |
| 闭链机构/多自由度表示 | SDK 保留 "omitted closing joint" 与 articulation tree 支持；后续扩展 connector 闭链 |

---

## 11. 一句话总结

> **以 Articraft 的 articulated SDK + harness 为骨架，以 build123d 为几何内核，以 text-to-cad 的 Skill 组织与 scripts 工具 + agentcad 的测量验证为工具层，以你已有的 Spec/Review/Coding/Diagnosis + 冻结/采样/隐藏复核 Harness 为控制层，组合成一个 unified 的 static CAD + articulated 3D Agent 系统——这是当前开源生态下最省力、license 最干净的路径。**
