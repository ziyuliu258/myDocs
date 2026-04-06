## General Cache Organization(S, E, B) 
>Cache的机制完全由硬件实现。
![637](../attachments/Pasted%20image%2020260329225512.png)
- S（Set）：组数，用s位数字标记组数，按照表示逻辑总共有$2^s$个组。
- E：行数，一个组有E个**Cache Line**，用e个数字表示，按照逻辑仍然有$E=2^e$。
- B（Block）：数据块数，每一行有B个块，b位表示，$B=2^b$
- Cache Line组成：
	![388](../attachments/Pasted%20image%2020260329235249.png)
	- 开头一个Valid Bit，标记块是否有效；
	- 中间Tag，是唯一标识，和后面的内容组合起来可以唯一对应一个内存地址；
	- 后面用b位储存，可以看成Offset，可以表示$B = 2^b\, \text{Bytes}$。
	![321](../attachments/Pasted%20image%2020260330005404.png)
	- 总大小$C = S \times E\times B$
## Mapping Method
### Direct Mapping 直接映射
$E = 1$，也就是每个Set只有一个Cache Line。
![625](../attachments/Pasted%20image%2020260330005852.png)
### E-way Set Associative Mapping E路组相连映射
![619](../attachments/Pasted%20image%2020260330010610.png)
图中一个Set里有两个Cache Line，所以在图中每一行有两个Line。此时叫 **“2-路组相连映射”**。
### Fully Associative Mapping 全相连映射
![739](../attachments/Pasted%20image%2020260330011044.png)
只有一个Set。这种不太常用，因为所有Line都被塞到一个Set里，要访问一个地址的时候需要很复杂的搜索方法。在Cache中不常用，因为硬件在虚拟存储的DRAM中使用。