---
type: Source
title: Dense Passage Retrieval：面向开放域问答的稠密检索方法
description: 提出DPR框架，使用双编码器架构将问题和段落分别编码到稠密向量空间中，在多个开放域问答基准上取得显著提升
tags: [RAG, Dense Retrieval, Open-Domain QA]
timestamp: "2026-05-01T10:00:00Z"
round_created: 1
round_updated: 1
okf_version: 0.1
authors: "Karpukhin V, Oğuz B, Min S, Lewis P, Wu L, Edunov S, Chen D, Yih W"
year: 2020
source_id: source_001
---

# Dense Passage Retrieval：面向开放域问答的稠密检索方法

> Karpukhin V, Oğuz B, Min S, Lewis P, Wu L, Edunov S, Chen D, Yih W (2020)

> Karpukhin V, Oğuz B, Min S, Lewis P, Wu L, Edunov S, Chen D, Yih W. (2020)

## 摘要

本文提出 Dense Passage Retrieval (DPR) 框架，使用双编码器架构将问题和段落分别编码到稠密向量空间中，在多个开放域问答基准上显著超越 BM25。

## 提取的概念

- [Dense_Retrieval](/concepts/Dense_Retrieval.md) - 本文是稠密检索领域的奠基性工作
- [RAG](/concepts/RAG.md) - DPR 被广泛用作 RAG 系统的检索组件

## 提取的声明

- [claim_001](/concepts/RAG.md#claim_001): DPR 在开放域问答中显著优于 BM25
- [claim_002](/concepts/Dense_Retrieval.md#claim_002): 双编码器架构是稠密检索的最优架构选择

## 方法细节

DPR 使用两个 BERT 编码器分别编码问题(q)和段落(p)，通过内积计算相关性得分：

$$s(q, p) = E_Q(q)^T E_P(p)$$

训练使用以下负采样策略：
1. 随机负样本：批次内的其他段落
2. BM25 难负样本：BM25 检索到但未包含答案的段落

## 关键结果

| 数据集 | DPR Top-20 | BM25 Top-20 | 提升 |
|--------|-----------|-------------|------|
| Natural Questions | 78.4% | 59.1% | +19.3% |
| TriviaQA | 85.7% | 76.2% | +9.5% |
| WebQuestions | 75.0% | 66.1% | +8.9% |

## 相关来源

- [source_003](/sources/source_003.md) - 检索方法综述
- [source_009](/sources/source_009.md) - 对比学习改进稠密检索
