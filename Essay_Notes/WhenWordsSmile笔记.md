## 一、摘要

本文提出了 **CTEG**（Continuous Text-to-Expression Generator），首个端到端的文本到 3D 面部表情生成模型。与现有管线式方法（先情感分析得离散标签，再基于标签生成表情）不同，CTEG 采用基于 CVAE 的自回归架构，在**连续隐空间**中学习表情变化，能够生成**多样化、时序流畅且情感一致**的面部表情序列。为支撑该任务，作者构建了 **EmoAva**——一个包含 **15,000** 条文本-3D 表情对的大规模高质量数据集，从影视剧多角色对话场景中采集，覆盖超过 100 部影视作品。实验表明，CTEG 在表情多样性、自然度和情感一致性等多个维度上显著超越现有基线。

---

## 二、背景

### 2.1 问题与动机

数字人（talking head）研究长期聚焦于**语音-唇形同步**，忽略了面部表情的丰富情感动态。现有方法通常采用**管线式架构**：

$$\text{文本} \xrightarrow{\text{情感分析}} \text{离散情绪标签} \xrightarrow{\text{条件生成}} \text{面部表情}$$

这种范式存在两大局限：

1. **离散标签表达能力不足**：有限的情绪类别（如"高兴""悲伤"）无法捕捉人类情感的全部丰富性与微妙差异。
2. **管线信息损失**：分阶段处理导致信息丢失和误差传播，且无法建模文本与表情之间的**一对多映射**关系（同一句话不同人说、不同语境说，表情完全不同）。

### 2.2 现有工作局限

| 方法/数据集                       | 局限                            |
| ---------------------------- | ----------------------------- |
| EMOTE、EmoTalk3D              | 基于离散情绪标签，表情粗粒度                |
| EmoTalk、LaughTalk            | 从语音提取情绪特征，未直接利用文本语义           |
| LM-Listener（Ng et al., 2023） | 仅面向听者表情；VQ-VAE 离散建模，时序一致性受限   |
| 现有数据集                        | 规模小、角色单一、缺乏一对多映射（$N$ 最大仅到 76） |

### 2.3 本文定位

**首次**提出端到端的文本到 3D 表情生成，采用 **CVAE 连续隐空间**建模，天然支持一对多映射，同时保证表情的流畅性与多样性。

---

## 三、方法

### 3.1 任务定义

给定文本输入 $x$，模型生成 $T$ 个时间步的表情向量序列：

$$\psi = \{E_0, E_1, \dots, E_T\}$$

每个 $E_t \in \mathbb{R}^{d}$（$d = 53$）来自 FLAME 3D 人脸模型的表情参数，FLAME 将人脸参数化解耦为：

$$F = \{\beta, \Delta v, \varrho, \Theta, \psi\}$$

其中 $\beta$ 为形状参数，$\Delta v$ 为顶点偏移，$\varrho$ 为全局平移，$\Theta$ 为关节姿态，$\psi$ 为**表情相关形变**。由于表情与形状及身份因素解耦，模型可以以**身份无关**（identity-agnostic）的方式直接回归 $\psi \in \mathbb{R}^{53}$。

### 3.2 整体架构

CTEG 由两大核心模块组成：

- **编码侧**：**EwA**（Expression-wise Attention，表情级注意力模块）——增强面部单元间的空间关联
- **解码侧**：**CVAD**（Conditional Variational Autoregressive Decoder，条件变分自回归解码器）——CVAE 与 Transformer 解码器的混合体

选择该架构的三重动机：
1. **CVAE** 的连续隐空间有利于表情流畅性
2. **Transformer 解码器**的自注意力机制擅长建模序列间的长程依赖，有利于情感-内容一致性
3. **变分自回归解码**（VAD）适合建模每个时间步内都有无数变化可能的表情序列

### 3.3 表情级注意力模块（EwA）

人脸的各个单元是一个整体。例如大笑时下颌张开，同时影响眼部和脸颊。为建立面部区域间的连接，EwA 将原始表情向量 $E$ 拆分为两部分：

- $E_j$：下颌部分
- $E_f$：下颌以上部分

通过投影层映射到隐空间后，以转换后的 $E_j$ 为查询（Query），$E_f$ 为键（Key）和值（Value），进行交叉注意力计算，得到增强后的下颌特征 $E_j' \in \mathbb{R}^{|E_j|}$。最终重组后的表情编码为：

