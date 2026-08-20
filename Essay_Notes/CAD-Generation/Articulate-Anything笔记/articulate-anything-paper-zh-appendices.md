# Articulate-Anything：论文中文全译（附录 A）

> 论文：*Articulate-Anything: Automatic Modeling of Articulated Objects via a Vision-Language Foundation Model*
> 作者：Long Le 等，ICLR 2025
> 原文：[Articulate-anything.pdf](../../Essay/3DAssets/Articulate-anything.pdf)
> 翻译范围：论文附录 A（A.1–A.8）。引用、公式编号、数值、模型名、函数名和代码标识符均按原文保留。

## A　附录

> **图 14：关节预测失败的可视化。**
> 我们可视化了不同类型的关节失败；其严重程度从最严重的关节类型错误，到最轻微的关节限位错误。
>
> 图内左、右两列分别为“真值（Groundtruth）”和“预测（Prediction）”；从上到下的行标签依次为“关节类型（Joint type）”、“关节轴（Joint axis）”、“关节原点（Joint origin）”和“关节限位（Joint limit）”。

### A.1　连杆和关节预测误差的计算

#### A.1.1　连杆误差

一个连杆由位置 $x \in \mathbb{R}^3$ 和四元数方向 $q \in \mathbb{H}$ 表示，其中 $\mathbb{H}$ 是单位四元数的空间。给定预测的连杆状态 $(x_p, q_p)$ 和真值状态 $(x_g, q_g)$，我们定义两项误差度量：

**位置误差：**预测位置与真值位置之间的欧氏距离：

$$
e_{\mathrm{pos}} = \lVert x_p - x_g \rVert_2 \tag{4}
$$

**方向误差：**单位球面上的测地距离，计算为：

$$
e_{\mathrm{orient}} = 2\arccos\bigl(\lvert q_p \cdot q_g \rvert\bigr) \tag{5}
$$

其中，$\cdot$ 表示四元数点积。这个度量表示预测方向和真值方向之间的最小旋转角。总连杆误差是这些分量的平均值。

#### A.1.2　关节误差

关节误差通过将预测关节状态的若干分量与真值进行比较来计算。令 $J_p$ 和 $J_g$ 分别表示预测和真值的关节状态。关节误差的分量按从最严重到最轻微的顺序如下：

1. **关节类型误差：**用于表示预测关节类型是否与真值相符的二元度量：

   $$
   e_{\mathrm{type}} =
   \begin{cases}
   0, & \text{若 } \operatorname{type}(J_p)=\operatorname{type}(J_g),\\
   1, & \text{否则。}
   \end{cases}
   \tag{6}
   $$

2. **关节轴误差：**预测关节轴和真值关节轴之间的夹角：

   $$
   e_{\mathrm{axis}} = \min\!\left(
   \arccos\!\left(\frac{a_p \cdot a_g}{\lVert a_p \rVert_2\lVert a_g \rVert_2}\right),
   \arccos\!\left(\frac{-a_p \cdot a_g}{\lVert a_p \rVert_2\lVert a_g \rVert_2}\right)
   \right) . \tag{7}
   $$

   其中，$a \in \mathbb{R}^3$ 是旋转关节的旋转轴或移动关节的平移轴，且 $e_{\mathrm{axis}} \in [0, \pi]$。

3. **关节原点误差：**对于旋转关节，我们利用叉积计算两条关节轴之间的最短距离：

   $$
   e_{\mathrm{origin\_pos}} =
   \frac{\lvert p \cdot (a_p \times a_g) \rvert}{\lVert a_p \times a_g \rVert} . \tag{8}
   $$

   其中，$p=x_p-x_g$ 是预测原点与真值原点之间的差，$a_p, a_g$ 分别是预测和真值的关节轴。对于移动关节，我们使用欧氏距离：

   $$
   e_{\mathrm{origin\_pos}} = \lVert x_p-x_g \rVert_2 . \tag{9}
   $$

4. **关节限位误差：**由两个子分量组成：

   1. *运动范围差异：*

      $$
      e_{\mathrm{limit\_range}} = \lVert m_p-m_g \rVert_2 , \tag{10}
      $$

      其中 $m_i=a_i(u_i-l_i)$，$u_i$ 和 $l_i$ 分别为关节上限和下限。

   2. *运动方向差异：*

      $$
      e_{\mathrm{limit\_dir}} = 1 - \frac{m_p \cdot m_g}{\lVert m_p \rVert_2\lVert m_g \rVert_2} . \tag{11}
      $$

      此度量的取值范围是 0（方向完全相同）到 2（方向完全相反）；1 表示两个方向彼此垂直。

