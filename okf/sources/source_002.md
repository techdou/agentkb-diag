---
type: Source
title: 检索增强生成：面向知识密集型 NLP 任务的神经方法
description: 提出RAG框架，将DPR检索与BART生成相结合的端到端模型
tags: [RAG, Retrieval-Augmented Generation, Knowledge-Intensive NLP]
timestamp: "2026-05-01T10:00:00Z"
round_created: 1
round_updated: 1
okf_version: 0.1
authors: "Lewis P, Perez E, Piktus A, Petroni F, Karpukhin V, Goyal N, Küttler H, Lewis M, Yih W, Rocktäschel T, Riedel S, Kiefer D"
year: 2020
source_id: source_002
---

# 检索增强生成：面向知识密集型 NLP 任务的神经方法

> Lewis P, Perez E, Piktus A, Petroni F, Karpukhin V, Goyal N, Küttler H, Lewis M, Yih W, Rocktäschel T, Riedel S, Kiefer D (2020)

---
type: Source
title: 检索增强生成：面向知识密集型 NLP 任务的神经方法
description: 提出RAG框架，将DPR检索与BART生成相结合的端到端模型
tags: [RAG, Retrieval-Augmented Generation, Knowledge-Intensive NLP]
timestamp: "2026-05-01T10:00:00Z"
round_created: 1
round_updated: 1
okf_version: 0.1
authors: "Lewis P, Perez E, Piktus A, Petroni F, Karpukhin V, Goyal N, Küttler H, Lewis M, Yih W, Rocktäschel T, Riedel S, Kiefer D"
year: 2020
source_id: source_002
---


> Lewis P, Perez E, Piktus A, Petroni F, Karpukhin V, Goyal N, Küttler H, Lewis M, Yih W, Rocktäschel T, Riedel S, Kiefer D (2020)

> Lewis P, Perez E, Piktus A, et al. (2020)

## 摘要

提出 RAG 框架，将 DPR 检索与 BART 生成器相结合的端到端模型，标志着 RAG 范式的正式确立。

## 提取的概念

- [RAG](/concepts/RAG.md) - 本文定义了 RAG 框架的基本范式
- [Dense_Retrieval](/concepts/Dense_Retrieval.md) - 使用 DPR 作为检索组件

## 提取的声明

- [claim_003](/concepts/RAG.md#claim_003): RAG 模型在开放域问答上优于所有纯生成模型

## 方法变体

1. **RAG-Token**: 每个 token 生成时使用不同的检索文档
2. **RAG-Sequence**: 整个序列使用相同的检索文档

## 实验结果

RAG 在开放域问答、事实验证（FEVER）、实体链接等任务上均显著优于不检索的方法，验证了检索增强生成的有效性。

## 相关来源

- [source_001](/sources/source_001.md) - DPR 检索组件
- [source_004](/sources/source_004.md) - REALM 相关工作
- [source_006](/sources/source_006.md) - FiD 多段落融合
