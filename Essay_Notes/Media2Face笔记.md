## Media2Face 概要

**Media2Face** 是一个用于共语面部动画（co-speech facial animation）生成的多模态条件扩散模型。它接受语音音频、文本描述或图像提示，生成高质量的 3D 面部表情及头部姿态，旨在为虚拟数字人提供真实、情感丰富且风格可控的实时交互能力。

该工作的核心创新在于提出了一种 **三部曲方案**：

1. **GNPFA（广义神经参数化面部资产）**：一种基于 VAE 的潜在表示，能从多种扫描数据中解耦身份与表情，并高效地从野生视频中提取高质量的面部动作。
2. **M2F‑D 数据集**：利用 GNPFA 从大量带有情绪和风格标签的视频中提取数据，构建了超过 60 小时的、扫描质量的 4D 面部动画数据集。
3. **Media2Face 扩散模型**：在 GNPFA 的隐空间中进行生成，接受音频（Wav2Vec2）、文本或图像（CLIP）等多模态条件，并通过分类器自由引导实现精细控制。

---

## 方法（Method）详解

![830](../attachments/Pasted%20image%2020260520024347.png)

### 1. GNPFA – 面部表情的潜在空间构建

GNPFA 由几何 VAE 和视觉编码器组成，旨在学习一个**与身份无关的表情潜在空间**。

#### 1.1 几何 VAE（Geometry VAE）
**几何生成器**使用UNet架构，证据如下：
![](../attachments/Pasted%20image%2020260519233806.png)
##### 训练$G_R$
- **输入**：某帧的面部几何体 $\mathbf{G}_R$ 及其对应的中性几何体 $\overline{\mathbf{G}}_R$（同一角色无表情状态）。
- **编码**：表情潜码 $\mathbf{z}_R = E_\text{geo}(\mathbf{G}_R)$。$E_\text{geo}$是**几何编码器**。
- **解码**：重构面部 $\tilde{\mathbf{G}}_R = G_\text{geo}(\overline{\mathbf{G}}_R, \mathbf{z}_R)$。$G_{geo}$是**几何生成器（解码器）**。
- **重建损失**：

$$
\mathcal{L}_{\text{recon},R} = \| \tilde{\mathbf{G}}_R - \mathbf{G}_R \|_2^2 \tag{1}
$$

同时训练两个映射网络 $M$ 和 $M'$，以兼容传统 blendshape 动画：
>[!Quote]
>“为了支持传统的混合形状动画，我们训练两个映射网络 $M$ 和 $M^′$，其中前者将混合形状的权重 $w$ 映射到我们的潜在空间，后者则进行相反的操作。”
- 从 blendshape 权重 $\mathbf{w}_B$ 映射到潜空间：$\tilde{\mathbf{z}}_B = M_\text{geo}(\mathbf{w}_B)$
- 用 $G_\text{geo}$ 重构 $\tilde{\mathbf{G}}_B = G_\text{geo}(\overline{\mathbf{G}}_B, \mathbf{z}_B)$，并反向映射 $\tilde{\mathbf{w}}_B = M'(\tilde{\mathbf{z}}_B)$
- **综合损失**：

$$
\mathcal{L}_{\text{recon},B} = \| \tilde{\mathbf{G}}_B - \mathbf{G}_B \|_2^2 
+ \| \tilde{\mathbf{z}}_B - \mathbf{z}_B \|_2^2 
+ \| \tilde{\mathbf{w}}_B - \mathbf{w}_B \|_2^2 \tag{2}
$$

其中 $\mathbf{G}_B$ 是通过个人 blendshape 与权重 $\mathbf{w}_B$ 变形得到的几何体。
> [!Quote]
> “我们使用坐标图来表示几何形状，它存储 UV 空间中 2D 几何图上每个顶点的 3D 位置。可以使用固定拓扑将该表示形式与网格表示形式相互转换。除了与 CG 兼容之外，由于其非线性和顶点级粒度，它还创建了比现有参数化面部模型更真实、更可信的动画空间。”
#### 1.2 视觉编码器（提取表情与头部姿态）
利用真实扫描图像和随机合成的 blendshape 图像训练两个视觉编码器 $E_\text{exp}$ 和 $E_\text{pose}$，分别用来从**RGB图像**中提取 **表情的潜在代码** 和 **头部的姿势（角度）**：
- **表情潜码**：$\hat{\mathbf{z}}_R = E_\text{exp}(\mathbf{I}_R)$
- **头部姿态**：$\hat{\mathbf{p}}_R = E_\text{pose}(\mathbf{I}_R)$
- **渲染对比**：通过可微渲染器 $\mathcal{R}$ 获得预测图像 $\hat{\mathbf{I}}_R = \mathcal{R}(\hat{\mathbf{G}}_R, \hat{\mathbf{p}}_R)$，其中 $\hat{\mathbf{G}}_R = G_\text{geo}(\overline{\mathbf{G}}_R, \hat{\mathbf{z}}_R)$
- **训练损失**：