当所有关节分量预测均位于容差范围内时，一次关节预测即告成功。否则，关节失败会按一种自然顺序归因：先检测最严重的错误——关节类型——最后检测最轻微的错误——关节限位。

不同关节失败类型的可视化见图 14。

### A.2　Critic 与真值的一致性

图 15 可视化了两个 articulation 任务中，真值与我们自己的 critic 对“成功”的预测之间的混淆矩阵。我们的视觉 critic 与真值高度相关。最大的分歧来自假阳性情形，即 critic 错误地把一次错误的 articulation 判定为正确。这些情形包含难以察觉的错误。

> **图 15：Critic–真值混淆矩阵。**
> 我们的视觉 critic 与真值高度相关。最大的分歧来自假阳性情形，即 critic 错误地将一个错误的 articulation 判为正确；这些情形包含难以察觉的错误。

图 15 的两个混淆矩阵如下。纵轴为真值（Ground Truth），横轴为预测（Predicted）；两轴的类别均为成功（Success）与失败（Failure）。

| 任务 | 真值 / 预测 | 预测成功 | 预测失败 |
|---|---|---:|---:|
| 连杆放置（Link Placement） | 真值成功 | 真阳性（True Pos）：84.42% | 假阴性（False Neg）：1.59% |
| 连杆放置（Link Placement） | 真值失败 | 假阳性（False Pos）：5.68% | 真阴性（True Neg）：8.30% |
| 关节预测（Joint Prediction） | 真值成功 | 真阳性（True Pos）：73.06% | 假阴性（False Neg）：1.99% |
| 关节预测（Joint Prediction） | 真值失败 | 假阳性（False Pos）：4.57% | 真阴性（True Neg）：20.38% |

### A.3　机器人训练细节

我们使用 PPO 和生成的资产，在 Robosuite 模拟器中训练一条 Franka 机械臂执行四项机器人操作任务。策略输出关节和夹爪的位置。对于每项任务，我们以 3 个随机种子训练策略，每个种子使用 Stable-Baselines3 库中的 PPO [Raffin et al. (2021)] 进行 200 万个环境步。我们随机化物理参数（摩擦、阻尼、摩擦损失等）、物体的尺度和位姿，以获得鲁棒的策略。

### A.4　基线方法

URDFormer 要求输入图像中每一个物体部件都有一个边界框；该边界框可以通过微调后的 Grounding DINO [Liu et al. (2023c)] 获得，也可以通过物理引擎提供的真值边界框这一 oracle 获得。Real2Code 要求以定向物体边界框（OBB）作为输入文本来查询 LLM。在 PartNet-Mobility 上，这些 OBB 使用 Blender 中 oracle RGB-D 图像和真值分割掩码获得。

#### A.4.1　随手采集的输入

与基线需要大量人工整理不同，我们基于视频的方法在杂乱环境中随手采集的输入上表现出色：我们为 URDFormer 调整了 DINO 边界框，并为 Real2Code 仔细整理了前景分割及其他超参数。项目网站展示了用 iPhone 随手拍摄的多种物体类别。输入具有不同的观察角度，并且有时会意外地倾斜。这类输入给基线带来很大困难。例如，图 18 展示了 URDFormer 所需的人工调整。图 17 展示了为了清理 real2code 的物体部件掩码和点云而人工整理的前景分割掩码及其他调优后的超参数。

#### A.4.2　复现 Real2Code

**Real2Code 的 LLM 训练。**Real2Code 没有发布其 LLM 模型检查点或训练代码。因此，我们基于其论文描述和其他代码，尽力复现其 LLM 模型。我们使用其预处理代码获得 LLM 训练数据集，并如论文所述，采用 4-bit 量化和 LoRA [Hu et al. (2021)] 微调 CodeLlama-7B-Instruct 模型 [Roziere et al. (2023)]。LLM 的提示词见图 16。

> **图 16：我们用于复现 real2code 的指令提示词。**
> 原始工作 GitHub 上既没有训练代码，也没有模型检查点。

图 16 中的提示词全文如下；字段名、结构和输出格式按原文保留：

