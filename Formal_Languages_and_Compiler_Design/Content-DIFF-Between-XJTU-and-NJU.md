本目录用于整理西安交通大学《形式语言与编译》的复习材料。当前最重要的结论是：`Reference/NJU-Compiler` 可以用来快速补理解，但不能直接替代本校 `Slides`。本校考试范围更偏“形式语言 + 编译原理笔试题”，NJU 资料更偏“现代编译器工程课”。

## 复习材料定位

- `Slides/`：本校官方课件，必须作为最终考试边界。
- `Slides/课程总结与知识梳理2026.docx`：官方复习范围，优先级最高。
- `Slides/知识图谱2026.pdf`：官方知识结构，适合确认每章覆盖点。
- `Reference/Material/exam_17/`：往年期末题，适合判断题型。
- `Reference/Material/2024形编考试题回忆版.docx`：较规范的 2024 回忆题，适合判断近年考点。
- `Reference/NJU-Compiler/`：辅助理解用，不能直接按它的范围复习。

## 总体判断

NJU 的课适合用来听懂编译原理主干，例如自动机、LL/LR 分析、属性文法、中间代码、寄存器分配等。但本校考试还会重点考：

- 形式语言理论题
- PDA
- 文法化简
- g-NFA 状态约简法
- SLR(1) itemDFA 和冲突消解
- 符号表与声明语义分析
- QTAC/四元式
- 运行时栈快照、访问链、控制链、函数作为参数

这些内容必须回到本校课件补齐。

## NJU 资料重点听什么

### 1. 自动机、正则表达式、词法分析

重点看：

- `Reference/NJU-Compiler/2024/3-lexer-re-automata/`

重点内容：

- RE、NFA、DFA 的关系
- RE -> NFA
- NFA -> DFA 子集构造法
- DFA 最小化
- DFA -> RE
- 词法分析中的最长匹配和优先级

对应本校：

- `Slides/第二章DFA2026.pdf`
- `Slides/第二章NFA2026.pdf`
- `Slides/第三章RE2026.pdf`
- `Slides/第四章2026.pdf`

注意：本校“最小 DFA 转 RE”主要用 `g-NFA 状态约简/状态消去法`，最终仍要看本校 `第三章RE2026.pdf`。

### 2. LL(1) 分析

重点看：

- `Reference/NJU-Compiler/2024/6-parser-ll/`

重点内容：

- FIRST 集
- FOLLOW 集
- LL(1) 文法
- 预测分析表
- 消除左递归
- 递归下降分析的基本思想

对应本校：

- `Slides/第六章-2026.pdf`

这部分 NJU 和本校重合较高，可以重点听。

### 3. LR(0)、SLR(1)

重点看：

- `Reference/NJU-Compiler/2024/14-parser-lr0/`
- `Reference/NJU-Compiler/2024/15-parser-lr1/` 的前半部分

重点内容：

- LR(0) item
- closure/goto
- ACTION/GOTO 表
- 移进-归约分析
- 移进-归约冲突
- 归约-归约冲突
- SLR(1) 分析表

对应本校：

- `Slides/第八章-2026new.pdf`

注意：`15-parser-lr1` 后半的 LR(1)、LALR(1) 细节，本校期末优先级低，可以略过。

### 4. 属性文法与语义分析

重点看：

- `Reference/NJU-Compiler/2024/9-semantics-ag/`

重点内容：

- 属性文法
- SDD
- SDT
- 综合属性
- 继承属性
- 属性求值

对应本校：

- `Slides/第九章2026.pdf`

注意：本校更容易考具体符号表和声明语义分析，NJU 只能帮助理解属性文法，不能替代本校第 9 章。

### 5. 中间代码生成

重点看：

- `Reference/NJU-Compiler/2024/11-ir-expr/`
- `Reference/NJU-Compiler/2024/12-ir-control-backpatch/`

重点内容：

- 表达式翻译
- 布尔表达式翻译
- if/while 控制流翻译
- 回填思想
- 三地址码生成

对应本校：

- `Slides/第十章2026.pdf`

