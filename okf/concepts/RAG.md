---
type: Concept
title: RAG
description: 检索增强生成 (RAG) 是一种将信息检索与语言模型生成相结合的自然语言处理范式。RAG 首先从知识库中检索与输入查询相关的文档片段，然后将检索到的内容作为上下文输入语言模型以生成最终响应。
tags: [rag]
timestamp: "2026-05-10T16:00:00Z"
round_created: 1
round_updated: 3
okf_version: 0.1
aliases: [检索增强生成, Retrieval-Augmented Generation, 检索增强生成系统]
claim_ids: [claim_001, claim_003, claim_005, claim_006, claim_009, claim_018, claim_022, claim_024, claim_025, claim_028]
---

# RAG

> Aliases: 检索增强生成, Retrieval-Augmented Generation, 检索增强生成系统

---
type: Concept
title: RAG
description: 检索增强生成 (RAG) 是一种将信息检索与语言模型生成相结合的自然语言处理范式。RAG 首先从知识库中检索与输入查询相关的文档片段，然后将检索到的内容作为上下文输入语言模型以生成最终响应。
tags: [rag]
timestamp: "2026-05-10T16:00:00Z"
round_created: 1
round_updated: 3
okf_version: 0.1
aliases: [检索增强生成, Retrieval-Augmented Generation, 检索增强生成系统]
claim_ids: [claim_001, claim_003, claim_005, claim_006, claim_009, claim_018, claim_022, claim_024, claim_025, claim_028]
---


## 定义

检索增强生成 (RAG) 是一种将信息检索与语言模型生成相结合的自然语言处理范式。RAG 首先从知识库中检索与输入查询相关的文档片段，然后将检索到的内容作为上下文输入语言模型以生成最终响应。

## 关键声明