```text
[INST] 你是一个经过训练、能够理解 3D 场景和物体关系的 AI 助手。给定下述定向
边界框（OBB）信息，你的任务是生成一份 child joints 列表，用以描述物体部件之间的
articulation。

OBB Information:{...}

生成一份 child joints 列表。每个 joint 均应由一个字典描述，字典包含下列键：
- box：子边界框的 ID
- type：关节类型（旋转关节使用 'hinge'，移动关节使用 'slide'）
- idx：旋转轴索引（x 轴为 0，y 轴为 1，z 轴为 2）
- edge：OBB 上的边缘坐标，例如 [1, -1]
- sign：关节方向（+1 或 -1）

重要：你的回复必须只包含 child joints 列表，且必须与下方所示格式完全一致，
前后不得有任何额外文本：
child joints = [
dict(box=[child OBB ID], type=[joint type], idx=[rotation axis index], edge=[edge
coordinates], sign=[direction]),
# 根据需要添加更多 joint ]

生成 child joints 列表：[/INST]
```

译注：图 16 中原文确实写作 `child joints`（含空格）；尽管这不是 Python 中合法的变量名，仍按原文保留。

**Real2Code 的真实环境重建。**我们未能基于发布的代码复现形状补全模型。因此，我们改为使用 Open3D [Zhou et al. (2018)] 中的 alpha surface reconstruction [Edelsbrunner et al. (1983)]，从点云重建网格，并手动调节超参数。我们发现，该方法从其公开发布的网格中得到的网格质量相当或更高。

我们手工选择 SAM 的查询点以确保近乎完美的前景分割掩码；调节 3D 分割方案的超参数（如输入图像、查询点数量、最小点云大小等）；清理点云、掩码，并调节网格提取。kinematic-aware SAM 模型使用基线作者提供的代码进行了微调。

我们人工整理前景分割掩码、移除错误分割的点云、调节超参数，并人工解析其 LLM 输出。图 17 将 real2code 的输入及中间输出可视化。

> **图 17：Real2code 经人工整理的输入和中间输出。**
> 为了从 DUSt3R 获得良好的全局对齐，我们对每个物体使用约 3 至 7 张不同视角的输入图像。通过查询基础 SAM 模型，人工整理了前景分割掩码。通过调节各种分割超参数（例如使用哪些输入图像、查询点数量、最小点云大小等）和表面重建参数（即 $\alpha$），对分割后的点云和网格进行了整理。对每个分割掩码，人工移除错误分割的点云；使用 Open3D 的半径离群值移除（radius outlier removal）去除伪点；并且只保留 DBSCAN 聚类 [Ester et al. (1996)] 得到的最大连通分量。LLM 输出含有错误的语法和额外的冗余表述，因而被人工解析。
>
> 图内从左到右的列标签为：“输入图像（多视角图像之一）”、“前景分割掩码（多个掩码之一）”、“SAM 输出（多个输出之一）”、“分割后的点云”和“分割后的网格”。

#### A.4.3　评估 URDFormer

URDFormer 为每个边界框预测一个 link，并为每个非根 link 关联一个 joint。为将 URDFormer 的预测与真值对照评估，我们采用一个 link 匹配算法，将预测 link 与真值 link 对齐。通过计算物理引擎提供的边界框与 link 分割掩码之间的重叠度，将每个 URDFormer 边界框与一个真值 link 匹配。对于真实环境重建，我们如图 18 所示手动校正了物体部件边界框。

> **图 18：URDFormer 的人工校正。**
> 比较其微调 DINO 所给出的边界框与我们的人工校正结果。
>
> 图内两列标签分别为“DINO”和“人工（Manual）”。

### A.5　可比较的输入模态

图 19 将 **ARTICULATE-ANYTHING** 与基线在相同输入模态下进行比较。借助基础模型的常识和高层规划能力，我们以同样贫乏的输入模态获得了比既有工作更高的准确率。

> **图 19：可比较的输入。**
> 我们使用相同输入模态，将 **ARTICULATE-ANYTHING** 与两个基线 Real2Code 和 UDRFormer 进行比较。该消融在基线相应的已见类别上完成。
>
> 图内柱状数据如下：基于文本的方法中，Articulate Anything（文本）为 **40.3%**，Real2Code Oracle 为 **13.5%**；基于图像的方法中，Articulate Anything（图像）为 **48.5%**，URDFormer Oracle 为 **24.7%**，URDFormer DINO 为 **20.2%**。纵轴为成功率（Success Rate，%）。