注意：本校用 QTAC、四元式、`place/code/tc/fc` 等属性写法，答题时要按本校记法。

### 6. 寄存器分配

重点看：

- `Reference/NJU-Compiler/2024/17-codegen-ra/`

只看：

- 活跃变量分析
- 干涉图
- 图着色
- spill/溢出

对应本校：

- `Slides/第十二章代码优化2026.pdf`

LLVM 后端细节不用深挖。

## NJU 资料可以快速看或略听什么

### ANTLR / 手写 Lexer

相关目录：

- `Reference/NJU-Compiler/2024/1-lexer-antlr/`
- `Reference/NJU-Compiler/2024/2-lexer-handwritten/`

只需要看：

- 最长匹配
- 优先级
- 手写 lexer 的大致思想

可以略过：

- ANTLR 工程配置
- Gradle
- visitor/listener
- 具体工具链细节

本校更关注：

- σ-DFA
- 前缀最大化原则
- 事实优先级
- 词法记号设计

这些必须看 `Slides/第四章2026.pdf`。

### CFG 基础

相关目录：

- `Reference/NJU-Compiler/2024/5-parser-cfg/`

可以看：

- CFG
- 语法树
- 二义性
- 泵引理直觉

但本校第 5 章更重视：

- 文法化简
- 无用符号
- ε-产生式
- 单位产生式
- 短语、直接短语、句柄

所以必须回到 `Slides/第五章2026.pdf`。

## 建议直接略过什么

为了期末突击，以下 NJU 内容性价比低：

- ANTLR 工程细节
- ALL(\*) / parser-allstar
- LLVM IR 深入内容
- Clang 工具链
- RISC-V codegen
- LR(1) 后半
- LALR(1) 细节
- Gradle/ANTLR 项目实现
- 编译器项目工程实践

这些内容对理解现代编译器有价值，但对本校期末笔试帮助有限。

## 必须回本校课件补什么

### 第 2、3 章：DFA/NFA/RE

看：

- `Slides/第二章DFA2026.pdf`
- `Slides/第二章NFA2026.pdf`
- `Slides/第三章RE2026.pdf`

必须掌握：

- NFA/ε-NFA -> DFA 子集构造
- DFA 最小化
- g-NFA 状态约简法
- DFA/NFA -> RE
- 给语言写 RE

### 第 4 章：词法分析

看：

- `Slides/第四章2026.pdf`

必须掌握：

- 词法记号设计
- σ-DFA
- 前缀最大化原则
- 事实优先级
- 根据联合 DFA 写 token 输出

### 第 5 章：CFG

看：

- `Slides/第五章2026.pdf`

必须掌握：

- CFG 定义
- 推导、归约、语法树
- 短语、直接短语、句柄
- 二义性
- 消除无用符号
- 消除 ε-产生式
- 消除单位产生式

### 第 6 章：LL(1)

看：

- `Slides/第六章-2026.pdf`

必须掌握：

- 消除左递归
- 消除回溯
- FIRST/FOLLOW/SELECT
- LL(1) 判定
- 预测分析表

### 第 7 章：PDA

看：

- `Slides/第七章2026.pdf`

必须掌握：

- PDA 定义
- ID/瞬时描述
- 直接移动、移动
- 终态接受、空栈接受
- PDA 设计
- DPDA 判断

NJU 资料不能替代这一章。

### 第 8 章：SLR(1)

看：

- `Slides/第八章-2026new.pdf`

必须掌握：

- 规范归约
- 句柄剪枝
- 活前缀
- LR(0) 项目集规范簇
- itemDFA
- LR(0)/SLR(1) 分析表
- 冲突判断与消解

### 第 9 章：语义分析

看：

- `Slides/第九章2026.pdf`

必须掌握：

- 符号表结构
- 表头、登记项、类型特有信息
- bind/lookup/newtab
- 简单变量声明
- 数组声明
- 函数声明
- 属性文法与属性求值

### 第 10 章：中间代码生成

看：

- `Slides/第十章2026.pdf`

必须掌握：

