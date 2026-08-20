# Paper-Agent 相关工作与设计相似性调研

> 检索截止：2026-08-04（America/New_York）  
> 检索方式：通过 EXA MCP 进行英文语义检索，并用 ACL Anthology、PMLR、Nature、AAAI DOI、OpenReview 和 arXiv 页面核对论文状态与摘要。  
> 说明：这是一份面向项目定位的快速 related-work scan，不替代可复现的系统综述；“没有发现完全相同工作”只表示在本次检索范围内未发现一篇把所有组件完整合并的论文。

## 结论先行

有，而且相似工作已经形成一个比较清晰的研究簇：

1. **科学文献检索与综合**：OpenScholar、ResearchAgent、Ai2 Scholar QA 等直接研究从大量论文中检索、组织、归纳和引用。
2. **多智能体深度研究与长文生成**：Co-STORM、ManuSearch、RAPID、Agent Laboratory 将规划、检索、阅读、写作或审查拆成多个阶段/角色。
3. **长期记忆与知识图谱**：HippoRAG、Zep、CatRAG 研究图结构、时间性、证据链和跨文档检索。
4. **论文的可执行化与复现**：Paper2Agent、HiRAS、MLAgentBench、PaperArena 将论文理解推进到工具调用、代码生成、实验执行或 agent 评测。
5. **报告审查与结构化组织**：WikiREVIEW、WikiMAG、AI Scientist 等研究多视角审查、结构规划、自动修订和自动同行评议。

**与当前 Paper-Agent 最接近的不是某一篇单独论文，而是几条工作的交集：**

> OpenScholar 的科学文献检索/引用约束 + Co-STORM 的多智能体探索/报告交互 + HippoRAG 的图式长期记忆 + Agent Laboratory/ResearchAgent 的研究流程编排。

在本次检索到的正式发表论文和高相关预印本中，**没有发现一篇同时实现当前工作区的完整组合**：自动选论文与 source fallback、单篇论文 `paper_notes`、T1–T7 分组深读、报告 groundedness 审计、profile 隔离的 claims/evidence/synthesis/provenance、claim relations，以及 theme/gap/opportunity/health/field-map/evidence-matrix 派生工作台。

但这不等于所有单点设计都新颖。若把 Paper-Agent 写成论文，最稳妥的定位是：**一个面向“持续学术阅读”的可审计研究记忆系统与端到端 Web 工作台**；创新重点应放在 profile-level memory、证据治理、跨论文更新/冲突处理和可测评估，而不是泛称“用多个 LLM agent 自动读论文”。

## 当前项目的功能向量

根据本工作区 `AGENTS.md`、`CLAUDE.md` 和实际代码结构，Paper-Agent 当前包含：

- **Source / selection**：从 OpenReview、OpenAlex、DBLP、arXiv、Semantic Scholar 等获取候选；按 DOI、arXiv ID、标题去重；embedding + lexical blended rerank；PDF URL enrichment；topic-fit gate；LLM Top-1 选择；优先 PDF，必要时保留真实 HTML source。
- **Paper understanding**：PDF 图表/表格识别与裁剪；HTML 正文抽取；共享结构化 `paper_notes`，包含问题、方法、结果、局限、术语和 figure highlights。
- **Interpretation orchestration**：T1–T7 任务；Group A 为 `T1 → T5 → T6`，Group B 为 `T2 → T3 → T4`，T7 汇总；WorkingMemory 作为 job 级短期记忆。
- **Trust / report**：report audit 检查 groundedness 和 consistency，必要时保守修复；英文 source-of-truth、中文展示层；报告 variants 支持再次 grounded refinement。
- **Long-term memory**：profile 隔离的 entity、claim、evidence、synthesis、review、revision、provenance；claim scope、structured evidence、reinforces/extends/contradicts 关系；stability/lifecycle；按 job/paper 删除或跨 profile 移动 bundle。
- **Derived research views**：theme、gap、opportunity、memory health、field map、evidence matrix、brief、living survey；其中关系、机会和治理视图以确定性规则派生，方便回归与审计。
- **Product surface**：FastAPI + React Web-only 工作台，包含 Run、Reports、Papers、Profiles、Living Survey、Memory Workspace 和 Settings。