**表 1：方法间平均关节预测误差的比较（越低越好）。**“Type”表示关节类型预测错误的比例；“Axis”误差以弧度计；“Origin”误差以米计。**ARTICULATE-ANYTHING** 显著优于全部已有工作。**ARTICULATE-ANYTHING** 使用 few-shot prompting，且不区分 ID 与 OOD 类别，因此只报告“全部类别（All Classes）”的结果。分类误差（关节类型）给出 95% 置信区间；连续误差（关节轴和原点）给出标准差。

| 方法 | 全部类别：Type ↓ | 全部类别：Axis ↓ | 全部类别：Origin ↓ | ID 类别：Type ↓ | ID 类别：Axis ↓ | ID 类别：Origin ↓ | OOD 类别：Type ↓ | OOD 类别：Axis ↓ | OOD 类别：Origin ↓ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Real2Code Oracle | 0.537 ± 0.014 | 1.006 ± 0.723 | 0.294 ± 0.417 | 0.410 ± 0.029 | 1.164 ± 0.671 | 0.344 ± 0.479 | 0.576 ± 0.016 | 0.937 ± 0.734 | 0.272 ± 0.386 |
| URDFormer Oracle | 0.556 ± 0.025 | 0.374 ± 0.666 | 0.581 ± 0.355 | 0.418 ± 0.036 | 0.208 ± 0.532 | 0.609 ± 0.357 | 0.679 ± 0.032 | 0.643 ± 0.766 | 0.513 ± 0.340 |
| URDFormer DINO | 0.460 ± 0.033 | 0.261 ± 0.583 | 0.547 ± 0.317 | 0.288 ± 0.039 | 0.133 ± 0.437 | 0.582 ± 0.281 | 0.722 ± 0.047 | 0.758 ± 0.782 | 0.438 ± 0.385 |
| **ARTICULATE-ANYTHING** | **0.021 ± 0.003** | **0.141 ± 0.441** | **0.200 ± 0.380** | — | — | — | — | — | — |

> **图 20：连续误差的小提琴图。**
> 关节类型是二元误差，因此不适用于这张图。正如表 1 所示，**ARTICULATE-ANYTHING** 的平均原点误差和轴误差最小。对于关节轴，我们注意到基线中存在两个不同的模态，表明其中分别包含分布内数据和 OOD 数据的误差。
>
> 图内左图为“关节原点误差（米）”（Joint Origin Error）；右图为“关节轴误差（弧度）”（Joint Axis Error）。横轴的四种方法依次为 Articulate Anything、Real2Code Oracle、URDFormer Oracle 和 URDFormer DINO。

### A.6　附加统计

图 21 和图 22 分别按物体类别给出连杆放置和关节预测任务的成功率分解。我们在所有任务中都使用相机位姿。小物体部件或奇异、不规则的运动往往会给 **ARTICULATE-ANYTHING** 带来更大困难。进一步优化（例如利用相机进行放大）可能改善性能。表 1 给出了我们的方法和既有工作带有统计置信度的原始平均误差；图 20 则通过小提琴图进一步可视化了误差分布。

> **图 21：按物体类别划分的 ARTICULATE-ANYTHING 连杆放置成功率。**
> 图中平均值为 **0.86**。图内类别标签与成功率如下（类别原文保留在括号中）：

| 类别 | 成功率 |
|---|---:|
| 键盘（Keyboard） | 1.00 |
| 盒子（Box） | 1.00 |
| 窗户（Window） | 0.98 |
| 储物家具（StorageFurniture） | 0.98 |
| 笔记本电脑（Laptop） | 0.98 |
| 冰箱（Refrigerator） | 0.98 |
| 洗碗机（Dishwasher） | 0.98 |
| 风扇（Fan） | 0.98 |
| 时钟（Clock） | 0.97 |
| 刀具（Knife） | 0.95 |
| 开关（Switch） | 0.94 |
| 烤箱（Oven） | 0.93 |
| 微波炉（Microwave） | 0.92 |
| 厨房锅具（KitchenPot） | 0.92 |
| 门（Door） | 0.91 |
| 瓶子（Bottle） | 0.91 |
| 水龙头（Faucet） | 0.90 |
| 推车（Cart） | 0.90 |
| 垃圾桶（TrashCan） | 0.90 |
| 打印机（Printer） | 0.90 |
| 遥控器（Remote） | 0.88 |
| 水壶（Kettle） | 0.86 |
| 桌子（Table） | 0.86 |
| 马桶（Toilet） | 0.86 |
| 地球仪（Globe） | 0.85 |
| 灯（Lamp） | 0.84 |
| 电话（Phone） | 0.83 |
| 眼镜（Eyeglasses） | 0.83 |
| 分配器（Dispenser） | 0.82 |
| 洗衣机（WashingMachine） | 0.82 |
| 椅子（Chair） | 0.81 |
| 钳子（Pliers） | 0.80 |
| 显示器（Display） | 0.78 |
| 咖啡机（CoffeeMachine） | 0.78 |
| 保险箱（Safe） | 0.77 |
| 手提箱（Suitcase） | 0.71 |
| 相机（Camera） | 0.70 |
| 烤面包机（Toaster） | 0.68 |
| 剪刀（Scissors） | 0.65 |
| 笔（Pen） | 0.62 |
| USB | 0.59 |
| 水桶（Bucket） | 0.58 |
| 鼠标（Mouse） | 0.57 |
| 折叠椅（FoldingChair） | 0.54 |
| 打火机（Lighter） | 0.39 |
| 订书机（Stapler） | 0.39 |