$$
\mathcal{L}_{\text{exp},R} = \| \tilde{\mathbf{G}}_R - \mathbf{G}_R \|_2^2 
+ \| \hat{\mathbf{I}}_R - \mathbf{I}_R \|_2^2 \tag{3}
$$

对合成 blendshape 图像同样计算 $\mathcal{L}_{\text{exp},B}$。

完成后，GNPFA 即可从任意野生视频帧提取表情潜码 $\mathbf{z}_e$ 和头部姿态 $\boldsymbol{\theta}$，用于构建大规模高质量的 M2F‑D 数据集。
> - $G_R$和$\overline{G_R}$来自于文中所说的Range of Motion（RoM）数据集。
> - 几何VAE的Encoder和Decoder就是$E_{geo}$和$G_{geo}$。
> - 个性化blendshape基建立在RoM扫描上（***从数据集的几个身份中抽取200个身份***），但随机权重$w_B$本身是数学生成，与RoM原始样本无关。因此$w_B$和随之得到的$G_B$是随机生成的。从RoM数据集中挑选一些ID，按照FACS标准随机生成一个K维向量$w_B$，权重元素值从合理值里选取。这样用随机数生成的数据可以算是一种数据增强。然后把权重矩阵送到$M$里，得到一个预测的潜在空间的表示$\tilde{\mathbf{z}}_B$；$G_B$送到预训练的$E_{geo}$里得到真值$z_B$。后面是用$M'$来重建$\tilde{w}_B$。所以$M$和$M'$其实就相当于这个场景下的**双向翻译器**（`weight <-> latent space`）。

---

![874](../attachments/Pasted%20image%2020260519230825.png)
### 2. Media2Face 扩散模型 – 多模态条件生成

Media2Face 是一个基于 Transformer 的潜在扩散模型（**DiT Model**），可调节多模态驱动信号。它对连续头部姿势和面部表情的联合分布进行建模，即完整的面部动画，从而促进姿势和表情的自然协同。它还采用多条件引导，通过 CLIP 引导的风格化和基于图像的关键帧编辑实现高度一致的协同语音面部动画合成。

#### 2.1 序列表示
对于每一帧 $i$，将表情潜码 $\mathbf{z}_e^i$ 与头部姿态 $\boldsymbol{\theta}^i$ 拼接为一个状态向量：
$$
\mathbf{x}_i = [\mathbf{z}_e^i, \boldsymbol{\theta}^i]
$$
动画序列表示为 $\mathbf{X}_{1:N} = [\mathbf{x}_i]_{i=1}^N$。
> [!Quote]
> 在扩散模型中，生成被建模为马尔可夫去噪过程。
> > - 扩散模型里，**正向过程**是加噪声，对干净数据$X_0$不断添加高斯噪声，直到变成一个噪声图$X_T$；**反向过程**是逆向还原，训练一个Denoiser网络，从乱码图像$X_T$猜测原本的图像，层层减噪声，从$X_i$得到$X_{i-1}$。神经网络一层层抹去噪声之后，最后就**生成**了一个符合数据分布的照片$X_0$。
> > - 是一个**迭代**的过程，每一步去噪只依赖当前步的噪声分布（$X_i$），这符合马尔可夫链的无记忆特性。
#### 2.2 多模态条件
- **音频**：原始波形通过 Wav2Vec2 提取特征，线性插值到与序列等长，得到 $\mathbf{A}_{1:N}$。
- **风格/情绪**：文本或图像提示由 CLIP 编码为统一的隐向量 $\mathbf{P}$。

#### 2.3 去噪 Transformer 与训练目标
扩散前向过程向干净序列 $\mathbf{X}_{1:N}^0$ 加噪得到 $\mathbf{X}_{1:N}^t$，模型 $G$ 直接预测干净序列：
$$
\hat{\mathbf{X}}_{1:N}^0 = G\bigl( \mathbf{X}_{1:N}^t, \; t, \; \mathbf{A}_{1:N}, \; \mathbf{P} \bigr) \tag{4}
$$

