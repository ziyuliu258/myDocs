## Abstract
长期时间序列预测在许多关键领域都是至关重要的，但其准确性仍然受到现有模型的感受野瓶颈的根本制约。主流的基于Transformer和多层感知器( MLP )的方法主要依赖于**有限的回溯窗口**，限制了它们对**长期依赖关系**的建模能力，损害了预测性能。自然地扩展回视窗口是无效的，因为它不仅引入了令人望而却步的计算复杂度，而且淹没了历史噪声中至关重要的长期依赖关系。为了应对这些挑战，作者提出了CometNet，一个新颖的**上下文模体指导（Contextual Motif-guided）的长期时间序列预测框架**。 CometNet首先引入了一个上下文模体**提取模块**，该模块从复杂的历史序列中识别出循环的、占主导地位的上下文模体，提供了远远超过有限的回视窗口的广泛的时间依赖；随后，提出了一种基于模体引导的**预测模块**，将提取的主导模体整合到预测中。通过动态地将回溯窗口映射到其相关模体，CometNet有效地利用了它们的上下文信息，以加强长期预测能力。在8个真实世界数据集上的大量实验结果表明，CometNet显著优于当前最先进的方法( SOTA )，特别是在扩展预测范围上。

## Introduction

### 接收域瓶颈（Receptive Field Bottleneck）
#### 有限长度回溯窗口
以往的模型都是使用有限的回溯窗口数据来预测未来序列特征的，这样有限的时间窗口会天然地把连续的时间序列切割成上下文无关的、离散的时间片，因此限制了学习序列长程依赖的能力。
#### 滑动窗口方法的局限
滑动窗口虽然可以遍历整个序列，但是它的梯度传播是局限于窗口之内的，因此阻断了长期依赖的梯度传递。
#### 单纯扩大接收域为什么不好
- 好处：性能提升；
- 坏处：
	- 时间复杂度有指数级的增长；
	- 会引入历史噪声，从而淹没某些时域的特征；
### 解决：上下文特征（Contextual Motifs）
>不知道如何翻译motifs这个词，其本意是图画/文学作品中反复出现的主导性的事物（意象）。
#### 阐释
真实世界的序列往往被一些反复出现的、具有代表性的上下文特征决定，如工厂生产周期/季节性气候变化。
#### 模型
CometNet，基于上下文特征引导的时序预测网络，把上下文特征整合到预测过程中。包括两个核心模块：
##### 上下文特征提取模块
扫描整个序列，提取出来**上下文特征库**。
##### 特征引导预测模块
从特征库里选择和回溯窗口最相关的特征，然后将其用于预测未来。

> 总结而言，文章作者说这样的一个上下文特征可以跳出回溯窗口的局限，能考虑到全局的特点。
## Method

### 模型结构

![](../attachments/Pasted%20image%2020260118120015.png)
采用了 **通道无关** 策略，$N$个通道就是$N$个独立的序列：
<img src="../attachments/Pasted%20image%2020260118120835.png" style="zoom:50%;" />
下文直接把每个通道的通道索引上标省略。

#### Motif库建立
<img src="../attachments/Pasted%20image%2020260118121216.png" style="zoom:50%;" />
<img src="../attachments/Pasted%20image%2020260118121332.png" style="zoom:50%;" />
这个$M$就是Motif库，取`top_k`个元素。

#### 预测模块

每个motif对应一个网络（MoE），采用**门控机制**，把输入和库$M$中最相关的motif $m_k$关联，然后激活对应的网络来预测。
<img src="../attachments/Pasted%20image%2020260118121859.png" style="zoom:50%;" />

### Contextual Motif Extraction
分为三个模块：**multi-scale candidate discovery, cross-scale redundancy filtering, and benefit-driven selection**
#### Multi-scale Candidate Discovery
<img src="../attachments/Pasted%20image%2020260118124032.png" style="zoom:50%;" />

>先moving average，得出 **去趋势** 的序列$X^{det}$（此处猜测应该是用原序列减去移动平均后的序列得到周期序列），然后再做一个FFT。

选定$top-N_s$个周期$\Lambda=\{\lambda_{1},\lambda_{2},\cdot\cdot\cdot,\lambda_{N_{s}}\}$，关于每个周期的处理，先**对序列下采样**，然后再随机选$N_r$个时间点作为中心点，提取出$N_r$个长度为$\lambda_i$的patch，计算彼此之间的相似度/相关系数，形成皮尔逊相关系数矩阵，文中称被随机选取出来的点是 **“锚点（anchor）”** 。对于每个锚点，计算密度系数，公式如下：
<img src="../attachments/Pasted%20image%2020260118134302.png" style="zoom:50%;" />

>就是对相关系数做了一个筛选（threshold）。

通过计算密度分数，选择前 $N_{c}$ 个锚点作为聚类质心，形成 $N_{c}$ 个簇。 从每个簇中，选择最具代表性的子序列（中心点，Medoid）作为候选模态，这个中心点的度量标准是采用动态时间规整（DTW）实现的，在下一个小模块里详述。 此过程产生候选模态集 $\mathcal{C}=\bigcup_{s=1}^{N_{s}}C_{s}$。

