---
type: Concept
title: GraphRAG
description: GraphRAG 是一种将知识图谱结构引入 RAG 框架的方法，通过从文档中提取实体和关系构建知识图谱，利用图结构信息增强检索能力。
tags: [graphrag]
timestamp: "2026-05-10T16:00:00Z"
round_created: 2
round_updated: 3
okf_version: 0.1
aliases: [图增强RAG, 图检索增强生成]
claim_ids: [claim_011, claim_020]
---

# GraphRAG

> Aliases: 图增强RAG, 图检索增强生成

## 定义

GraphRAG 是一种将知识图谱结构引入 RAG 框架的方法，通过从文档中提取实体和关系构建知识图谱，利用图结构信息增强检索能力。

## 关键声明

- [claim_011](/concepts/GraphRAG.md#claim_011): GraphRAG 在全局性问题回答上显著优于传统 RAG (支持)
- [claim_020](/concepts/GraphRAG.md#claim_020): GraphRAG 在通用场景下显著优于向量 RAG (冲突)

> claim_020 存在冲突：[source_011](/sources/source_011.md) 宣称 GraphRAG 显著优于向量 RAG，但 [source_023](/sources/source_023.md) 的对比分析发现，在精确事实查询场景下 GraphRAG 确实优于向量 RAG（+15%），但在开放域问题和语义匹配任务上提升不显著（+2%），且构建成本是向量 RAG 的 5-8 倍。

## 相关概念

- [RAG](/concepts/RAG.md) - GraphRAG 是 RAG 的图增强变体
- [KG_RAG](/concepts/KG_RAG.md) - 相关的知识图谱 RAG 方法
- [Dense_Retrieval](/concepts/Dense_Retrieval.md) - 底层检索技术

## 证据来源

- [source_011](/sources/source_011.md) - GraphRAG 提出论文 (Edge et al., 2024)
- [source_023](/sources/source_023.md) - GraphRAG vs 向量 RAG 对比 (Zhang et al., 2024)

## Claims

<a id="claim_011"></a>**claim_011** (supported): GraphRAG在全局性问题回答上显著优于传统RAG
<a id="claim_020"></a>**claim_020** (conflicted): GraphRAG在通用场景下显著优于向量RAG

# Citations

[1] [GraphRAG：利用知识图谱增强检索增强生成的全局理解能力 (2024)](/sources/source_011.md)
[2] [GraphRAG 与向量 RAG 的对比分析：重新审视图结构在检索中的作用 (2024)](/sources/source_023.md)
