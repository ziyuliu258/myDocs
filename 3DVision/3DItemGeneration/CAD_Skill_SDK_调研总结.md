# CAD Agent Skill 与 CAD SDK/API 生态调研

**调研日期**: 2026-08-05  
**调研目标**: 系统梳理 CAD Agent 生态，包括可接入的 Agent Skill 和实际可用的 CAD SDK/API

> **术语约定**: 文中的 **text-to-cad** 特指 `earthtojake/text-to-cad` 这个具体仓库（一个 CAD/机器人/制造 Agent Skill 产品库），不是泛指”文本生成 CAD”技术。

---

## 核心结论

### 关键发现

1. **CAD Skill 生态多元化** - 不只有 text-to-cad 一家，还有 agentcad、FreeCAD 系列、OpenSCAD 系列等多条技术路线
2. **text-to-cad ≠ 单一 Skill** - 它是一个产品库，内含 7+ 个子 Skill（cad、cad-viewer、dxf、urdf 等）
3. **Articraft 与 text-to-cad 定位不同** - 前者是可动物体领域 SDK，后者是通用 CAD Agent 工作流
4. **本地建模首选 build123d** - 配合 text-to-cad 的 cad Skill 或 agentcad，输出 STEP

### 推荐技术栈

**本地 CAD Agent 原型**:
```
Agent Skill: text-to-cad@cad 或 agentcad
     ↓
建模 SDK: build123d (参数化 B-Rep)
     ↓
主工件: STEP 文件
     ↓
验证: cad-viewer + 尺寸/拓扑检查
     ↓
导出: STL/3MF/DXF/URDF/G-code
```

**已有 CAD 平台**:
- Fusion → Fusion API
- Onshape → FeatureScript + REST API  
- FreeCAD → FreeCAD Python API / cli-anything-freecad
- Rhino → RhinoCommon

---

## 0. 术语分层

**理解三层架构很重要**:

```
用户需求
  ↓
Agent Skill (告诉 Agent 怎么规划、调用、验证)
  ↓
CLI/MCP 或 SDK (执行命令/代码)
  ↓
CAD 内核或平台 (计算几何并保存模型)
  ↓
文件输出 (STEP/DXF/STL/URDF 等)
```

常见混淆：
- ❌ “cad-viewer 是一个 SDK” → ✅ 它是验证工作流 Skill
- ❌ “build123d 是一个 Skill” → ✅ 它是建模 SDK
- ❌ “OCCT 可以直接给 Agent 用” → ✅ 太底层，需要高层封装

---

## 1. 术语快速对照

| 类别                  | 解决什么问题                  | 典型对象                              | Agent 直接用？         |
| ------------------- | ----------------------- | --------------------------------- | ------------------ |
| **Agent Skill**     | 告诉 Agent 任务流程、验收标准、输出约定 | `cad`、`freecad-scripts`           | ✅ 是入口              |
| **CLI/MCP harness** | 把 CAD 运行时暴露为可调用工具       | `agentcad`、`cli-anything-freecad` | ✅ 通过 Skill 调用      |
| **CAD SDK**         | 用代码创建/修改几何              | build123d、CadQuery                | ❌ Agent 写代码，SDK 执行 |
| **几何内核**            | B-Rep/曲面/布尔/拓扑          | OCCT、Parasolid                    | ❌ 太底层              |
| **CAD 平台 API**      | 控制商业/云 CAD 平台           | Fusion API、Onshape REST           | ⚠️ 需要授权和平台         |
| **CAD DSL**         | 用专门语言描述模型               | OpenSCAD、FeatureScript            | ✅ Agent 可生成脚本      |
| **云 AI CAD 服务**     | 云端接收提示词生成 CAD           | Zoo Agent API                     | ✅ 但需验证输出           |
| **研究项目**            | 论文/特定任务的原型              | Text2CAD (论文)、Articraft           | ⚠️ 看成熟度            |

---

## 2. CAD Agent Skill 清单

### 核心生成类 Skill

