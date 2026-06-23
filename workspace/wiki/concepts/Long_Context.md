---
type: Concept
title: Long-Context
description: "长上下文模型是指支持超长输入上下文窗口（100K tokens 以上）的大语言模型，如 GPT-4-128K 和 Claude-100K。这类模型引发了\"检索是否仍然必要\"的核心争议。"
tags: [long-context]
timestamp: "2026-05-10T16:00:00Z"
round_created: 3
round_updated: 3
okf_version: 0.1
aliases: [长上下文, 超长上下文, Long-context LM]
claim_ids: [claim_019]
---

# Long-Context

> Aliases: 长上下文, 超长上下文, Long-context LM

## 定义

长上下文模型是指支持超长输入上下文窗口（100K tokens 以上）的大语言模型，如 GPT-4-128K 和 Claude-100K。这类模型引发了"检索是否仍然必要"的核心争议。

## 关键声明

- [claim_018](/concepts/RAG.md#claim_018): 长上下文模型在知识源小于100K tokens时表现与RAG相当 (支持)
- [claim_019](/concepts/Long_Context.md#claim_019): 长上下文模型在超过50K tokens时中间位置信息召回率低于40% (支持)

## 与 RAG 的关系

长上下文模型与 RAG 存在竞争与互补关系：
- 小规模知识源（<100K tokens）: 长上下文模型可与 RAG 媲美
- 大规模知识源: RAG 仍具优势
- "迷失在中间"问题: 长上下文对中间位置信息关注不足

## 相关概念

- [RAG](/concepts/RAG.md) - 长上下文模型被视为 RAG 的替代方案

## 证据来源

- [source_021](/sources/source_021.md) - RAG vs 长上下文 (Li et al., 2024)
- [source_022](/sources/source_022.md) - 检索瓶颈与长上下文 (Chen et al., 2024)

## Claims

<a id="claim_019"></a>**claim_019** (supported): 长上下文模型在超过50K tokens时中间位置信息召回率低于40%

# Citations

[1] [RAG 系统在大规模知识库中的检索瓶颈与长上下文解决方案 (2024)](/sources/source_022.md)
