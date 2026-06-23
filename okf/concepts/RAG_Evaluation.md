---
type: Concept
title: RAG Evaluation
description: RAG 评估是对检索增强生成系统在检索质量、生成质量和端到端性能等方面进行系统衡量的方法论体系。
tags: [rag-evaluation]
timestamp: "2026-05-10T16:00:00Z"
round_created: 1
round_updated: 3
okf_version: 0.1
aliases: [RAG评估, RAG测评, RAGAS]
claim_ids: [claim_010, claim_023]
---

# RAG Evaluation

> Aliases: RAG评估, RAG测评, RAGAS

---
type: Concept
title: RAG Evaluation
description: RAG 评估是对检索增强生成系统在检索质量、生成质量和端到端性能等方面进行系统衡量的方法论体系。
tags: [rag-evaluation]
timestamp: "2026-05-10T16:00:00Z"
round_created: 1
round_updated: 3
okf_version: 0.1
aliases: [RAG评估, RAG测评, RAGAS]
claim_ids: [claim_010, claim_023]
---


## 定义

RAG 评估是对检索增强生成系统在检索质量、生成质量和端到端性能等方面进行系统衡量的方法论体系。

## 关键声明

- [claim_010](/concepts/RAG_Evaluation.md#claim_010): RAGAS 评估与人类评估具有高度一致性 (支持)
- [claim_023](/concepts/RAG_Evaluation.md#claim_023): RAGAS 评估指标之间具有高相关性 (冲突)

> claim_023 存在冲突：[source_018](/sources/source_018.md) 宣称 RAGAS 与人类评估一致性高 (Spearman > 0.8)，但 [source_026](/sources/source_026.md) 指出评估指标间实际 pairwise Spearman < 0.5，存在系统性偏差。

## 评估维度

1. 忠实度 (Faithfulness)
2. 答案相关性 (Answer Relevancy)
3. 上下文精密度 (Context Precision)
4. 上下文召回率 (Context Recall)

## 相关概念

- [RAG](/concepts/RAG.md) - RAG 的评估方法论

## 证据来源

- [source_007](/sources/source_007.md) - RAG 评估指标综述 (Liu et al., 2022)
- [source_018](/sources/source_018.md) - RAGAS 评估框架 (Es et al., 2023)
- [source_026](/sources/source_026.md) - 评估框架批判 (Liu et al., 2024)

# Citations

[1] [RAGAS：检索增强生成的自动化评估框架 (2023)](/sources/source_018.md)
[2] [RAG 评估框架的局限性：对 RAGAS 等自动化评估方法的批判性分析 (2024)](/sources/source_026.md)

## Claims

<a id="claim_010"></a>**claim_010** (supported) [src:source_018]: RAGAS评估与人类评估具有高度一致性
<a id="claim_023"></a>**claim_023** (conflicted) [src:source_026]: RAGAS评估指标之间具有高相关性

# Citations

[1] [RAGAS：检索增强生成的自动化评估框架 (2023)](/sources/source_018.md)
[2] [RAG 评估框架的局限性：对 RAGAS 等自动化评估方法的批判性分析 (2024)](/sources/source_026.md)
