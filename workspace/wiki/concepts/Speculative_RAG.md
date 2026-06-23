---
type: Concept
title: Speculative RAG - 推测性RAG
description: Speculative RAG 是一种通过推测性文档选择加速 RAG 推理过程的框架，利用并行生成和轻量级验证器提升效率。
tags: [speculative-rag---推测性rag]
timestamp: "2026-05-10T16:00:00Z"
round_created: 3
round_updated: 3
okf_version: 0.1
aliases: [推测性RAG, 并行推测RAG]
claim_ids: [claim_030]
---

# Speculative RAG - 推测性RAG

> Aliases: 推测性RAG, 并行推测RAG

## 定义

Speculative RAG 是一种通过推测性文档选择加速 RAG 推理过程的框架，利用并行生成和轻量级验证器提升效率。

## 关键声明

- [claim_030](/concepts/Speculative_RAG.md#claim_030): Speculative RAG 在提升速度的同时也提升了检索召回率 (不支持)

> 根据 [source_019](/sources/source_019.md)，Speculative RAG 将端到端推理延迟降低了 40%，但在高召回要求场景下可能出现最优文档被过滤的问题。

## 相关概念

- [RAG](/concepts/RAG.md) - Speculative RAG 是 RAG 的效率优化变体
- [Corrective_RAG](/concepts/Corrective_RAG.md) - 两者都涉及文档选择机制

## 证据来源

- [source_019](/sources/source_019.md) - Speculative RAG (Wang et al., 2024)

## Claims

<a id="claim_030"></a>**claim_030** (unsupported): Speculative RAG在提升速度的同时也提升了检索召回率

# Citations

[1] [Speculative RAG：通过并行推测加快 RAG 推理 (2024)](/sources/source_019.md)
