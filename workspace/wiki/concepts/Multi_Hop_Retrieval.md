---
type: Concept
title: Multi-Hop Retrieval
description: 多跳检索是一种需要多步检索和推理才能回答复杂问题的检索范式。与单步检索不同，多跳检索需要在多个信息源之间进行桥接推理。
tags: [multi-hop-retrieval]
timestamp: "2026-05-05T14:00:00Z"
round_created: 2
round_updated: 2
okf_version: 0.1
aliases: [多跳检索, 多步推理检索, Multi-step Retrieval]
claim_ids: [claim_015]
---

# Multi-Hop Retrieval

> Aliases: 多跳检索, 多步推理检索, Multi-step Retrieval

## 定义

多跳检索是一种需要多步检索和推理才能回答复杂问题的检索范式。与单步检索不同，多跳检索需要在多个信息源之间进行桥接推理。

## 关键声明

- [claim_015](/concepts/Multi_Hop_Retrieval.md#claim_015): 多跳检索成功率随跳数增加急剧下降 (支持)

## 退化数据

| 跳数 | 准确率 |
|------|--------|
| 1 | 85% |
| 2 | 62% |
| 3 | 38% |
| 4 | 21% |

## 相关概念

- [RAG](/concepts/RAG.md) - 多跳检索是 RAG 面临的核心挑战

## 证据来源

- [source_015](/sources/source_015.md) - MultiHop-RAG 基准论文 (Tang et al., 2024)

## Claims

<a id="claim_015"></a>**claim_015** (supported): 多跳检索成功率随跳数增加急剧下降

# Citations

[1] [MultiHop-RAG：面向多跳推理的 RAG 评估基准 (2024)](/sources/source_015.md)
