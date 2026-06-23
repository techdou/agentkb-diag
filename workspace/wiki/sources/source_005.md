---
type: Source
title: 开放域问答系统中的检索方法评估
description: 系统评估开放域问答中的各类检索方法，提出DrQA系统
tags: [RAG, Open-Domain QA, Evaluation]
timestamp: "2026-05-01T10:00:00Z"
round_created: 1
round_updated: 1
okf_version: 0.1
authors: "Chen D, Fisch A, Weston J, Bordes A"
year: 2017
source_id: source_005
---

# 开放域问答系统中的检索方法评估

> Chen D, Fisch A, Weston J, Bordes A (2017)

> Chen D, Fisch A, Weston J, Bordes A. (2017)

## 摘要

系统评估开放域问答中的各类检索方法，提出 DrQA 系统，揭示检索质量对下游问答性能的关键影响。

## 提取的概念

- [RAG](/concepts/RAG.md) - 检索在 QA 中的作用
- [Dense_Retrieval](/concepts/Dense_Retrieval.md) - 对比不同检索方法

## 提取的声明

- [claim_005](/concepts/RAG.md#claim_005): 检索质量是影响端到端问答性能的首要因素

## 方法

DrQA 系统使用 TF-IDF 加词向量进行段落检索，然后使用文档阅读器抽取答案。

## 相关来源

- [source_001](/sources/source_001.md) - DPR 改进检索
- [source_010](/sources/source_010.md) - 事实验证中的检索
