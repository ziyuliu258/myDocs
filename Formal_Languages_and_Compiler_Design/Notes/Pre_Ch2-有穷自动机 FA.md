## 概述
### 自动机的语言
能够被自动机$A$接受的字符串的集合为$A$的语言，记为$L(A)$。
### 有穷自动机的基本要素
- 有限个状态；
- 存在状态之间的转移；
- 有一个初始状态；
- 一个或者多个终止状态。
## 确定性有穷自动机 DFA
### 定义
**确定性有穷自动机 (Deterministic Finite Automa, DFA)** 是一种定义语言的形式化系统，形式如下：
$$(Q, \Sigma, \delta, q_0, F)$$

- $Q$：有限的状态集合；
- $\Sigma$：Input Alphabet，输入符号的集合；
- $\delta$`\delta`：转移函数。
	- Input：一个状态 + 一个输入符号；
	- $\delta(q, a)$：在$q$状态接受符号$a$后DFA走向的下一个状态。
- $q_0$：初始状态。$q_0 \in Q$
- $F$：终止状态集合，$F \subseteq Q$，终止状态也称**接受状态**；
>其中需要注意的是 $\delta$ 是一个全函数，也就是说总是存在下一个状态。如果没有转移的话，我们增加一个 **死状态 (dead state)** 表示没有转移的情况。画图的时候一般不画出来。
>![](../../attachments/Pasted%20image%2020260314184947.png)
### 表示方法
#### 图表示
用一张 **状态转换图** 来表示 DFA，其中：

- 用 **结点 (node)** 表示状态；
- 用 **弧 (arc)** 表示转移函数；
    - 从状态 p 到状态 q 的弧上面标有所有的能够让 p 转移到 q 的输入符号。
- 用标有 `Start` 的箭头指向起始状态；
- 用 **双圆 (double circle)** 表示终止状态。
![](../../attachments/Pasted%20image%2020260314190746.png)
>这是识别英文文章中`ing`的DFA。
#### 转移表
![](../../attachments/Pasted%20image%2020260314190837.png)
#### 转移函数的拓展
将$\delta$拓展到**一个状态 + 一个输入字符串**的方式，描述一组输入对DFA的影响。
![](../../attachments/Pasted%20image%2020260314191909.png)
>实际上使用不区分$\hat{\delta}$和$\delta$，所以要根据具体情境区分。

例：

