# Autoformer 代码笔记
### Q、K、V的形状：K和V需要相同，但是可以和Q不相同。
### 对于多头的操作
- **标准 Transformer**：多头结果是 **拼接 + 线性映射**（不是取均值）。
- **Autoformer**：在 `corr` 的训练阶段，用 `mean` 来做一个近似，减少复杂度。
> 但是在论文中的论述里，这个多头的处理还是和原本的注意力是一样的。在非训练阶段，应该也是保持论文里的做法。
### `Roll`操作的实现
```python
for i in range(top_k):

	pattern = torch.roll(tmp_values, -int(index[i]), -1)	
	delays_agg = delays_agg + pattern * 
				(tmp_corr[:, i].unsqueeze(1).unsqueeze(1).unsqueeze(1).repeat(1, head, channel, length))
return delays_agg
```
### 常用的torch方法/其他库的方法
#### `torch.roll(input, shifts, dims)`
- 作用：把张量 `input` 在指定维度 `dims` 上**循环滚动**（类似数组循环移位）。
- `shifts`：移动多少个位置，正数表示向后移，负数表示向前移。
- `dims`：在哪个维度上滚动，通常是整数或整数元组。
>将原来的序列向前滚动，正好相当于将`value`列向后滚动。
#### `Tensor.view(B, H, -1)`
`Tensor.view()` 的作用是：
> **在不改变底层数据的前提下，改变张量的形状 (shape)**。

简单说，就是「**重新整理形状**」，类似于 NumPy 里的 `.reshape()`。
所以，如果原来的形状是`[B, H, C, L]`，执行了上面的操作，返回的形状是`[B, H, C * L]`。
#### `Tensor.unfold(dim, window_size, stride)`
某种滑动窗口机制。如果对一个三维的张量`[B, N, C]`执行`a.unfold(1, S, Stride)`，得到的形状为`[B, Window_Num, C, S]`。
>我们可以这么理解：
>![[Pasted image 20251009005642.png]]
>从展开的那一维开始，我们就可以看成一个多维的元素，然后对照以上示例，发现变换后原先那一维变成了**滑动窗口的个数**，而最后一维对应地变为**窗口的大小**。
#### `torch.stack(a, dim=k)`
对一个列表作用，按着列表摞起来，摞出来的一个维度成为新的第`K`维度。
### 标准`MultiHeadAttention`的返回值
标准的返回值有两个，分别为`out`与`attn`。
- `out`：`[B, L, d_models]`
- `attn`：`[]`
### 时间延迟聚合模块再补充
这个延迟（位移）只位移一个$\tau$ ，GPT给出的解释如下：
>**周期性依赖**：每个 `τ` 代表一个周期，平移 `τ` 能保持对相同周期的模式对齐，捕捉周期性依赖。
>**对齐周期**：只平移一个 `τ`，能对齐相同周期的位置，而不是跨周期的模式。
>**避免信息丢失**：平移多个 `τ` 会让模型错过周期内相位对齐的模式，可能导致信息丢失或模糊化。