> **图 22：按物体类别划分的 ARTICULATE-ANYTHING 关节预测成功率。**
> 图中平均值为 **0.75**。图内类别标签与成功率如下（类别原文保留在括号中）：

| 类别 | 成功率 |
|---|---:|
| 遥控器（Remote） | 0.98 |
| 键盘（Keyboard） | 0.95 |
| 微波炉（Microwave） | 0.92 |
| 笔记本电脑（Laptop） | 0.92 |
| 储物家具（StorageFurniture） | 0.88 |
| 桌子（Table） | 0.80 |
| 电话（Phone） | 0.80 |
| 窗户（Window） | 0.79 |
| 厨房锅具（KitchenPot） | 0.79 |
| 洗碗机（Dishwasher） | 0.73 |
| 打印机（Printer） | 0.68 |
| 洗衣机（WashingMachine） | 0.67 |
| 咖啡机（CoffeeMachine） | 0.55 |
| 烤面包机（Toaster） | 0.53 |
| 鼠标（Mouse） | 0.52 |
| 笔（Pen） | 0.51 |
| 开关（Switch） | 0.50 |
| 垃圾桶（TrashCan） | 0.42 |
| 冰箱（Refrigerator） | 0.41 |
| 椅子（Chair） | 0.41 |
| 相机（Camera） | 0.38 |
| USB | 0.38 |
| 水壶（Kettle） | 0.35 |
| 门（Door） | 0.35 |
| 烤箱（Oven） | 0.34 |
| 手提箱（Suitcase） | 0.33 |
| 分配器（Dispenser） | 0.31 |
| 马桶（Toilet） | 0.29 |
| 瓶子（Bottle） | 0.22 |
| 打火机（Lighter） | 0.21 |
| 盒子（Box） | 0.20 |
| 刀具（Knife） | 0.13 |
| 保险箱（Safe） | 0.13 |
| 水龙头（Faucet） | 0.08 |
| 显示器（Display） | 0.06 |
| 灯（Lamp） | 0.06 |
| 水桶（Bucket） | 0.05 |
| 订书机（Stapler） | 0.04 |
| 眼镜（Eyeglasses） | 0.01 |
| 折叠椅（FoldingChair） | 0.00 |
| 时钟（Clock） | 0.00 |
| 地球仪（Globe） | 0.00 |
| 钳子（Pliers） | 0.00 |
| 风扇（Fan） | 0.00 |
| 剪刀（Scissors） | 0.00 |

### A.7　网格重建

**表 2：网格重建质量。**表中给出不同模型在真实环境结果上的 Chamfer distance（越低越好）。最佳结果以粗体表示，次佳结果以下划线表示。与网格生成模型整合后的 **ARTICULATE-ANYTHING** 远优于任何基线。即便采用检索，我们的系统仍优于所有既有工作，包括使用 DUSt3R 做显式 3D 场景重建的 Real2Code。

| 方法 | 马桶（Toilet） | 柜体（Cabinet） | 手提箱（Suitcase） | 椅子（Chair） | 平均值（Avg.） |
|---|---:|---:|---:|---:|---:|
| Ours（Generation） | **0.0637** | **0.0740** | **0.0735** | **0.0698** | **0.0703** |
| Ours（Retrieved） | <u>0.1133</u> | <u>0.1215</u> | <u>0.0781</u> | 0.1210 | 0.1102 |
| Real2Code | 0.1192 | 0.1397 | 0.0877 | <u>0.0987</u> | <u>0.1085</u> |
| URDFormer | 0.4191 | 0.2164 | 0.1531 | 0.1278 | 0.2291 |