| Skill                    | 仓库                                                                    | 定位                                  | 安装量 (2026-08) |
| ------------------------ | --------------------------------------------------------------------- | ----------------------------------- | ------------: |
| **text-to-cad@cad**      | [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) | 通用 CAD 生成，STEP-first                |          7.7K |
| **agentcad**             | [jdilla1277/agentcad](https://github.com/jdilla1277/agentcad)         | 本地 CAD CLI + MCP，build123d/CadQuery |            14 |
| **freecad-scripts**      | [github/awesome-copilot](https://github.com/github/awesome-copilot)   | FreeCAD Python/宏专家                  |           963 |
| **cli-anything-freecad** | [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything)           | FreeCAD 258 命令 harness              |           458 |
| **openscad**             | [mitsuhiko/agent-stuff](https://github.com/mitsuhiko/agent-stuff)     | OpenSCAD 生成/验证                      |           685 |

### text-to-cad 产品库内的其他 Skill

> ⚠️ **重要**: 下面 6 个 Skill 都来自同一个仓库 `earthtojake/text-to-cad`，不是独立竞品

| Skill | 定位 | 安装量 |
|---|---|---:|
| **cad-viewer** | STEP/STL 可视化审查 | 5.3K |
| **step-parts** | 标准件检索（螺钉/轴承/电机） | 6.1K |
| **implicit-cad** | 隐式几何/SDF/TPMS | 4.0K |
| **dxf** | 2D 激光/CNC 切割图 | 3.9K |
| **urdf/sdf/srdf** | 机器人描述文件 | 各 5.6K |

### 研究/实验类 Skill

| Skill | 定位 | 特点 | 来源 |
|---|---|---|---|
| **openscad-iterative-modeling** | OpenSCAD MCP 迭代闭环 | SCAD → PNG → 批评 → 修改 | [fboldo/openscad-mcp-server](https://github.com/fboldo/openscad-mcp-server) |
| **cadquery-builder** (agent3dify) | 图像到 CadQuery | 多 Agent + 渲染验证器 | [neka-nat/agent3dify](https://github.com/neka-nat/agent3dify) |

> **注**: `cadquery-builder` 是 agent3dify 项目中的 CadQuery Builder 子 Agent 组件，负责从工程图像生成 CadQuery 模型代码。

### Skill 分层总结

```
生成入口层: cad, agentcad, freecad-scripts
    ↓
软件控制层: cli-anything-freecad (258 FreeCAD 命令)
    ↓
视觉反馈层: cad-viewer, openscad-iterative-modeling
    ↓
专项能力层: dxf (2D), implicit-cad (SDF), openscad (CSG)
    ↓
领域扩展层: urdf/sdf (机器人), step-parts (标准件)
```

---

## 3. CAD SDK/API 清单

### 本地参数化建模 SDK (首选)

| SDK                    | 类型               | 推荐度 | 适合场景                     |
| ---------------------- | ---------------- | --- | ------------------------ |
| **build123d**          | Python 参数化 B-Rep | ⭐⭐⭐ | 新建本地 Agent 项目，STEP-first |
| **CadQuery**           | Python 参数化 CAD   | ⭐⭐⭐ | 复现论文，已有 CadQuery 代码      |
| **FreeCAD Python API** | 完整 CAD 应用 API    | ⭐⭐  | 已有 FreeCAD 项目，需要特征树      |
| **OpenSCAD**           | CSG DSL + CLI    | ⭐⭐  | 简单规则件，3D 打印              |

**几何内核与绑定**:
- **OCCT**: C++ 几何内核，build123d/CadQuery 底层
- **OCP** (cadquery-ocp): OCCT 的薄 Python 绑定
- **pythonOCC**: 另一套 OCCT Python 封装

**2D 工程图**:
- **ezdxf**: Python DXF 读写，激光/CNC 切割

### 商业/云端 CAD 平台 API

| 平台 | API/SDK | 适合场景 |
|---|---|---|
| **Rhino** | RhinoCommon (.NET) | NURBS/自由曲面，Grasshopper 自动化 |
| **Fusion** | Fusion API (桌面脚本) | 已有 Fusion 工作流 |
| **Fusion** | Fusion Automation API (云端) | 批处理/服务器自动化 |
| **Onshape** | FeatureScript + REST API | 云协作/自定义特征 |
| **Zoo** | Agent API / KCL / Engine API | 托管 AI CAD 服务 |

### 组件管理框架

- **PartCAD**: 管理 STEP/STL、脚本、组件接口、装配和 Git 协作

---

## 4. 按任务选型速查表

| 目标                | 推荐 Skill                                 | 推荐 SDK               | 输出格式          |
| ----------------- | ---------------------------------------- | -------------------- | ------------- |
| **本地文本生成机械零件**    | text-to-cad@cad / agentcad               | build123d            | STEP + 源码     |
| **复现研究论文**        | cadquery-builder                         | CadQuery             | Python + STEP |
| **已有 FreeCAD 项目** | freecad-scripts / cli-anything-freecad   | FreeCAD Python API   | FreeCAD 文档    |
| **简单支架/打印件**      | openscad                                 | OpenSCAD             | SCAD + STL    |
| **视觉反馈迭代**        | cad-viewer / openscad-iterative-modeling | build123d/CadQuery   | PNG + STEP    |
| **2D 激光/CNC**     | text-to-cad@dxf                          | ezdxf + build123d    | DXF           |
| **机器人可动物体**       | text-to-cad@cad + urdf/sdf               | build123d + 机器人工具    | STEP + URDF   |
| **Fusion 企业流程**   | Fusion MCP                               | Fusion API           | Fusion 文档     |
| **云 CAD 协作**      | Onshape MCP                              | FeatureScript + REST | Onshape 文档    |
| **快速接入云 AI**      | Zoo MCP                                  | Zoo Agent API        | 云端模型          |

---

## 5. 核心对比: Articraft vs text-to-cad

### Articraft 定位

```
可动物体领域 SDK
 + parts / geometry / joints 抽象
 + 受限 workspace / harness
 + probe / compile / test 反馈
 + Agent 的 edit → execute → repair 循环
```

**解决问题**: 有几何和关节语义的可动物体如何被 Agent 可靠修改和测试  
**不是**: 通用 CAD 生态入口

### text-to-cad 定位

```
CAD/机器人/制造 Agent Skill 产品库
 + cad: 通用 CAD 生成工作流 (STEP-first)
 + cad-viewer: 可视化审查
 + dxf/urdf/sdf: 领域扩展
 + step-parts: 标准件检索
```

**工作方式**:
```
自然语言需求
  → skills/cad (规划、约定、验证流程)
  → Agent 写 build123d Python
  → packages/cadpy (STEP 工件、验证、装配)
  → cad-viewer (可视化审查)
  → 按需导出到其他 Skill
```

### 直接对比

| 维度             | Articraft                            | text-to-cad                  |
| -------------- | ------------------------------------ | ---------------------------- |
| **产品边界**       | 可动物体领域 SDK                           | 通用 CAD Agent Skill 产品库       |
| **核心对象**       | parts、geometry、joints                | Python 源码、STEP 工件            |
| **Agent 工作方式** | 受限 workspace 内 edit/repair           | 生成/修改 build123d 代码 + STEP 验证 |
| **验证机制**       | 关节结构 + 领域测试                          | 尺寸/拓扑/快照 + 浏览器审查             |
| **适用范围**       | 可动物体（关节/运动）                          | 通用 CAD + 机器人 + 制造            |
| **组合关系**       | 可用 text-to-cad 生成几何，Articraft 处理关节语义 |                              |

**结论**: 两者可以组合使用 - text-to-cad 提供通用 CAD 能力，Articraft 处理可动物体的领域约束。

---

## 6. 推荐技术栈

### 新建本地 CAD Agent

```
Agent Skill: text-to-cad@cad 或 agentcad
     ↓
建模 SDK: build123d
     ↓
几何内核: OCCT/OCP (build123d 自动调用)
     ↓
验证: cad-viewer + agentcad measure/inspect
     ↓
主工件: STEP
     ↓
导出: STL/3MF/DXF/URDF 等
```

### 复现研究/图像转 CAD

```
框架: agent3dify 风格 (supervisor + verifier)
     ↓
建模 SDK: CadQuery
     ↓
反馈: 渲染视图 + 几何检查
     ↓
输出: CadQuery Python + STEP
```

### 企业已有平台

- **Fusion 用户**: Fusion API / Fusion Automation API
- **Onshape 用户**: FeatureScript + REST API
- **FreeCAD 用户**: FreeCAD Python API / cli-anything-freecad
- **Rhino 用户**: RhinoCommon / Grasshopper

---

## 7. 调研来源与方法

### Agent Skill 来源

1. [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) - Skills CLI 搜索
2. [agentcad](https://github.com/jdilla1277/agentcad) - GitHub + Skills CLI
3. [CLI-Anything FreeCAD](https://github.com/HKUDS/CLI-Anything) - SKILL.md
4. [freecad-scripts](https://github.com/github/awesome-copilot) - GitHub 官方 Skill 集合
5. [OpenSCAD Skills](https://github.com/mitsuhiko/agent-stuff) - mitsuhiko 仓库
6. [OpenSCAD MCP](https://github.com/fboldo/openscad-mcp-server) - MCP 服务器
7. [agent3dify](https://github.com/neka-nat/agent3dify) - 研究项目

### SDK/API 官方文档

**本地建模 SDK**:
- [build123d](https://build123d.readthedocs.io/)
- [CadQuery](https://cadquery.readthedocs.io/)
- [FreeCAD API](https://www.freecad.org/api/)
- [OpenSCAD](https://openscad.org/documentation.html)

**几何内核与绑定**:
- [OCCT](https://dev.opencascade.org/doc/overview/html/)
- [OCP/cadquery-ocp](https://pypi.org/project/cadquery-ocp/)
- [pythonOCC](https://github.com/tpaviot/pythonocc-core)
- [ezdxf](https://ezdxf.readthedocs.io/)

**商业/云平台**:
- [RhinoCommon](https://developer.rhino3d.com/guides/rhinocommon/)
- [Fusion API](https://aps.autodesk.com/developer/overview/autodesk-fusion-api)
- [Fusion Automation API](https://aps.autodesk.com/automation-apis)
- [Onshape FeatureScript](https://cad.onshape.com/FsDoc/)
- [Onshape REST API](https://onshape-public.github.io/docs/api-intro/)
- [Zoo Agent API](https://zoo.dev/docs/developer-tools/agent-api)
- [Zoo KCL](https://zoo.dev/docs/kcl)

**组件管理**:
- [PartCAD](https://github.com/openvmp/partcad)

### 调研方法

- 用 Exa MCP 搜索 GitHub 仓库、README、SKILL.md
- 用 Skills CLI (`npx skills find`) 检查安装量
- 核对官方文档和 API 弃用状态
- 所有数据为 2026-08-05 快照，会随时间变化

---

## 附录: 安装量说明

**安装量 ≠ 质量或用户数**:
- 数据来自 Skills CLI 2026-08-05 快照
- text-to-cad 子 Skill 的安装量不应相加（同一用户可能安装多个）
- 新项目（如 agentcad）安装量低但技术成熟度可能很高
- 优先根据实际需求选型，而非只看安装量