$$E' = \text{Concat}\big(E_f,\; E_j + E_j'\big) \in \mathbb{R}^{|E|}$$

再将 $E'$ 投影到高维空间 $d_{\text{model}}$，并加上正弦位置编码（PE）以捕获序列顺序信息。

### 3.4 条件变分自回归解码器（CVAD）

#### 3.4.1 生成模型分解

CVAD 的目标是最大化条件对数似然 $\log p(\psi \mid x)$。为更好地捕捉时序动态，将联合分布分解为逐步条件概率，并显式建模历史隐状态：

$$p(\psi \mid z, x) = \prod_{t=1}^{T} p\big(\psi_t \mid \psi_{<t},\, z_t,\, x\big) = \prod_{t=1}^{T} p\big(\psi_t \mid \psi_{<t},\, f_\zeta(z_{<t}),\, x\big) \tag{1}$$

其中 $f_\zeta$ 为 **LTA**（Latent Temporal Attention，隐变量时序注意力）模块，通过遮蔽多头注意力（masked multi-head attention）实现——第 $t$ 步只能关注 $1$ 到 $t-1$ 步的隐状态，使当前时刻的隐表示融合历史情感上下文，增强情感-内容一致性。

#### 3.4.2 先验与后验分布

假设先验分布 $P_\theta$ 和后验分布 $Q_\phi$ 均为**多元高斯分布**：

$$Q_\phi(z_t \mid \psi_{\leq t}, x) = \mathcal{N}\big(\mu_r(\psi_{\leq t}, x),\; \sigma_r(\psi_{\leq t}, x)\big) \tag{2}$$

$$P_\theta(z_t \mid \psi_{<t}, x) = \mathcal{N}\big(\mu_p(\psi_{<t}, x),\; \sigma_p(\psi_{<t}, x)\big)$$

两者的关键在于条件范围不同：$Q_\phi$ 以当前及历史表情 $\psi_{\leq t}$ 为条件（训练时可用，因为已知真实表情），$P_\theta$ 仅以历史表情 $\psi_{<t}$ 为条件（推理时只能依赖已生成的部分）。

两个高斯分布分别由两个神经网络参数化：

$$[\mu_r, \sigma_r] = \big[h_r^\mu(o),\; h_r^\sigma(o)\big],\quad [\mu_p, \sigma_p] = \big[h_p^\mu(o),\; h_p^\sigma(o)\big] \tag{3}$$

$$o = A_{\text{mask}}\big[A(\psi_{\leq t},\, x)\big]$$

其中 $h$ 为线性层，$A_{\text{mask}}$ 为遮蔽注意力模块（masked attention），$A$ 为交叉注意力模块（cross attention）。

#### 3.4.3 重参数化技巧

由于从分布中采样不可导，采用重参数化技巧使梯度能回传：

$$z_t = \mu_t + \sigma_t \odot \epsilon,\quad \epsilon \sim \mathcal{N}(0, I) \tag{4}$$

其中 $\odot$ 表示逐元素乘法。**训练阶段** $z_t$ 从后验分布 $Q_\phi(z_t \mid \psi_{\leq t}, x)$ 采样，**推理阶段**则从先验分布 $P_\theta(z_t \mid \psi_{<t}, x)$ 采样——因为推理时没有真实 $\psi_t$ 可用。

#### 3.4.4 生成网络

获得采样后的 $z_t$，学习第二条件生成分布 $P_\theta(\psi_t \mid \psi_{<t}, z_t, x)$。同样假设为多元高斯分布，仅参数化均值 $\mu^g$（方差固定为全 1 矩阵）：

$$\mu_t^g = \text{FFN}\Big(\text{Concat}\big(A(o_1), A(o_2), \dots, A(o_l)\big)\Big) \tag{5}$$

$$A(o_i) = A\big((\psi_{<t} + z_{<t})W_i^Q,\; xW_i^K,\; xW_i^V\big)$$

其中 $l$ 为交叉注意力头数，$W_i^Q, W_i^K, W_i^V$ 为第 $i$ 个注意力头的投影矩阵，FFN 为位置前馈网络。多层堆叠时，第 $m$ 层的输入采样自 $\mathcal{N}(\mu_g^{m-1}, \sigma)$。最终通过重参数化采样得到预测表情：

$$\hat{\psi}_t = \mu_t^{m,g} + \epsilon,\quad \epsilon \sim \mathcal{N}(0, I)$$

