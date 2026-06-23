---
type: Concept
title: KB Degradation
description: 知识库退化是指由 LLM Agent 持续自动维护的知识库在多轮更新后出现的结构劣化现象，包括概念孤岛增加、重复概念增多、知识冲突加剧和检索性能下降等问题。
tags: [kb-degradation]
timestamp: "2026-05-10T16:00:00Z"
round_created: 3
round_updated: 3
okf_version: 0.1
aliases: [知识库退化, 知识库劣化, 知识库维护退化]
claim_ids: [claim_027]
---

# KB Degradation

> Aliases: 知识库退化, 知识库劣化, 知识库维护退化

## 定义

知识库退化是指由 LLM Agent 持续自动维护的知识库在多轮更新后出现的结构劣化现象，包括概念孤岛增加、重复概念增多、知识冲突加剧和检索性能下降等问题。

## 关键声明

- [claim_027](/concepts/KB_Degradation.md#claim_027): 多轮 Agent 维护导致知识库检索召回率从 92% 降至 61% (支持)

## 退化现象

| 指标 | 维护前 | 维护后 | 变化 |
|------|--------|--------|------|
| 概念孤岛数量 | 1 | 4 | +300% |
| 重复概念率 | 5% | 22% | +340% |
| 知识冲突数量 | 2 | 10 | +400% |
| 检索召回率 | 92% | 61% | -34% |

## 相关概念

- [RAG](/concepts/RAG.md) - 知识库退化的核心研究领域

## 证据来源

- [source_029](/sources/source_029.md) - 知识库自动维护退化 (Zhang et al., 2024)

## Claims

<a id="claim_027"></a>**claim_027** (supported): 多轮Agent维护导致知识库检索召回率从92%降至61%

# Citations

[1] [知识库的自动维护退化：多轮 Agent 更新下的知识结构劣化研究 (2024)](/sources/source_029.md)