|      | 0    | 1    |
| ---- | ---- | ---- |
| A    | A    | B    |
| B    | A    | C    |
| C    | C    | C    |
有以下之式成立：
$$\delta(B,011) = \delta(\delta(B,01), 1)= \delta(\delta(\delta(B, 0), 1), 1) = \delta(\delta(A, 1), 1)= \delta(B, 1) = C$$
### DFA 的语言
对于一个 DFA $A$ 来说，$L(A)$ 是从初始状态走到终止状态的所有路径的标签**字符串**的集合。形式化定义如下：
![](../../attachments/Pasted%20image%2020260314201147.png)
>显然，这里的状态转移函数是拓展意义上的，这一语言里的每个元素都是一个字符串，每个字符串都能让DFA从初始状态走到终止状态。
### 正则语言
如果一个语言$L$可以被某个DFA $A$ 恰好接受（$L=L(A)$），那么称这个语言是**正则**（Regular）的。
>“恰好接受” $\approx$ DFA接受且只接受$L$的字符串。
#### 几个例子
参考这一[网页](https://fla.cuijiacai.com/02-fa/#_2-2-6-%E6%AD%A3%E5%88%99%E8%AF%AD%E8%A8%80)。
## 非确定性有穷自动机 NFA
**非确定性有穷自动机 (Nondeterministic Finite Automaton, NFA)** 可以同一时刻处在多个状态中。当有一个输入符号的时候，可以从一个状态转移到多个可能的下一状态。
NFA 从一个初始状态开始，如果任意一个选择序列能够到达一个终止状态，我们就认为 NFA 可以接受这个字符串。
### 定义
![](../../attachments/Pasted%20image%2020260314232100.png)
### DFA与NFA的等价性
DFA和NFA在语言的表达能力上是等价的。
- 能够用NFA表达的语言，一定存在某个DFA能够表达出相同的语言；
- 能够用DFA表达的语言，一定存在某个NFA能够表达出相同的语言。
前者很容易理解，后者需要用到**子集构造**方式证明。
>[!note]
>**子集构造** 假设 NFA 为 $N = (Q, \Sigma, \delta_N, q_0, F_N)$，我们要构造一个等价的 DFA $D = (Q_D, \Sigma, \delta_D, q_D, F_D)$。
>- $Q_D=2^Q$；
>- $\delta_D(R, a) = \bigcup_{r \in R}\delta_N(r, a)$
>- $q_D = \{q_0\}$
>- $F_D = \{ R \in Q_D \mid R \cap F_N \neq \emptyset \}$
>	>[!Note]
>	>对于一个 NFA，如果读入字符串 $w$ 后，从起点出发存在**至少一条**路径能到达终止状态，那么我们就说这个 NFA 接受 $w$。所以从这一点出发，只要构造这个接受状态集合的时候，存在和DFA的接收状态集合重合的地方，就说它能找到一个解，因此就是可以接受的。（*定义 2.7*）
#### 小结论
由于NFA和DFA的等价性，**NFA也只能接受正则语言**。换句话说，正则语言的一个核心特征是**有限记忆**。
## 带空转移的NFA
### 定义
我们可以在 NFA 的基础上再允许某个状态在没有输入字符的时候就转移到另一个状态，也就是说转移函数可以接受 $\epsilon$ 输入。这样的NFA就称为带空转移的NFA，写作 $\epsilon$-NFA。
**仍然只能接受正则语言**。
### 关键定义
#### 状态闭包
定义见下面。
>例：
>![](../../attachments/Pasted%20image%2020260315232425.png)
#### 转移函数与其拓展
$$
\hat{\delta}(q, w) = \begin{cases} 
CL(q), & \text{if } w = \epsilon \\ 
\bigcup_{p \in \hat{\delta}(q, x)} CL(\delta(p, a)), & \text{if } w = xa 
\end{cases}
$$

### 带空转移NFA与NFA的等价性
- 每一个 NFA 就是一个 $\epsilon$-NFA，只不过没有空转移；****
- 每个 $\epsilon$-NFA，都能构造一个NFA与之接受相同的语言。
>[!NOTE]
>参考证明如下：
>首先补充几个关键概念。
>- 定义：状态$q$的**状态闭包**（也就是$\epsilon-\text{closure}$）为从$q$开始通过接受一个/若干个$\epsilon$能够到达的状态集合，记为$CL(q)$。
>- 定义：状态集合$Q$的状态闭包，形式化公式如：
>	$$CL(Q)=\bigcup_{q \in Q}CL(q)$$
>以下为具体证明。
>![](../../attachments/Pasted%20image%2020260315231325.png)

>[!IMPORTANT]
>对于上文的证明，有下面的补充解释。
>对于状态转移函数，**带空转移的NFA**是先输入$a$，再闭包；而**构造出的等价NFA**规定，转移函数对初始状态先闭包，得出状态$q$，再和$a$一起输入到$\epsilon$-NFA的转移函数中。所以对于这两个NFA来说，可以将中间部分对齐：
>- $\epsilon$-NFA 是：$\quad \quad \quad \dots \to a_1 \to \mathbf{(\epsilon^*)} \to a_2 \to \dots$
>- 构造 NFA 是：$\dots \mathbf{(\epsilon^*)} \to a_1 \to \mathbf{(\epsilon^*)} \to a_2 \to \dots$
>但是开头和结尾有错位。
>而终止状态的构造$$F' = \{ q \in Q \mid CL(q) \cap F \neq \emptyset \}$$
>则补齐了末尾的差别。
>而回顾$\epsilon$-NFA的状态转移函数公式
>$$\hat{\delta}(q, w) = \begin{cases} CL(q), & \text{if } w = \epsilon \\ \bigcup_{p \in \hat{\delta}(q, x)} CL(\delta(p, a)), & \text{if } w = xa \end{cases}$$
> 可以看到，它处理第一个字符之前也是做了闭包。
> 所以，前后都对齐了，因此可以证明二者是等价的。
## 总结
- 三者都只能接受**正则语言**；
- NFA设计起来更容易，状态数（成指数级地）更少，但是难以被实现，因为不确定；
- DFA可以被计算机真正实现，因为计算机世界是确定的。
