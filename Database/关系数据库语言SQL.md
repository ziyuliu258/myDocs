## 定义
结构化查询语言SQL（Structured Query Language）是一种介于**关系代数**与**关系演算**之间的语言，其功能包括**查询、操纵、定义和控制**四个方面，是一个通用的的关系数据库语言。
目前，SQL已成为关系数据库的标准语言。
## 特点
>了解
- 综合统一
- 高度非过程化：不需要**指定存取路径**，只需要**指定行为**，剩下由SQL和系统自动完成
- 面向集合：
	- 非关系数据模型采用面向记录的操作方式，操作对象是记录；
	- SQL采用集合操作方式，操作对象是**元组（记录）的集合**
	- `WHERE age > 20`
- 以同一种语法结构提供多种使用方式：可以作为独立语言，可以作为嵌入式语言放在别的语言中。
- 简洁易用
## 操作语句
![614](../attachments/Pasted%20image%2020260424010033.png)
常用的动词只有九个：
![531](../attachments/Pasted%20image%2020260424010118.png)
## 基本概念
- 基本表
	- 本身独立存在
	- 一个关系对应一个基本表
	- 一个基本表对应一个存储文件
	- 一个表带若干索引
- 存储文件
	- 逻辑结构组成关系数据库内模式；
	- 物理结构任意，对用户透明（用户无法得知）
- 视图
	- 从一个或几个基本表导出的表
	- 数据库只存放视图定义，不存放图对应的数据
	- 视图是虚表
	- 用户可以在视图上定义视图
![](../attachments/Pasted%20image%2020260424012216.png)
## 组成
- 数据定义语言 SQL DDL
- 数据操纵语言 SQL DML
- 数据控制语言 SQL DCL
- 嵌入式SQL语言的使用规定
### 数据定义语言
数据定义功能：**模式（Schema）定义**、**表定义**、**视图**和**索引**的定义。
![767](../attachments/Pasted%20image%2020260424012551.png)
#### 创建基本表
```sql
CREATE TABLE <表名>(<列名>  <数据类型> [完整性约束条件]
                  [,<列名>  <数据类型> [完整性约束条件]]
                       ……
                   [表级完整性约束条件])
```
##### 数据类型
- SQL中**域**的概念用**数据类型**来实现。
- 定义表的属性：数据类型 + 长度
- 选用数据类型需要参考**取值范围 + 使用运算类型**
![596](../attachments/Pasted%20image%2020260424014607.png)
![598](../attachments/Pasted%20image%2020260424014620.png)
##### 列的完整性约束
- 用SQL保留字`NULL`或`NOT NULL`指定当前列是否可以取空值或不允许取空值
- `UNIQUE`：指定列取值不可重复
- `DEFAULT <表达式>`指定该列缺省值
	- `DEFAULT NULL`指定当前列缺省取空值
```sql
PRIMARY KEY ( <列名> ) ,
FOREIGN KEY    (<列名>)  REFERENCES <表名> 
ON DELETE {RESTRICT | CASCADE | SET NULL},
CHECK      <逻辑条件表达式>
```
##### 例题
![536](../attachments/Pasted%20image%2020260424015057.png)
创建STUDENT,COURSE,SC三个基表。
```sql
CREATE TABLE  STUDENT
   (SNO CHAR(7)  NOT NULL,
	SNAME VARCHAR(10) NOT NULL,
	SEX  CHAR(1) NOT NULL,
	BDATE  DATE NOT NULL,
	HEIGHT  DEC(3,2) DEFAULT 0.0,
	PRIMARY KEY(SNO));    //定义主键

 CREATE TABLE COURSE
   (CNO  CHAR(6) NOT NULL,
	CNAME  VARCHAR(30) NOT NULL,
	LHOUR  SMALLINT NOT NULL,
	CREDIT DEC(1,0) NOT NULL,
	SEMESTER  CHAR(2) NOT NULL,
	PRIMARY KEY(CNO)); //定义主键
CREATE TABLE SC
	(SNO CHAR(7)  NOT NULL,
	CNO  CHAR(6) NOT NULL, 
	GRADE  DEC(4,1) DEFAULT NULL,
	PRIMARY KEY(SNO,CNO),    //定义主键
	FOREIGN KEY(SNO)              //定义外键
		REFERENCES STUDENT
		ON DELETE CASCADE,
	FOREIGN KEY(CNO) //定义外键
		REFERENCES COURSE
		ON DELETE RESTRICT,
	CHECK (GRADE IS NULL) OR (GRADE BETWEEN 0 AND 100)
);

```