### 3.5 损失函数

CVAD 的损失由重构误差与 KL 散度组成：

$$\mathcal{L}_{\text{CVAD}} = \sum_t \mathcal{L}_{\text{rec}}(\psi_t, \hat{\psi}_t) + \sum_t \mathcal{L}_{\text{KL}}(t) \tag{6}$$

其中 $\mathcal{L}_{\text{rec}}$ 为均方误差（MSE），KL 散度项用于约束后验分布逼近先验分布：

$$\mathcal{L}_{\text{KL}}(t) = \text{KL}\Big(Q_\phi(z_t \mid \psi_{\leq t}, x) \;\big\|\; P_\theta(z_t \mid \psi_{<t}, x)\Big) \tag{7}$$

### 3.6 目标引导损失（Target Guided Loss）

CVAE 存在一个臭名昭著的问题——**模型坍塌**（KL 项 $\to 0$，隐变量被解码器忽略）。常见缓解方法（调整 KL 权重）需要针对具体训练过程精细调参，在大数据集或大模型上极为耗时。为此，本文设计了一个简洁而有效的目标引导损失 $\mathcal{L}_g$：

$$\mathcal{L}_g = \sum_t \mathcal{L}_{\text{rec}}\big(\psi_t,\; f_\gamma(o_t)\big) \tag{8}$$

$$o_t = \sum_{i=1}^{N_c} \text{FFN}_i(z_{<t}^i)$$

其中 $f_\gamma$ 为一个线性投影层，$N_c$ 为 CVAD 层数。该损失的核心思想是：**强制隐变量本身也能直接预测表情**，从而引导隐变量学习有意义的结构，防止被解码器彻底忽略。

### 3.7 总损失与训练细节

总损失函数为两者之和：

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{CVAD}} + \mathcal{L}_g \tag{9}$$

关键训练配置：
- 冻结预训练语言模型 BERT（`bert-base-cased`，最后隐状态，$d_{\text{model}} = 768$）
- 教师强制（teacher forcing）并行训练，推理时逐帧自回归解码
- Adam 优化器，100 epoch，最大表情序列长度 256，最大句子长度 128
- 预热步数 $\text{warmup} = 4000$，学习率调度：

$$lr = d_{\text{model}}^{-0.5} \cdot \min\big(\text{step}^{-0.5},\; \text{step} \cdot \text{warmup}^{-1.5}\big) \tag{10}$$

- 注意力头数 12，FFN 隐层维度 2048，单层 CVAD（$N_c = 1$）
- 残差连接 + 层归一化贯穿整个架构
- 总参数量 < 130M，单卡 NVIDIA A100

### 3.8 推理策略

- 序列前添加训练集平均表情作为平滑起始
- 以全零向量作为"标准脸"终止符，推理时当预测表情与标准脸的欧氏距离低于阈值（如 1.0）时停止解码
- 辅以最大序列长度（MSL）约束解码，防止无限生成

### 3.9 EmoAva 数据集

| 特征 | 数据 |
|------|------|
| 总实例数 | 15,000（训练/验证/测试 = 12,000/1,500/1,500） |
| 总 FLAME 帧数 | 782,471 |
| 一对多实例 | 2,270 条（$N$ 从 2 到 76，占比 > 15%） |
| 来源 | MELD + MEMOR + YouTube，超 100 部影视作品 |
| 平均句子长度 | 14 词 |
| 平均表情步数 | 52 帧 |
| 多情绪序列占比 | > 95%（单序列含两种及以上情绪） |

**构建流程**：原始视频 $\to$ WhisperX 语音转录（得文本 + 时间戳） $\to$ 按时戳裁剪 $\to$ FaceNet 面部追踪 + 人工修正 $\to$ EMOCA-v2 提取 FLAME 3D 表情系数 $\to$ 三名标注员独立审核 + 多数投票（Fleiss' $\kappa = 0.86$）。

### 3.10 评价指标

