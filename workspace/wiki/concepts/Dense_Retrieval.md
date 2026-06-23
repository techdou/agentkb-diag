---
type: Concept
title: Dense Retrieval
description: 稠密检索是一种使用神经网络将文本映射到低维稠密向量空间的信息检索方法。与基于关键词匹配的稀疏检索（如 BM25）不同，稠密检索通过语义相似度计算实现检索。
tags: [dense-retrieval]
timestamp: "2026-05-05T14:00:00Z"
round_created: 1
round_updated: 2
okf_version: 0.1
aliases: [稠密检索, 密集检索, Dense Passage Retrieval, DPR]
claim_ids: [claim_002, claim_004, claim_007]
---

# Dense Retrieval

> Aliases: 稠密检索, 密集检索, Dense Passage Retrieval, DPR

## 定义

稠密检索是一种使用神经网络将文本映射到低维稠密向量空间的信息检索方法。与基于关键词匹配的稀疏检索（如 BM25）不同，稠密检索通过语义相似度计算实现检索。

## 关键声明

- [claim_001](/concepts/RAG.md#claim_001): DPR 在开放域问答中显著优于 BM25 (支持)
- [claim_002](/concepts/Dense_Retrieval.md#claim_002): 双编码器架构是稠密检索的最优架构选择 (支持)
- [claim_004](/concepts/Dense_Retrieval.md#claim_004): 稀疏检索在精确匹配场景下仍优于稠密检索 (支持)
- [claim_007](/concepts/Dense_Retrieval.md#claim_007): 对比学习可以显著提升稠密检索的表示质量 (支持)

## 相关概念

- [RAG](/concepts/RAG.md) - 稠密检索是 RAG 的核心组件
- [GraphRAG](/concepts/GraphRAG.md) - 图增强检索，稠密检索的扩展
- [KG_RAG](/concepts/KG_RAG.md) - 结合知识图谱和稠密检索的混合方法

## 证据来源

- [source_001](/sources/source_001.md) - DPR 奠基性工作 (Karpukhin et al., 2020)
- [source_003](/sources/source_003.md) - 检索方法综述 (Lin et al., 2021)
- [source_009](/sources/source_009.md) - 对比学习改进 (Gao et al., 2021)

## Claims

<a id="claim_002"></a>**claim_002** (supported): 双编码器架构是稠密检索的最优架构选择
<a id="claim_004"></a>**claim_004** (supported): 稀疏检索在精确匹配场景下仍优于稠密检索
<a id="claim_007"></a>**claim_007** (supported): 对比学习可以显著提升稠密检索的表示质量

# Citations

[1] [Dense Passage Retrieval：面向开放域问答的稠密检索方法 (2020)](/sources/source_001.md)
[2] [知识密集型 NLP 任务中的检索方法综述 (2021)](/sources/source_003.md)
[3] [基于对比学习的稠密检索表示优化 (2021)](/sources/source_009.md)
