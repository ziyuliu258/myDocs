> [!NOTE]
> 主要是课程简介。介绍了一些基本的东西，以及推荐阅读的书目。
## 参考书/资料推荐
>更多参见本[链接](https://github.com/courses-at-nju-by-hfwei/compilers-resources/tree/master/books)
- ANTLR 4：实验所用的语言，参考书《ANTLR 4权威指南》
- 《自制编译器》
- 教材：“龙书”《编译原理》
- LLVM：最好看官方文档
- [https://godbolt.org](https://godbolt.org)：在线的编译器，可以查看每一行源代码对应的中间表示/汇编代码。
	![](../../attachments/Pasted%20image%2020260511175731.png)
## 其他内容
>[!note]
>补充一些零碎的内容。这一章没讲什么。

![408](../../attachments/Pasted%20image%2020260511174243.png)
### 中间表示（IR, Intermediate Representation）
![](../../attachments/Pasted%20image%2020260511174727.png)
![](../../attachments/Pasted%20image%2020260511175022.png)
#### 为什么需要IR？
- 如果不引入中间语言（介于高级语言和汇编语言之间），那么上图的例中，就需要写9种`A->B`的组合的编译器；而有了中间表示只需要写三种前端和三种后端就可以。
- 如上图所示，使用中间表示，可以在中间表示层做**机器无关**的代码优化，从前端得到的中间表示只需要面向后端的中间表示优化就可以，不需要做特别的设计。
	![](../../attachments/Pasted%20image%2020260511180605.png)
### LLVM中间表示优化
#### 优化策略：常量传播
![](../../attachments/Pasted%20image%2020260511183023.png)
- 定义：**如果在编译时就能确定某个变量的值是一个常量，那么就直接用这个常量替换掉程序中所有用到该变量的地方。**
- 不开优化时结果中间表示结果如下：
	```bash
	clang -emit-llvm -S opt.c -o opt.ll
	```
	![](../../attachments/Pasted%20image%2020260512160431.png)
	>明显有`icmp`的比较命令，也就是`if/else`的判断条件。且上面有两个字符串，也就是两个分支的结果（`@.str`/`@.str.1`）
- 所以开O1级优化：
	```bash
	clang -emit-llvm -S opt.c -o opt1.ll -O1 -g0
	```
	由于在这个例子中，`two`和`three`的值都不会变化，所以可以直接看成常数，于是后面的都可以被替换成常数，从而可以直接把判断分支都剪掉，只剩下最后的那个正确选择。
	![](../../attachments/Pasted%20image%2020260512160719.png)
	>此时直接就看不到另一个字符串了，主逻辑也是非常简单，直接`call`了`@puts`函数（也就是打印语句），把那个最后的`"three > two\00"`打印出来了。
#### Pass（趟）
![](../../attachments/Pasted%20image%2020260512161036.png)
- 编译器的前端的任务，可以简单概括为**生成IR**。
- 编译器开发最重要的事情之一就是，**如何在IR上做优化**。
- 在IR上做优化，将一些优化策略写在编译框架上，每一个策略通过一个“Pass（趟/遍）”来作用到IR上。
### 编译器前后端具体流程
#### 前端
![215](../../attachments/Pasted%20image%2020260512161632.png)
##### 举例
```c
// Created by hengxin on 02/14/23.

// comment out #include <stdio.h> before executing the following two commands
// ast: abstract syntax tree
// (1) clang -Xclang -ast-dump naming.c
  // clang naming.c -o naming
  // clang -cc1 -ast-view naming.c (for graphviz)
// (2) clang -fsyntax-only -Xclang -dump-tokens naming.c

#include <stdio.h>

// The code with really bad names for variables.
int main() {
  int two;
  int three;
  scanf("%d%d", &two, &three);
  int six = two + three;

  if (six > 4) {
    six = 5;
  } else {
    six = 3;
  }

  return 0;
}
```
###### 词法分析
 **作用：分割字符串**，把单字符组成的字符串，分割成一个一个有意义的**词法单元（token）**，也就是**from CharStream to TokenStream**。
 先注释掉`#include <stdio.h>`，防止分析过多的内容；然后执行命令：
 ```bash
 clang -fsyntax-only -Xclang -dump-tokens naming.c
 ```
 得到结果
 ```bash
 int 'int'        [StartOfLine]  Loc=<naming.c:13:1>
identifier 'main'        [LeadingSpace] Loc=<naming.c:13:5>
l_paren '('             Loc=<naming.c:13:9>
r_paren ')'             Loc=<naming.c:13:10>
l_brace '{'      [LeadingSpace] Loc=<naming.c:13:12>
int 'int'        [StartOfLine] [LeadingSpace]   Loc=<naming.c:14:3>
identifier 'two'         [LeadingSpace] Loc=<naming.c:14:7>
semi ';'                Loc=<naming.c:14:10>
int 'int'        [StartOfLine] [LeadingSpace]   Loc=<naming.c:15:3>
identifier 'three'       [LeadingSpace] Loc=<naming.c:15:7>
semi ';'                Loc=<naming.c:15:12>
identifier 'scanf'       [StartOfLine] [LeadingSpace]   Loc=<naming.c:16:3>
l_paren '('             Loc=<naming.c:16:8>
string_literal '"%d%d"'         Loc=<naming.c:16:9>
comma ','               Loc=<naming.c:16:15>
amp '&'  [LeadingSpace] Loc=<naming.c:16:17>
identifier 'two'                Loc=<naming.c:16:18>
comma ','               Loc=<naming.c:16:21>
amp '&'  [LeadingSpace] Loc=<naming.c:16:23>
identifier 'three'              Loc=<naming.c:16:24>
r_paren ')'             Loc=<naming.c:16:29>
semi ';'                Loc=<naming.c:16:30>
int 'int'        [StartOfLine] [LeadingSpace]   Loc=<naming.c:17:3>
identifier 'six'         [LeadingSpace] Loc=<naming.c:17:7>
equal '='        [LeadingSpace] Loc=<naming.c:17:11>
identifier 'two'         [LeadingSpace] Loc=<naming.c:17:13>
plus '+'         [LeadingSpace] Loc=<naming.c:17:17>
identifier 'three'       [LeadingSpace] Loc=<naming.c:17:19>
semi ';'                Loc=<naming.c:17:24>
if 'if'  [StartOfLine] [LeadingSpace]   Loc=<naming.c:19:3>
l_paren '('      [LeadingSpace] Loc=<naming.c:19:6>
identifier 'six'                Loc=<naming.c:19:7>
greater '>'      [LeadingSpace] Loc=<naming.c:19:11>
numeric_constant '4'     [LeadingSpace] Loc=<naming.c:19:13>
r_paren ')'             Loc=<naming.c:19:14>
l_brace '{'      [LeadingSpace] Loc=<naming.c:19:16>
identifier 'six'         [StartOfLine] [LeadingSpace]   Loc=<naming.c:20:5>
equal '='        [LeadingSpace] Loc=<naming.c:20:9>
numeric_constant '5'     [LeadingSpace] Loc=<naming.c:20:11>
semi ';'                Loc=<naming.c:20:12>
r_brace '}'      [StartOfLine] [LeadingSpace]   Loc=<naming.c:21:3>
else 'else'      [LeadingSpace] Loc=<naming.c:21:5>
l_brace '{'      [LeadingSpace] Loc=<naming.c:21:10>
identifier 'six'         [StartOfLine] [LeadingSpace]   Loc=<naming.c:22:5>
equal '='        [LeadingSpace] Loc=<naming.c:22:9>
numeric_constant '3'     [LeadingSpace] Loc=<naming.c:22:11>
semi ';'                Loc=<naming.c:22:12>
r_brace '}'      [StartOfLine] [LeadingSpace]   Loc=<naming.c:23:3>
return 'return'  [StartOfLine] [LeadingSpace]   Loc=<naming.c:25:3>
numeric_constant '0'     [LeadingSpace] Loc=<naming.c:25:10>
semi ';'                Loc=<naming.c:25:11>
r_brace '}'      [StartOfLine]  Loc=<naming.c:26:1>

 ```
###### 语法分析
为解析出来的词法单元流构建一个语法树，如果能构建成功，说明程序合法；否则就说明有语法错误。
> 用[godbolt.org](https://godbolt.org)查看。或者看示例程序的注释中注明的命令。
#### 后端
![250](../../attachments/Pasted%20image%2020260626191258.png)