因此，项目的核心单位不是一次 QA，也不是单纯的摘要，而是：

```text
paper source → structured notes → staged interpretation → audited report
             → profile-scoped durable memory → derived research map/opportunities
```

## 一、最直接的科学文献/研究助手近邻

| 论文 | venue / 状态 | 与 Paper-Agent 的重合 | 关键差异与定位判断 |
|---|---|---|---|
| [OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented Language Models](https://www.nature.com/articles/s41586-025-10072-4) | Nature，2026 | **主题：很高；设计：中高**。专门面向科学文献；检索、rerank、长文综合、自反馈和引用准确性。使用 4,500 万篇开放论文，并提出 ScholarQABench。 | 更像大规模科学 RAG / literature synthesis 模型，不是单篇论文深读工作流，也没有 Paper-Agent 的 profile 级持久记忆、claim lifecycle、人工 review queue 和 Web 记忆治理。它是最重要的质量与引用评测基线。 |
| [Into the Unknown Unknowns: Engaged Human Learning through Participation in Language Model Agent Conversations](https://aclanthology.org/2024.emnlp-main.554/) | EMNLP 2024 main | **设计：很高**。Co-STORM 使用多个 LM agent 进行多视角对话，维护动态 mind map，并生成带引用的综合报告；支持用户中途 steer。 | 面向开放主题和复杂信息寻求，不专门理解科学论文；mind map 不是可治理的 claims/evidence 事实层。Paper-Agent 的 Run/Report/Memory Workspace 可视为把这类探索式交互落到持续学术阅读上。 |
| [Agent Laboratory: Using LLM Agents as Research Assistants](https://aclanthology.org/2025.findings-emnlp.320/) | Findings of EMNLP 2025 | **主题：很高；设计：高**。把 literature review、experiment、report writing 组织成三阶段，允许人在每阶段反馈，并产出代码仓库与研究报告。 | 目标是从研究想法到实验和论文的科研自动化，范围大于 Paper-Agent；Paper-Agent 更聚焦“读懂论文并沉淀领域记忆”，不自动把研究推进到实验。Agent Laboratory 的 84% 成本下降结果值得作为流程效率对照。 |
| [ResearchAgent: Iterative Research Idea Generation over Scientific Literature with Large Language Models](https://openreview.net/forum?id=I0oWWdH7cS) | ACL ARR 2024 April submission；OpenReview 投稿，不按正式录用论文计 | **主题：很高；设计：中高**。从核心论文出发，连接 academic graph 和 entity-centric knowledge store，再让 ReviewingAgents 迭代改进研究想法。 | 它更偏研究想法生成和 peer-style critique；与 Paper-Agent 的 profile、related papers、theme/gap/opportunity 很接近，但不是当前工作区这种“论文解读 → 证据写回 → 长期记忆治理”闭环。 |
| [ManuSearch: Democratizing Deep Search in Large Language Models with a Transparent and Open Multi-Agent Framework](https://aclanthology.org/2025.findings-emnlp.130/) | Findings of EMNLP 2025 | **设计：高**。solution planner、Internet search agent、structured webpage reader 三个协作 agent；强调可解释、开放和可复现，并提供 ORION benchmark。 | 主要解决开放网页 deep search，不负责科学论文的领域记忆和报告后治理。它与 Paper-Agent 的 selector、source_documents、processor 和 evidence extraction 边界最接近。 |
| [RAPID: Efficient Retrieval-Augmented Long Text Generation with Writing Planning and Information Discovery](https://aclanthology.org/2025.findings-acl.859/) | Findings of ACL 2025 | **设计：中高**。retrieval-augmented preliminary outline、attribute-constrained search、plan-guided generation 三模块，专门处理长文本的事实、覆盖和连贯性。 | 论文对象是 Wikipedia-like long text；没有 T1–T7 论文语义结构，也没有 profile memory、audit provenance 和跨论文增量更新。它支持 Paper-Agent 把“结构先行 + 检索约束”作为相关工作定位。 |
| [AI2 Scholar QA: Organized Literature Synthesis with Attribution](https://arxiv.org/abs/2504.10861) | 2025 arXiv preprint | **主题：高**。Semantic Scholar 摘要索引 + 全文索引、cross-encoder rerank、LLM 过滤/聚类/综合，并输出 attribution。 | 更接近 OpenScholar 的开放实现/产品型 literature QA；长期 memory 和 paper-level task decomposition 不是重点。 |

### 判断

这一组说明：**“检索论文 + 生成带引用的长文”已经是明确的研究方向，单独以此作为创新点不够。** Paper-Agent 应突出“持续阅读后的结构化知识如何被验证、维护、冲突化解和用于下一篇论文”，而不是仅强调自动摘要或多 agent。

## 二、长期记忆、图谱和证据治理近邻

| 论文 | venue / 状态 | 可借鉴设计 | 与 Paper-Agent 的关系 |
|---|---|---|---|
| [HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models](https://arxiv.org/abs/2405.14831) | NeurIPS 2024（论文正文标注为 NeurIPS 2024） | 用 LLM 把语料转为 schemaless knowledge graph，以 query concepts 作为 seed，在图上运行 Personalized PageRank；报告在多跳 QA 上最高约 20% 提升，并显著降低迭代检索成本。 | 与 Memory V3 的图和长期 retrieval 最接近，但 HippoRAG 重点是非参数 KG retrieval；Paper-Agent 还显式区分 claim/evidence/synthesis/review/provenance，并把治理结果派生为 health、field map、evidence matrix。 |
| [Breaking the Static Graph: Context-Aware Traversal for Graph-Based RAG](https://aclanthology.org/2026.findings-acl.290/) | Findings of ACL 2026 | CatRAG 针对静态图的 semantic drift，加入 symbolic anchoring、query-aware dynamic edge weighting、key-fact passage weighting，强调完整 evidence chain。 | 对 Paper-Agent 的 claim relation 和 evidence retrieval 很有启发：共享 entity 或相似度不应自动等于“相关”，查询目标、scope 和证据链完整性需要进入 traversal/排序。 |
| [Zep: A Temporal Knowledge Graph Architecture for Agent Memory](https://arxiv.org/abs/2501.13956) | 2025 arXiv preprint / production-oriented system paper | Graphiti 采用 episode、semantic entity、community 三层图，保留原始输入、实体关系和时间有效性，强调跨 session synthesis。 | 与 Paper-Agent 的 provenance、profile 隔离、时间性和跨 session memory 方向一致；区别是 Zep 面向通用 agent/enterprise conversation，而 Paper-Agent 面向学术 claim 与证据治理。 |
| [From RAG to Memory: Non-Parametric Continual Learning for Large Language Models](https://arxiv.org/abs/2502.14802) | 2025 arXiv preprint | HippoRAG 2 试图把 RAG 变为可持续整合的新知识层，结合 PPR 和更深的 passage integration。 | 可作为 Paper-Agent 后续研究“新论文加入后如何更新旧 claim、处理冲突、保持旧知识”的算法背景；当前项目的 relation/lifecycle 更偏确定性治理，而不是学习型 memory retriever。 |

### 判断

**Paper-Agent 的长期记忆层是最有机会形成差异化的部分，但需要更正式的抽象。** 当前代码已经具备一个很好的系统骨架：`claim` 是中层事实、`evidence` 是锚点、`synthesis` 是高层认识、`review/revision` 是治理记录、derived views 是只读认知层。下一步应把它形式化为“profile-scoped evidence-governed scholarly memory”，并用指标证明它比扁平向量库或普通 GraphRAG 更能减少 unsupported claims、处理冲突和支持跨论文综合。

## 三、论文可执行化、复现和评测近邻

| 论文 | venue / 状态 | 关键设计 | 与 Paper-Agent 的关系 |
|---|---|---|---|
| [Paper2Agent: Reimagining Research Papers As Interactive and Reliable AI Agents](https://arxiv.org/abs/2509.06917) | 2025 arXiv preprint | 多 agent 分析论文和代码库，自动构建 MCP server；通过生成测试和执行迭代增强可靠性，使用户可以用自然语言调用原论文工具和 workflow。 | 名称相似但方向相反：Paper-Agent 是 **paper → understanding/memory/report**；Paper2Agent 是 **paper + code → executable paper agent**。如果未来增加“从报告中触发复现实验/调用 paper tools”，它会是直接的扩展参考。 |
| [HiRAS: A Hierarchical Multi-Agent Framework for Paper-to-Code Generation and Execution](https://aclanthology.org/2026.findings-acl.377/) | Findings of ACL 2026 | 以 supervisory manager agents 协调细粒度 paper-to-code 阶段，提出 Paper2Code-Extra，强调全局监督、错误修正和减少 hallucination。 | 与 T1–T7 的 staged orchestration、artifact 传递、失败恢复相似；但任务是实验复现，不是报告解释和长期学术记忆。 |
| [PaperArena: An Evaluation Benchmark for Tool-Augmented Agentic Reasoning on Scientific Literature](https://arxiv.org/abs/2510.10909) | 2025 arXiv preprint | 跨论文、多模态、多工具科学推理 benchmark；提供 parsing、retrieval、programmatic computation、planning/action/memory/reflection 平台。报告最强系统平均准确率 38.78%，hard subset 仅 18.47%。 | 这是评估 Paper-Agent 的最直接候选之一：可测试图表、伪代码、跨论文证据链和工具使用，而不是只评一篇论文的摘要流畅度。 |
| [MLAgentBench: Evaluating Language Agents on Machine Learning Experimentation](https://proceedings.mlr.press/v235/huang24y.html) | ICML 2024 | 13 个机器学习实验任务，评估 agent 读写文件、执行代码、观察结果并迭代；报告平均成功率差异很大，凸显 long-horizon planning 与 hallucination 问题。 | 不是 Paper-Agent 的直接同类，但可借鉴其“任务环境 + 可执行结果 + 过程轨迹”思路，为未来的论文复现或 evidence verification 扩展提供评测框架。 |

### 判断

Paper2Agent/HiRAS 说明“理解论文”正在向“使用论文”发展；PaperArena/MLAgentBench 说明只看最终文本不够，必须评估过程、工具选择、证据链和可复现结果。当前 Paper-Agent 已有 `selector diagnostics`、`working_memory`、`report_audit`、`evidence` 等 artifact，具备构造这类 evaluation trace 的基础。

## 四、报告结构、审查与多视角修订近邻

| 论文 | venue / 状态 | 相关设计 | 对当前项目的启示 |
|---|---|---|---|
| [WikiREVIEW: A Multi-Perspective Review Framework for Automatic Wiki-Style Article Generation](https://doi.org/10.1609/aaai.v40i41.40768) | AAAI-26 | 初稿后由多视角专家在 chapter 和 paragraph 两级 review，反馈后持续修订，处理跨章节冗余、弱相关和逻辑不一致。 | 与 `ReportAuditor`、report refiner、T1–T7 之后的 repair 直接同构；Paper-Agent 的优势是把审查绑定到论文证据和 memory writeback，而不是只优化文章表面质量。 |
| [WikiMAG: A Multi-Agent Guided Framework for Generating Structured Wikipedia-like Articles](https://doi.org/10.1609/aaai.v40i37.40404) | AAAI-26 | progressive planner 先建粗粒度 outline，再标注 narrative/timeline/table；reflective inspector 多轮筛选引用；versatile writer 生成结构化文章。 | 与 Paper-Agent 的 report structure、figure/table 资产和 citation reliability 相近。可借鉴“结构类型显式标注”，把 paper notes 中的 result/table/figure/metric 更系统地接到报告段落。 |
| [Towards end-to-end automation of AI research](https://link.springer.com/article/10.1038/s41586-026-10265-5) | Nature，2026 | The AI Scientist 覆盖 ideation、literature search、experiment planning/implementation、analysis、manuscript 和自动 review；实验阶段使用 agentic tree search。 | 它比 Paper-Agent 更像完整科研自动化实验室，是宏观上位系统。Paper-Agent 可以明确声明边界：当前专注学术阅读和领域 memory，而不是自动发明和验证新实验。 |

### 判断

**“生成后审查/修订”已经有顶会和顶刊先例。** Paper-Agent 的可区分点不应是“有一个 critic”，而应是：审查结果是否会阻止无证据 claim 写入长期记忆、是否能保留删除原因、是否能在后续论文加入时重建 relation 和 derived views。

## 五、按 Paper-Agent 模块的相似性地图

| Paper-Agent 模块 | 最相似工作 | 相似程度 | 当前差异 |
|---|---|---:|---|
| 自动选论文、source enrichment、topic-fit gate | OpenScholar、ManuSearch、RAPID | 中高 | Paper-Agent 有明确的论文候选去重、PDF/HTML fallback 和 topic-fit precision-first gate；上述工作通常不提供同样的 job-level source semantics。 |
| PDF/HTML 处理、figure/table、structured notes | PaperArena、WikiMAG、OpenScholar | 中 | 相关工作多为检索或多模态 benchmark；Paper-Agent 把 PDF 与 HTML source 分开处理，并把结果归一化进 `paper_notes`。 |
| T1–T7 共享上下文与分组并行 | Agent Laboratory、HiRAS、ManuSearch | 中高 | 多阶段/多 agent 是共同范式；Paper-Agent 的任务分解是“论文解释学”专用，而非通用研究或 paper-to-code。 |
| grounded report audit / repair / refinement | OpenScholar、WikiREVIEW、AI Scientist | 高 | 审查与自反馈并不新；Paper-Agent 的潜在差异在审查结果直接约束 memory writeback，并保留 provenance。 |
| profile-scoped claims/evidence/synthesis | ResearchAgent、HippoRAG、Zep | 高 | 这些工作分别覆盖 academic graph、KG retrieval 或 temporal memory；Paper-Agent 将事实、证据、综合、review、revision 和删除/迁移语义统一到 profile 边界。 |
| claim relations 与 stability/lifecycle | HippoRAG、CatRAG、Zep | 中高 | 图检索和时序关系已有先例；Paper-Agent 的 `reinforces/extends/contradicts`、scope、review 状态和 lifecycle 是面向学术治理的组合，需要 benchmark 证明有效性。 |
| theme/gap/opportunity/health/field map/evidence matrix | ResearchAgent、PaperArena | 中高 | 研究想法和 benchmark 有相邻工作；Paper-Agent 把它们做成 profile 的确定性 derived views，而不是新的 LLM 事实源。 |
| Web 工作台、报告/记忆/图谱/微调 | Co-STORM、STORM 类系统、Zep 产品 | 中高 | 交互工作台已有先例；Paper-Agent 的产品边界更完整，但“Web UI 本身”不应作为论文创新。 |

## 六、相似性结论与原创性风险

### 1. 主题层面：明显相似，属于活跃方向

“LLM agent 帮助研究者检索、阅读、综合和推进科学工作”已经被 EMNLP、ACL Findings、ICML、NeurIPS、AAAI 和 Nature 等 venue 覆盖。相关工作不再只是 demo，而是在研究 benchmark、citation accuracy、long-horizon reliability、tool use、memory 和 reproducibility。

### 2. 完整设计层面：本次检索没有发现一对一复刻

目前最接近的组合是：

```text
OpenScholar       = scientific retrieval + rerank + citation-grounded synthesis
Co-STORM          = multi-agent discourse + mind map + interactive report
Agent Laboratory  = literature review + experiment + report workflow
HippoRAG / Zep    = graph/temporal long-term memory
ResearchAgent     = academic graph + entity store + iterative review
Paper-Agent       = single-paper deep reading + audited profile memory + derived research workspace
```

所以可以说 **“系统级组合有明显工程与研究空间”**，但不能说组成零件从未被提出。

### 3. 最有潜力的差异化主张

建议围绕以下主张组织论文，而不是围绕“多个 agent”：

1. **Evidence-governed scholarly memory**：长期记忆只接受有证据、可追溯、未被 audit 移除的 claim；claim 的 scope、stance、关系、稳定性和生命周期可解释。
2. **Profile-scoped continual synthesis**：每个研究主题/profile 是隔离边界；新论文写入后能重建关系、主题、空白、机会和领域地图，并支持按 job/paper 删除或迁移 bundle。
3. **Audited paper interpretation pipeline**：共享 `paper_notes` 让 T1–T7 以同一事实层工作，report audit 先于 memory writeback，减少“报告里看似合理、记忆里却变成无证据事实”的污染。
4. **PDF/HTML source fidelity**：把真实 HTML 论文页和 PDF fallback 区分开，并让下游处理链保留 source type 语义。这是系统可靠性设计，不是单纯抓取实现。
5. **从报告到可治理研究地图**：theme/gap/opportunity/health/field-map/evidence-matrix 是对阅读结果的确定性派生，不让每个页面重新调用 LLM 生成不稳定的“领域结论”。

## 七、建议补的实验与论文定位

如果目标是发表，而不是只做应用项目，建议至少补齐以下证据：

### A. Baseline 对比

- 单模型 PDF/HTML summary。
- 普通 RAG / vector memory。
- OpenScholar 或 PaperQA2 风格的 literature synthesis。
- Co-STORM/多 agent report 风格系统。
- 去掉 report audit、去掉 profile memory、去掉 claim relations 的 Paper-Agent ablation。

### B. 指标

- paper-level：事实准确性、关键结果覆盖率、figure/table 解释准确率、术语一致性。
- citation/evidence：citation precision、citation recall、claim-to-evidence support rate、unsupported claim rate、evidence chain completeness。
- memory-level：跨论文 retrieval、冲突识别 precision/recall、stale claim 处理、删除/迁移后无残留率、profile leakage rate。
- workflow-level：端到端 latency、LLM cost、失败恢复率、人工修改量、重复阅读节省量。
- research-map-level：gap/opportunity 的专家相关性、evidence matrix completeness、field-map cluster purity。

### C. 数据集和任务

- 选取一个主题下的时间序列论文，测试新旧结论冲突和 claim lifecycle。
- 构造需要跨论文、跨 figure/table、跨 supplementary material 的任务，参考 PaperArena 的难题设置。
- 让专家评估“报告正确”与“长期记忆可安全复用”是否一致；这两个目标不应混为一谈。
- 记录完整 trace：selector 候选、source URL、paper notes、T1–T7 artifact、audit 移除、memory writeback 和 derived view rebuild。

### D. 论文定位建议

可以考虑如下标题方向：

> **Paper-Agent: Evidence-Governed Longitudinal Memory for Auditable Scholarly Paper Interpretation**

或更偏系统：

> **Paper-Agent: An Auditable Web Workbench for Structured Paper Understanding and Continual Research Memory**

论文中应明确承认与 OpenScholar、Co-STORM、Agent Laboratory、HippoRAG、ResearchAgent、Paper2Agent 的关系，主动把项目放在“scientific literature agents / research assistants / agent memory / scholarly knowledge governance”的交叉处。

## 八、检索范围与状态说明

- **正式发表/正式 proceedings 页面**：OpenScholar（Nature 2026）、Co-STORM（EMNLP 2024）、Agent Laboratory（Findings EMNLP 2025）、ManuSearch（Findings EMNLP 2025）、RAPID（Findings ACL 2025）、MLAgentBench（ICML 2024）、HiRAS（Findings ACL 2026）、CatRAG（Findings ACL 2026）、WikiREVIEW（AAAI-26）、WikiMAG（AAAI-26）、The AI Scientist（Nature 2026）。
- **论文正文标注为 NeurIPS 2024，但本次以 arXiv 页面作为可访问来源**：HippoRAG。
- **OpenReview 投稿/预印本，不应在论文中写成已录用顶会**：ResearchAgent（ACL ARR 2024 submission）。
- **高相关但本次检索中仍以 arXiv/preprint 为主**：Paper2Agent、PaperArena、Zep、Ai2 Scholar QA、HippoRAG 2。
- 2026 年条目按当前日期记录；对于仅有 arXiv 或 OpenReview 页面、尚未给出正式 proceedings 的工作，报告中显式标注了状态。

## 最终判断

**答案是“有相似论文和设计，但目前未见一篇完整等价的 Paper-Agent”。** 直接相似度最高的方向是 OpenScholar 的科学文献综合、Co-STORM 的多智能体探索式报告、Agent Laboratory 的研究流程自动化、HippoRAG/Zep 的长期记忆、ResearchAgent 的 academic graph + iterative review，以及 PaperArena 的跨论文 agent 评测。

Paper-Agent 若要建立可信的原创性和论文贡献，应把重心从“自动读论文”提升为：

> **如何把一次有证据的论文解读，安全地沉淀为可审计、可冲突处理、可删除/迁移、可用于下一次研究综合的长期学术记忆。**

