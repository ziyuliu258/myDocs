> *Specifically FLAME includes a learned shape space of identity variations, an articulated jaw and neck, and eyeballs that rotate. Additionally we learn pose-dependent blendshapes for the jaw and neck from examples. Finally, we learn “expression” blendshapes to capture non-rigid deformations of the face.*
## 蒙皮与Skin Weight
每个顶点在移动的时候会受到骨骼的影响，这种机制就称为Skinning（蒙皮）。假设嘴唇的某个vertex受到jaw骨骼/关节和head骨骼/关节的影响，二者对它的影响程度用权重来表示（归一化的），那么这个权重就是Skin weight。
## 有哪些关节（Joint）
- Neck
- Head
- Jaw
- Eyeballs
## 参数
### pose参数
用$\theta$表示。主要控制**头部旋转**、**下巴旋转**和**眼球旋转**等，也就是Joint的旋转。
### shape参数
也就是不同的身份/脸型，$\beta$表示。
### expression参数
用$\psi$表示。
## 基础mesh的生成
假设中性脸是$T$，那么最后的形状就是$T_p=T+B_{id}\beta+B_{exp}\psi$（或者再加上pose）。
## 绑定流程
### 确定Joint位置
$J(\beta)$关节位置是由shape决定的，不同的脸的关节不一样，**身份决定骨骼位置**。
### LBS Linear Blend Skinning
经典线性蒙皮。
$$
M = W(T_p, J(\beta), \theta, W) 
$$
假设每个mesh的原始顶点表示为$v_i$，移动后的每个顶点为$v_i'$，有公式如下：
$$
v_i' =\sum_k w_{ik} G_kv_i
$$
其中$G_k$代表第 k 个骨骼关节（joint）的**全局变换矩阵**（global transformation matrix），也就是说使用的是*世界坐标*。
> [!Note]
> 这个全局变换矩阵是一个坑，还没填，需要到时候详细学一下。
### Pose corrective blendshape
Pose corrective blendshape是用于**修正骨骼蒙皮（LBS）产生的不自然形变**的一类额外形变模型。因为脸的jaw变角度时，并不是刚体旋转，所以不能直接旋转，所以要引入一个修正项blendshape。
加上这部分blendshape后，结果就如下：
$$
T_p=
T+
B_{id}\beta
+
B_{exp}\psi
+
B_P(\theta)
$$
#### 怎么训练？
通常不是人工设计，而是从扫描数据学习。假设有同一个人的neutral $V_0$，
jaw旋转30°的真实扫描$V_{real}$。先用LBS得到结果$V_{LBS}$，发现：
$$
V_{real}
\neq
V_{LBS}
$$
差值：
$$
\Delta V
=
V_{real}-V_{LBS}
$$
这个差值就是：

> corrective deformation

于是学习：
$$
B_P
$$
>[!Note]
>记得读SMPL，里面的学习方式和上述的相似。
## 局限
### LBS
LBS还是太简单，是低维的蒙皮方式，虽然有pose corrective blendshape补充，但是底层还是LBS，没法准取模拟真实的肌肉，不是生理模型，没有肌肉/脂肪/皮肤弹性之类的假设，只是几何方面的近似。这样的表达能力是显然弱于神经模型（比如NeRF Based Face）的。
### Jaw绑定
下颌运动建模太简单了，只是简单旋转。
### 表情空间有限
只有几十维度，是PCA得到的。还是比较简单。
### Identity 和 Expression 分离不彻底（关键！）
现实中是存在纠缠的，但是FLAME直接分离，做得太简单了。
### 其他
- topo固定，所有人的mesh顶点数是一样的；
- 依赖参数的拟合，没法对视觉前端的错误做修正。
- 不能展现更细微的皮肤纹理之类的