- QTAC
- 四元式
- 算术表达式翻译
- 布尔表达式短路翻译
- if/while 翻译
- 数组元素地址计算
- 函数调用与 return 翻译

### 第 11 章：运行时环境

看：

- `Slides/第十一章2026.pdf`

必须掌握：

- 活动树
- 活动记录/栈帧
- 参数区、链接区、局部区
- 访问链、控制链、返回地址
- 栈快照
- 调用序列、返回序列
- 函数序言、尾声
- 函数作为参数
- 非局部名访问

这是本校特色重难点，NJU 资料基本不能替代。

### 第 12 章：代码优化

看：

- `Slides/第十二章代码优化2026.pdf`

必须掌握：

- 控制流图
- succ/pred/path
- 支配关系
- 到达定值
- 活跃变量
- web/极大 web
- 干涉图
- 图着色寄存器分配
- 溢出与代码改写

## 按考试题型的优先级

最高优先级：

- NFA -> DFA -> 最小 DFA -> RE
- 文法化简
- FIRST/FOLLOW/LL(1)
- 规范归约、短语、句柄、二义性
- itemDFA、SLR(1) 分析表、冲突消解
- 符号表与声明语义分析
- QTAC/四元式
- 栈快照

中等优先级：

- PDA 移动与设计
- 词法分析联合 DFA
- 布尔表达式短路翻译
- 数组元素地址计算
- 寄存器分配

较低优先级：

- ANTLR
- LLVM IR 深入
- LR(1)/LALR(1)
- RISC-V 代码生成细节
- Clang 工具链

## 建议复习路线

1. 用 NJU 快速听懂自动机、LL、LR、属性文法、中间代码、寄存器分配的基本思想。
2. 回到本校 `Slides` 对照知识图谱补齐本校符号、算法和答题格式。
3. 用 `Reference/Material/exam_17/` 和 `2024形编考试题回忆版.docx` 检查自己是否能做出题型。
4. 最后按 `知识点提纲.md` 查漏补缺。

一句话：NJU 用来补理解，本校 Slides 用来对考试。

## 最终结论：NJU 2024 逐集观看建议

如果时间紧，按下面这个表执行。这里的“集”按 `Reference/NJU-Compiler/2024/` 里的课件目录理解。

| NJU 2024 目录               | 建议   | 为什么                                                       |
| ------------------------- | ---- | --------------------------------------------------------- |
| `0-overview`              | 选看   | 可以建立编译器整体流程直觉，但本校第 1 章更按形式语言与编译过程考。                       |
| `1-lexer-antlr`           | 略看   | 只看正则表达式、最长匹配、优先级；ANTLR 工程细节不考。                            |
| `2-lexer-handwritten`     | 略看   | 只看手写 lexer 的最长匹配思想；本校要回第 4 章看 σ-DFA。                      |
| `3-lexer-re-automata`     | 必看   | 对应本校第 2、3、4 章核心：RE、NFA、DFA、子集构造、DFA 最小化、DFA 到 RE。         |
| `4-parser-antlr`          | 略过   | ANTLR 和现代 parser 工具为主，本校期末性价比低。                           |
| `5-parser-cfg`            | 选看   | 看 CFG、推导、语法树、二义性；文法化简和句柄必须回本校第 5 章补。                      |
| `6-parser-ll`             | 必看   | 对应本校第 6 章：FIRST、FOLLOW、LL(1)、预测分析表、消除左递归。                 |
| `7-parser-allstar`        | 略过   | ALL(*) 属于 ANTLR 高级算法，本校基本不考。                              |
| `8-symtable`              | 选看   | 可帮助理解符号表，但本校第 9 章的 bind/lookup/newtab、offset、width 必须另补。  |
| `9-semantics-ag`          | 必看   | 对应属性文法、SDD/SDT、综合/继承属性；本校语义分析题需要这个底子。                     |
| `10-llvm-ir`              | 略过   | LLVM IR 深入内容，本校只需知道 IR/QTAC/LLVM-IR 的位置，不按 LLVM 细节考。      |
| `11-ir-expr`              | 必看   | 对应表达式翻译、三地址码、中间代码生成。                                      |
| `12-ir-control-backpatch` | 必看   | 对应布尔表达式、if/while、控制流翻译、回填思想；本校第 10 章会用类似思想但记法不同。          |
| `12-ir-control-easy`      | 选看   | 如果 `12-ir-control-backpatch` 看不懂，先看 easy；否则可跳。            |
| `12-ir-control-hard`      | 略过   | 比本校期末要求更工程化/复杂，时间紧不看。                                     |
| `13-codegen-riscv`        | 略过   | RISC-V 代码生成细节，本校不按这个考。                                    |
| `14-parser-lr0`           | 必看   | 对应 LR(0) item、closure/goto、ACTION/GOTO、移进归约分析，是本校第 8 章基础。 |
| `15-parser-lr1`           | 只看前半 | 看到 SLR(1) 分析表和 SLR(1) 文法即可；LR(1)、LALR(1) 后半略过。            |
| `16-codegen-isel`         | 略过   | 指令选择工程细节，非本校期末重点。                                         |
| `17-codegen-ra`           | 选看   | 只看活跃变量、干涉图、图着色、spill；LLVM register allocator 细节略过。        |

