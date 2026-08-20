> *Introduce & formalize fundamental concepts in RL in the context of **Markov decision processes**.*
> 全程会使用网格问题（grid example）来说明。

## State & State Space
![544](../../attachments/Pasted%20image%2020260814075434.png)
- State：Agent在环境中所处的状况
- State Space：所有可能State之集
## Action & Action Space (of a State)
- Action：在每个State下可以执行的操作。
- Action space of a state：$A(s_i) = {a_i}_{i=1}^{n_i}$ 
![730](../../attachments/Pasted%20image%2020260814080200.png)
> 比如在grid example中，上下左右移或者停留在原地就是当前状态的全部5种actions。

## State Transition
定义了Agent与环境的交互。形式化表达：
$$s_1 \xrightarrow{a_2} s_2$$
### Forbidden Area
![686](../../attachments/Pasted%20image%2020260814081110.png)
### Tabular Representation
状态转移表，但是弊端是只能表示deterministic cases。
![748](../../attachments/Pasted%20image%2020260814081333.png)
### State Transition Probability
比如说某一时刻agent处于$s_1$，给定action$a_2$，也就是右转，它会移动到$s_2$。以概率的形式来表达就是：
$$
p(s_2|s_1, a_2) = 1
$$
$$
p(s_i | s_1, a_2) = 0,\, \forall i \neq 2
$$
这只是一个确定性的例子，但是它可以表达stochastic（随机的）cases。
## Policy
数学化表示：用$\pi$来表示一个Policy。<u>$\pi$是一个概率，表示在某个状态$s_i$下选择action $a_i$的概率是多少。</u>
for state $s_1$,
$$\sum_i\pi(a_i|s_1) = 1$$
其中$i$是所有的actions。
### Tabular Representation
![736](../../attachments/Pasted%20image%2020260814082421.png)
## Reward
RL中最独特的概念之一。
- A **positive** reward represents **encouragement** to take the actions
- A **negative** one represents **punishment**
- **A zero reward means no punishment**, as well as encouragement to some extent
举例：
![1113](../../attachments/Pasted%20image%2020260814084542.png)
### Tabular Representation
![971](../../attachments/Pasted%20image%2020260814084633.png)
局限仍然是**只适用于确定性case**。实际上采用一个action能得到的reward可能是不确定的。
### Mathematical Description
比如说在$s_1$采取$a_1$（向上移动），于是出了bound，reward是-1，数学表达如下：
$$
p(r=-1|s_1,a_1) = 1 \quad and\quad p(r\neq -1| s_1, a_1) = 0
$$
## Trajectory
> 中文直译是“踪迹”/“轨迹”。

A trajectory is a **state-action-reward** chain.
![430](../../attachments/Pasted%20image%2020260814085542.png)
## Return
![986](../../attachments/Pasted%20image%2020260814085605.png)
一条trajectory上所有的rewards的加和。
**可以用来判断一个policy是好是坏。**
但是有可能在到达target之后策略仍然在继续发挥作用，reward可能仍然在叠加，所以return会发散，所以需要引入discounted return来解决这个问题。
## Discounted Return 折扣回报
从字面意义上理解，future rewards会打折扣，这个折扣是discount rate $\gamma$，且$\gamma \in [0,1)$  。
![966](../../attachments/Pasted%20image%2020260814090659.png)
所以作用有二：
- 让return收敛（收敛是converge，发散是diverge）
- 让far future和near future的rewards价值不同
	- $\gamma$越**小**，衰减程度越**大**，所以一个policy就会更加**短视**
	- $\gamma$越大，衰减程度越**小**，一个policy就会更加**有远见**
## Episode
- **如果一个agent遵循某种policy能到达terminal states，那么这样的一个trajectory就是一个episode。**
- 一个episode通常是被认为是一个finite trajectory。
- Tasks with episodes are called episodic tasks.
### Episodic & Continuing Tasks
- 一个Task如果有Terminal states，那么它就是episodic tasks；
- 一个Task如果没有Terminal states（终止状态），那么意味着agent和环境的交互永不停止，那么这样的tasks就被称为continuing tasks。
> 现实中episodic是常态，很少存在continuing tasks。
#### Unified way
我们并不区分两种tasks，**一律转化成continuing tasks。** 
方法：
- Option 1：Target state as an Absorbing state
	把target state看成absorbing ones，一旦到达absorbing states，之后的所有actions的结果都是停留在原状态，自然地，相应rewards也都是0；
- Option 2：Target state as a normal state with a policy
	也就是不区分是否是target。每次进入target states，$r = +1$；处于target state时也有policy，也可以跳出来。
**在RL中，采用更一般化的Option 2。**
## Markov Decision Process / MDP
![1153](../../attachments/Pasted%20image%2020260814093804.png)
最重要的是Markov过程的无记忆性（memoryless property）。也就是说**当前状态下选择某个action，转移到下一个状态的概率，和agent的状态转移历史并不相关**。
注意上文的无记忆性的公式是有错误的，参照以下教材github仓库的最新版本PDF中的表述：
![887](../../attachments/Pasted%20image%2020260814095141.png)