| 指标 | 含义 | 公式 |
|------|------|------|
| **Diversity** | 无条件生成序列间的平均欧氏距离 | $\text{Diversity} = \frac{1}{N_d}\sum_{i=1}^{N_d}\|\Psi_i - \Psi_i'\|$ |
| **MModality** | 同一文本两次生成间的平均欧氏距离 | $\text{MModality} = \frac{1}{N_m}\sum_{i=1}^{N_m}\|\psi_i - \psi_i'\|$ |
| **Variation** | 序列内部逐帧方差均值 | $\text{Variation} = \frac{1}{N_v}\sum_i \frac{1}{n_i}\sum_j \text{var}(E_{ij})$ |
| **FgD** | 相邻帧间平均欧氏距离（细粒度变化） | $\text{FgD} = \frac{1}{(T-1)N}\sum_i \sum_j \|E_{i,j+1} - E_{i,j}\|$ |
| **DoT** | 测试集所有生成序列两两间平均距离 | $\text{DoT} = \frac{2}{N(N-1)}\sum_{i<j}\|E_i - E_j\|$ |
| **Cppl** | 连续空间困惑度（衡量序列平滑性） | $\text{Cppl} = 2^{\frac{1}{N}\sum_i H_i(\xi)}$，其中 $H_i(\xi) \approx -\frac{1}{T}\sum_j \log_2 p_\xi(\psi_j^i \mid \psi_{<j}^i, x)$ |
| **Consistency** | 情感-内容一致性 | 人工评测（5 名参与者，Fleiss' $\kappa = 0.77$） |

其中 Cppl 中的条件分布 $p_\xi$ 通过多元正态分布的累积分布函数（CDF）近似计算：

$$p_\xi(\psi_j \mid \psi_{<j}, x) \approx \Phi(x + \delta; \mu_\xi^j, \sigma^2 I) - \Phi(x - \delta; \mu_\xi^j, \sigma^2 I)$$

$\delta = 0.8$，$\sigma = 0.2$ 为经验值。

---

## 四、结论

### 4.1 主要贡献

1. **CTEG 模型**：首个端到端的文本到 3D 表情生成模型，在连续隐空间中建模表情变化，生成多样化、流畅且情感一致的表情序列。

2. **EmoAva 数据集**：15,000 条高质量文本-3D 表情对，覆盖多角色对话场景，包含丰富的一对多映射，填补了该领域的数据稀缺。

3. **充分实验验证**：CTEG 在所有多样性指标上大幅超越 LM-Listener 基线，人工评测也证实其在情感-内容一致性上的优势。

### 4.2 关键实验发现

| 消融实验 | 结论 |
|----------|------|
| 移除 EwA | 四项多样性指标（DoT、FgD、Diversity、MModality）显著下降；隐空间聚类从 **146 降到 113**（降 29%） |
| 移除 LTA | 情感-内容一致性下降，验证历史隐状态建模对跨时间步情感连贯的重要性 |
| 移除 $\mathcal{L}_g$ | KL 项快速趋零（模型坍塌），除 Variation 外所有指标恶化，Cppl 从 262 暴增至 646 |
| 多层 CVAD（2-5 层） | 出现**累积采样不稳定性**——$N$ 层产生 $sN$ 个隐状态，随机性过大，单层最优 |

### 4.3 局限与展望

- **语言覆盖有限**：EmoAva 目前仅支持英语，但作者认为情感表达的普遍性使跨语言扩展具备可行性
- **缺乏个性化建模**：身份无关设计利于泛化，但无法捕捉个体的表达风格——这是作者有意为之的"先打基础再谈个性化"策略
- **偶发异常帧**：训练数据中罕见的帧间剧烈变化可能导致下颌运动过夸张，未来计划引入异常检测或插值平滑策略

---

> **个人评注**：CTEG 的核心设计哲学是**用连续隐空间取代离散标签的级联**。相比 KeyframeFace 的"关键帧 + LLM 微调"范式和 Express4D 的"简短提示 + 扩散模型"路径，CTEG 走的是"变分自回归 + Transformer"的端到端路线。其三大创新组件——EwA（面部区域交互）、LTA（历史隐状态建模）、$\mathcal{L}_g$（抗坍塌引导损失）——层层递进地解决了表情多样性、时序一致性和训练稳定性三个关键问题。特别是 $\mathcal{L}_g$ 以极简设计（仅一个线性投影层 $f_\gamma$）有效抑制了 CVAE 的 KL 消失问题，其机理是**让隐变量自身也承担预测任务**，从而防止被解码器边缘化——这一技巧对其他变分自编码器任务也具有参考价值。三篇论文横向对比可以看到该领域的三种范式：CTEG（连续隐空间 + 自回归）、Express4D（扩散模型 + 简短提示）、KeyframeFace（LLM 微调 + 关键帧），分别面向多样性、可扩展性和可控性三个不同的优化方向。