## 最小观看清单

时间非常紧时，只看这几集：

1. `3-lexer-re-automata`
2. `6-parser-ll`
3. `14-parser-lr0`
4. `15-parser-lr1` 前半
5. `9-semantics-ag`
6. `11-ir-expr`
7. `12-ir-control-backpatch`
8. `17-codegen-ra` 中寄存器分配相关部分

看完这些以后，必须回本校补：

1. `Slides/第三章RE2026.pdf`：g-NFA 状态约简，最小 DFA 转 RE。
2. `Slides/第四章2026.pdf`：σ-DFA、前缀最大化、事实优先级。
3. `Slides/第五章2026.pdf`：文法化简、短语、直接短语、句柄。
4. `Slides/第七章2026.pdf`：PDA、ID、移动、空栈/终态接受、DPDA。
5. `Slides/第八章-2026new.pdf`：本校 itemDFA/SLR(1) 写法和冲突消解。
6. `Slides/第九章2026.pdf`：符号表、声明语义分析、函数/数组登记。
7. `Slides/第十章2026.pdf`：QTAC、四元式、`place/code/tc/fc`。
8. `Slides/第十一章2026.pdf`：栈快照、访问链、控制链、函数作为参数。

## 如果使用 NJU 2021 版本

2021 版本的课程结构也能用，对应关系如下：

| NJU 2021 目录 | 建议 |
| --- | --- |
| `1-lexer-re-antlr` | 略看，正则和 lexer 直觉即可 |
| `2-lexer-handwritten` | 略看，最长匹配即可 |
| `3-lexer-automata` | 必看，对应自动机、子集构造、DFA 最小化 |
| `4-parser-grammar` | 选看，CFG、语法树、二义性 |
| `5-parser-antlr` | 略过 |
| `6-parser-ll` | 必看 |
| `7-parser-ll-antlr` | 略过 |
| `8-parser-lr0` | 必看 |
| `9-parser-lr1` | 只看 SLR(1) 相关，LR(1)/LALR 略过 |
| `10-semantics-sdd` | 必看 |
| `11-semantics-sdt` | 选看 |
| `12-semantics-symtab-types` | 选看，但本校符号表仍要回 Slides |
| `13-ir-expr-control` | 必看 |
| `14-ir-backpatch` | 必看 |
| `15-ir-others` | 略过 |

## 一句话版

NJU 最值得看的，是 `自动机 + LL(1) + LR(0)/SLR(1) + 属性文法 + 中间代码 + 寄存器分配`。  
NJU 可以略过的，是 `ANTLR 工程、ALL(*)、LLVM 深入、RISC-V、LR(1)/LALR(1) 后半、指令选择工程细节`。  
本校必须补的，是 `PDA、文法化简、g-NFA 状态约简、σ-DFA、本校符号表/QTAC写法、运行时栈快照`。