优化目标包含三项损失：
1. **简单损失**（Simple loss）：
   $$
   \mathcal{L}_{\text{simple}} = \| \mathbf{X}_{1:N}^0 - \hat{\mathbf{X}}_{1:N}^0 \|_2^2 \tag{5}
   $$
2. **速度损失**（Velocity loss），保证帧间变化真实：（一阶差分）
   $$
   \mathcal{L}_{\text{velocity}} = \big\| (\mathbf{X}_{2:N}^0 - \mathbf{X}_{1:N-1}^0) - (\hat{\mathbf{X}}_{2:N}^0 - \hat{\mathbf{X}}_{1:N-1}^0) \big\|_2^2 \tag{6}
   $$
3. **平滑损失**（Smooth loss），抑制加速度突变：（二阶差分）
   $$
   \mathcal{L}_{\text{smooth}} = \big\| \hat{\mathbf{X}}_{3:N}^0 + \hat{\mathbf{X}}_{1:N-2}^0 - 2\hat{\mathbf{X}}_{2:N-1}^0 \big\|_2^2 \tag{7}
   $$

总损失为加权和：
$$
\mathcal{L} = \lambda_{\text{simple}} \mathcal{L}_{\text{simple}} 
+ \lambda_{\text{velocity}} \mathcal{L}_{\text{velocity}} 
+ \lambda_{\text{smooth}} \mathcal{L}_{\text{smooth}} \tag{8}
$$

训练过程中对 $\mathbf{P}$ 和 $\mathbf{A}_{1:N}$ 分别施加随机掩码，使模型学会无条件和有条件去噪。

#### 2.4 推理与分类器自由引导
推理时，利用 CFG （**Classifier-Free Guidance**）分别控制 **语音同步强度** $s_A$ 和 **风格引导强度** $s_P$：
$$
\hat{\mathbf{X}}_{1:N}^0 = 
(1 - s_A - s_P) \cdot G(\mathbf{X}_{1:N}^t, t)
+ s_A \cdot G(\mathbf{X}_{1:N}^t, t, \mathbf{A}_{1:N})
+ s_P \cdot G(\mathbf{X}_{1:N}^t, t, \mathbf{A}_{1:N}, \mathbf{P}) \tag{9}
$$
通过调节两个标量，可在无表情、纯语音匹配与高风格化之间平滑过渡。

#### 2.5 推理加速与可控编辑
- **重叠批处理去噪**：将长音频切分重叠窗口并行去噪，大幅降低延迟。
- **关键帧编辑**：用 GNPFA 提取目标帧的潜码，结合扩散修补进行局部替换。
- **CLIP 指导的逐帧风格编辑**：为不同帧指定不同的文本/图像提示，利用梯度掩码实现段落内的情感渐变。

---

### 3. 算法流程（伪代码）

```
【训练阶段】
1. 在 RoM 扫描数据上训练 GNPFA（几何 VAE + 映射网络 M, M'）。
2. 冻结几何部分，用 RGB 图像训练视觉编码器 E_exp, E_pose。
3. 用 GNPFA 从大量野生视频中提取 (z_e, θ) → 构建 M2F-D 数据集。
4. 训练扩散模型：
   - 从 M2F-D 采样序列 X_{1:n}，提取音频特征 A_{1:n}，CLIP 编码得到 P。
   - 随机掩码条件，计算式(5)–(8)总损失，反向传播更新去噪器 G。

【推理阶段】
输入：原始音频 A，可选文本/图像提示 Prompt。
1. 用 Wav2Vec2 编码音频 → A_{1:n}，用 CLIP 编码 Prompt → P。
2. 从高斯噪声初始化 X_{1:n}^T。
3. for t = T down to 1 do:
      根据式(9)计算 X̂_{1:n}^0
      通过 DDIM 采样得到 X_{1:n}^{t-1}
4. 从最终生成的状态序列中分离表情潜码 ẑ_e 和头部姿态 θ̂。
5. 将 ẑ_e 输入 GNPFA 解码器 G_geo，联合目标角色的 neutral geometry 生成网格。
6. 结合 θ̂ 渲染出动画帧序列。
```
---
## 总结
Media2Face 通过 **GNPFA** 解决了高质量面部数据稀缺的问题，并在其隐空间中训练了一个**多模态条件扩散模型**，实现了音频、文本、图像的灵活混合控制。该方法在唇形同步精度、表情真实感和头部姿态自然度上均显著超越了现有方法，且支持实时推理与细粒度编辑，为虚拟陪伴、对话式 AI 等场景奠定了坚实的技术基础。