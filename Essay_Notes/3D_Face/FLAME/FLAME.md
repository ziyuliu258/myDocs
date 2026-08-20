## 整体流程
![](../../attachments/Pasted%20image%2020260818052906.png)


![777](../../attachments/Pasted%20image%2020260817081752.png)
- $\bar{T}$：中性脸mesh（Template Mesh）
- $\vec{\beta}$ ：ID参数，也就是shape系数；
- $B_S(\vec{\beta}, \mathcal{S})$：形状基是$\mathcal{S}$，而$\vec{\beta}$是参数
	![](../../attachments/Pasted%20image%2020260817084733.png)
- $\vec{\theta}$：pose参数，如eyeballs、jaw、head的张合/旋转。
- $B_P(\vec{\theta};\mathcal{P})$：姿态修正变形。因为单纯旋转下颌会产生不自然的脸部拉伸，所以这里加入额外的局部修正。
	![](../../attachments/Pasted%20image%2020260817084750.png)
- $(\vec{\psi}$：表情参数，例如微笑、皱眉、张嘴。
- $B_E(\vec{\psi};\mathcal{E})$：根据表情参数产生的面部表情变形。
- $J(\vec{\beta})$：关节位置，例如脖子关节、下颌关节、眼球关节。它会随人的脸型变化。
	![936](../../attachments/Pasted%20image%2020260817084301.png)
- $\mathcal{W}$：蒙皮权重，表示每个顶点受哪个关节影响、影响程度是多少。
- $W()$：线性混合蒙皮函数，也就是把顶点按照关节旋转进行变换。