**表 3：不同方法的 Chamfer distance 比较。**较低的数值表示更好的网格重建质量。表中给出了均值和标准差。

| 方法 | Chamfer distance |
|---|---:|
| Articulate-Anything（retrieval） | **0.1007 ± 0.062** |
| Real2Code（Oracle） | <u>0.229 ± 0.166</u> |
| URDFormer（Oracle） | 0.429 ± 0.267 |
| URDFormer（DINO） | 0.437 ± 0.217 |

表 2 包含图 7 中真实环境物体的网格重建结果。真值网格由配备 LiDAR 的 iPhone 捕获。由于 LiDAR 无法很好地捕获玻璃，未包含窗户（Window）。与网格生成模型整合后的 **ARTICULATE-ANYTHING** 远优于任何其他基线。即使使用检索，我们的系统仍优于所有既有工作，包括使用 DUSt3R 做显式 3D 场景重建的 Real2Code。表 3 比较了 PartNet-Mobility 数据集上的重建质量。Real2Code 使用了真值 RGBD 图像。评估某一物体时，我们会从候选池中移除该物体，以避免 **ARTICULATE-ANYTHING** 检索到完全相同的物体。

### A.8　生成新资产

> **图 23：带网格生成的 ARTICULATE-ANYTHING。**
> **ARTICULATE-ANYTHING** 可以与网格生成模型整合，以生成高质量的可动物体。视频演示请见项目网站：[https://articulate-anything.github.io/](https://articulate-anything.github.io/)。
>
> 图中从左到右展示的物体为：柜体（Cabinet）、椅子（Chair）、手提箱（Suitcase）、马桶（Toilet）和窗户（Window）。

目前，**ARTICULATE-ANYTHING** 使用网格检索机制来利用现有 3D 数据集。诸如 Objaverse [Deitke et al. (2024)] 的开放仓库包含超过 1,000 万个静态物体，为我们的系统提供了丰富资产来源；系统可通过 articulation 使其“活起来”。然而，要生成更加定制化的资产，一个很有前景的未来方向是利用大规模网格生成模型。

本节展示了朝这一目标迈出的初步结果。给定 **ARTICULATE-ANYTHING** 的视觉输入——例如视频或图像——我们首先提取目标物体的一张图像。随后利用网格生成模型生成物体的 3D 模型。图 24 比较了三种模型所生成的网格质量：Rodin [Deemos (2024)]、Instant Mesh [Xu et al. (2024)] 和 Stable-Fast-3D [Boss et al. (2024)]。

我们因其高质量输出选择 Rodin。随后，我们使用 Grounded Segment-Anything [Ren et al. (2024)] 获得物体按部件划分的 3D 分割。无条件分割并不可靠，因为依据任务不同，物体部件可能被欠分割或过分割。为解决这一问题，我们以视频输入为条件：指示一个 VLM 识别运动部件，并将其用作分割目标。接着，我们从多个相机视角渲染 3D 模型。对每个视角，我们应用 Grounded SAM：它先获取物体部件的边界框，再运行 SAM 得到细粒度的分割掩码。图 25 可视化了每个视角的 2D 分割掩码。

> **图 24：网格生成。**
> 使用不同模型，从单张源图像生成 3D 网格的比较。每个模型的输出均展示正视图和侧视图。
>
> 图内列标签为“源图像（Source image）”、Rodin、Instant Mesh 和 Stable-Fast-3D；各模型下的两行分别为“（a）正视图（front）”和“（b）侧视图（side）”。

> **图 25：Grounded SAM。**
> 使用 Grounded SAM 为物体的每个视角获得一个 2D 分割掩码。对于每个视角，左侧显示输入 RGB 图像，右侧显示以红色叠加的所得掩码。

通过投影几何将 2D 掩码提升至 3D。对于每个视角，我们使用相机参数和深度图把 3D 点投影到像素上，然后查询 2D 分割掩码，以得到 3D 点的分割标签。我们合并全部视角中这些已分割的 3D 点，获得将物体完整划分为其语义部件的 3D 分割。可能较稀疏的已分割点云通过最近邻匹配用于分割稠密网格。现在物体已正确完成 3D 分割，我们便可如前应用 **ARTICULATE-ANYTHING**。所得 3D 物体不仅拥有与真值匹配的高材质质量，而且在仿真中 articulation 后也会呈现真实的运动。视频演示请参见项目网站。