>这个候选集是针对单通道的，是一个通道的数据的所有尺度的候选模态。而$top-N_s$个尺度（对应不同的$top-N_s$周期）中每个尺度都对应一个**候选中心点集**$C_s$。
#### Cross-scale Redundancy Filtering
基本步骤如下：
- 构建一个无向图，每个顶点就是$\mathcal{C}$的一个候选模态，包含了一个通道的所有尺度的候选中心点。
- **边的权重**由DTW相似度分数决定，带一个threshold来对图的稀疏度做约束；
	<img src="../attachments/Pasted%20image%2020260118141830.png" style="zoom:50%;" />
- 按照权重计算的结果，来把图分成几个**连通分量**$\{\mathcal{G}_1, \mathcal{G}_2, \cdots, \mathcal{G}_{N_g}\}$，$\mathcal{G_i}=\mathcal{(V_i, E_i)}$。这样的分组就可以解决特征尺度/位置不对齐的情况了；
- 每个连通分量内部，计算其中每个patch的**簇内亲和力**，然后选出最高的那个patch作为这个连通分量的代表，文章称为**原型（Prototype）**，符号为$c^*_k$。这个亲和力依旧通过DTW结果给出，公式如下：
	<img src="../attachments/Pasted%20image%2020260118142716.png" style="zoom:50%;" />
	最后所有连通分量的原型组成最终的候选集合$\mathcal{C^*}$。文章认为这样的一个过程能够过滤冗余motif，保留具有代表性的选择。
#### Dominant Motif Selection
作者称他们的这个motif选择策略是“a benefit-driven selection strategy”，从以上的候选集合$\mathcal{C^*}$之中选出最后的主导motif。
- 首先对候选集合$\mathcal{C^*}$之中每个元素做一个内在质量评价：
	<img src="../attachments/Pasted%20image%2020260118143508.png" style="zoom:50%;" />
	
	><img src="../attachments/Pasted%20image%2020260118143601.png" style="zoom:50%;" />
	>三个名词的意思分别为“显著性”“流行度”“原子性”。
	>
	>- 显著性
	><img src="../attachments/Pasted%20image%2020260118151510.png" style="zoom:50%;" />
	>可以理解为**峰度**；
	>- 流行度
	><img src="../attachments/Pasted%20image%2020260118151553.png" style="zoom:50%;" />
	>- 原子性
	><img src="../attachments/Pasted%20image%2020260118151605.png" style="zoom:50%;" />
	>越简洁越好，泛化能力就越强。
- 然后作者又提出一个效益得分，公式如下：
	<img src="../attachments/Pasted%20image%2020260118144124.png" style="zoom: 50%;" />
	
	- 边际覆盖度 (Marginal Coverage, $Cov$)
		<img src="../attachments/Pasted%20image%2020260118145833.png" style="zoom:50%;" />
	- 边际多样性 (Marginal Diversity, $Div$)
		<img src="../attachments/Pasted%20image%2020260118145929.png" style="zoom:50%;" />
		迭代选择效益分数最高的候选者，构建出平衡了代表性、覆盖面和多样性的模态库 $\mathcal{M}$ 。这种策略实际上是**贪心**的，不能保证全局最优，但是能够降低对于NP难问题的处理时间。

### Motif-guided Forecasting

核心是类似**MoE**的思想。
#### Window Embedding

给定回顾窗口 $X_{t-L+1:t}$，首先通过 MLP 将其映射为紧凑的潜在表示 $e_{t}\in \mathbb{R}^{d_{v}}$：$$e_{t}=LayerNorm(MLP(X_{t-L+1:t}))$$
#### Gating Networks
该网络接收 $e_{t}$ 作为输入，动态地将当前观察与相关上下文模态关联。 门控网络包含两个并行头部：
- 路由头 $H_{route}$ 通过 Softmax 生成专家选择概率分布 $p_{t}\in\mathbb{R}^{K}$ ；
- 位置头 $H_{pos}$ 通过 Sigmoid 生成标量值 $s_{t}\in[0,1]$ ，编码当前观察在模态生命周期中的相对位置。
#### Context-conditioned Experts
- 框架包含 $K$ 个独立的上下文条件专家网络 $\{E_{1},\cdot\cdot\cdot,E_{K}\}$。每个专家 $E_{k}$ 接收 $e_{t}$ 和 $s_{t}$。
- 位置编码器 $\Phi_{pos}$ 将 $s_{t}$ 提升为高维嵌入 $e_{pos}$，随后与 $e_{t}$ 融合生成统一的上下文感知表示 $z_{t}=F_{fuse}(concat(e_{t},\Phi_{pos}(s_{t})))$。
- 最终预测 $\hat{X}_{t+1:t+H}$ 是所有专家输出的加权和：$\hat{X}_{t+1:t+H}=\sum_{k=1}^{K}p_{t,k}\cdot P_{k}(z_{t})$ 。
## Results
<img src="../attachments/Pasted%20image%2020260118153911.png" style="zoom:50%;" />
作者前面提到，motif机制在长程预测的表现提升更明显，结果表格佐证了这一点。

## Conclusion
本文介绍了一种新颖的上下文模体引导的长期时间序列预测框架CometNet，该框架通过发现和利用循环的、长程的上下文模体来提高预测精度。通过结合上下文模体抽取模块( Contextual Motif Extraction )和模体引导的预测模块( Motif-guided Forecasting )，CometNet有效地将局部观测建立在重要的长期上下文中，从而将具有重要长期依赖关系的预测融合在一起。在8个真实世界数据集上的大量实验表明，CometNet显著优于当前最先进的方法，特别是在扩展预测范围上。 这些结果突出了利用上下文模体来指导长期时间依赖关系建模的好处。