- [claim_003](/concepts/RAG.md#claim_003): RAG 模型在开放域问答上优于所有纯生成模型 (支持)
- [claim_005](/concepts/RAG.md#claim_005): 检索质量是影响端到端问答性能的首要因素 (支持)
- [claim_009](/concepts/RAG.md#claim_009): 检索与生成的联合训练可以提升两方面性能 (支持)
- [claim_022](/concepts/RAG.md#claim_022): RAG 系统在 35% 的边缘案例下会产生不可靠输出 (支持)
- [claim_024](/concepts/RAG.md#claim_024): RAG 在知识记忆方面比微调优势显著 (支持)
- [claim_025](/concepts/RAG.md#claim_025): 微调在分布外泛化上显著优于RAG (不支持)
- [claim_028](/concepts/RAG.md#claim_028): 检索在任何情况下都能提升LLM的生成质量 (不支持)

## 相关概念

- [Dense_Retrieval](/concepts/Dense_Retrieval.md) - RAG 的核心检索组件
- [GraphRAG](/concepts/GraphRAG.md) - RAG 的图增强变体
- [Agentic_RAG](/concepts/Agentic_RAG.md) - RAG 的智能体驱动变体
- [KG_RAG](/concepts/KG_RAG.md) - 结合知识图谱的 RAG
- [Multi_Hop_Retrieval](/concepts/Multi_Hop_Retrieval.md) - RAG 的多跳推理挑战
- [Long_Context](/concepts/Long_Context.md) - 长上下文模型——RAG 的替代方案
- [RAG_Evaluation](/concepts/RAG_Evaluation.md) - RAG 的评估方法
- [KB_Degradation](/concepts/KB_Degradation.md) - RAG 知识库的退化问题

## 证据来源

- [source_002](/sources/source_002.md) - RAG 奠基性工作 (Lewis et al., 2020)
- [source_005](/sources/source_005.md) - 开放域问答系统 (Chen et al., 2017)
- [source_007](/sources/source_007.md) - RAG 评估指标综述 (Liu et al., 2022)
- [source_008](/sources/source_008.md) - 检索生成联合训练 (Sachan et al., 2021)
- [source_025](/sources/source_025.md) - RAG 失效模式分析 (Zhao et al., 2024)
- [source_027](/sources/source_027.md) - RAG vs 微调 (Mallen et al., 2023)
- [source_030](/sources/source_030.md) - LLM 知识边界 (Kandpal et al., 2023)

# Citations

[1] [Dense Passage Retrieval：面向开放域问答的稠密检索方法 (2020)](/sources/source_001.md)
[2] [检索增强生成：面向知识密集型 NLP 任务的神经方法 (2020)](/sources/source_002.md)
[3] [开放域问答系统中的检索方法评估 (2017)](/sources/source_005.md)
[4] [RAG 中的评估指标与基准：系统综述 (2022)](/sources/source_007.md)
[5] [FiD：融合解码器——多检索段落的知识融合方法 (2021)](/sources/source_006.md)
[6] [面向知识密集型任务的检索与生成联合训练 (2021)](/sources/source_008.md)
[7] [RAG 与长上下文模型的对比研究：检索是否仍然必要？ (2024)](/sources/source_021.md)
[8] [边缘案例下的 RAG 系统失效模式分析 (2024)](/sources/source_025.md)
[9] [RAG 还是微调？面向知识注入的语言模型适应性方法比较 (2023)](/sources/source_027.md)
[10] [大语言模型的知识边界：何时检索、何时依赖内部知识 (2023)](/sources/source_030.md)

## Claims

<a id="claim_001"></a>**claim_001** (supported) [src:source_001]: DPR在开放域问答中显著优于BM25，Top-20检索准确率提升9%-19%
<a id="claim_003"></a>**claim_003** (supported) [src:source_002]: RAG模型在开放域问答上优于所有纯生成模型
<a id="claim_005"></a>**claim_005** (supported) [src:source_005,source_007]: 检索质量是影响端到端问答性能的首要因素
<a id="claim_006"></a>**claim_006** (supported) [src:source_006]: FiD随检索段落数增加性能持续提升
<a id="claim_009"></a>**claim_009** (supported) [src:source_008]: 检索与生成的联合训练可以提升两方面性能
<a id="claim_018"></a>**claim_018** (supported) [src:source_021]: 长上下文模型在知识源小于100K tokens时表现与RAG相当
<a id="claim_022"></a>**claim_022** (supported) [src:source_025]: RAG系统在35%的边缘案例下会产生不可靠输出
<a id="claim_024"></a>**claim_024** (supported) [src:source_027]: RAG在知识记忆方面比微调优势显著
<a id="claim_025"></a>**claim_025** (unsupported) [src:source_027]: 微调在分布外泛化上显著优于RAG
<a id="claim_028"></a>**claim_028** (unsupported) [src:source_021,source_030]: 检索在任何情况下都能提升LLM的生成质量

# Citations

[1] [Dense Passage Retrieval：面向开放域问答的稠密检索方法 (2020)](/sources/source_001.md)
[2] [检索增强生成：面向知识密集型 NLP 任务的神经方法 (2020)](/sources/source_002.md)
[3] [开放域问答系统中的检索方法评估 (2017)](/sources/source_005.md)
[4] [RAG 中的评估指标与基准：系统综述 (2022)](/sources/source_007.md)
[5] [FiD：融合解码器——多检索段落的知识融合方法 (2021)](/sources/source_006.md)
[6] [面向知识密集型任务的检索与生成联合训练 (2021)](/sources/source_008.md)
[7] [RAG 与长上下文模型的对比研究：检索是否仍然必要？ (2024)](/sources/source_021.md)
[8] [边缘案例下的 RAG 系统失效模式分析 (2024)](/sources/source_025.md)
[9] [RAG 还是微调？面向知识注入的语言模型适应性方法比较 (2023)](/sources/source_027.md)
[10] [大语言模型的知识边界：何时检索、何时依赖内部知识 (2023)](/sources/source_030.md)
