---
type: Source
title: 知识密集型 NLP 任务中的检索方法综述
description: 系统综述面向知识密集型NLP任务的检索方法，分为稀疏、稠密和混合三类
tags: [RAG, Knowledge Retrieval, Survey]
timestamp: "2026-05-01T10:00:00Z"
round_created: 1
round_updated: 1
okf_version: 0.1
authors: "Lin J, Nogueira R, Yates A"
year: 2021
source_id: source_003
---

# 知识密集型 NLP 任务中的检索方法综述

> Lin J, Nogueira R, Yates A (2021)

> Lin J, Nogueira R, Yates A. (2021)

## 摘要

系统综述了面向知识密集型 NLP 的检索方法，将其分为稀疏检索、稠密检索和混合检索三类。

## 提取的概念

- [Dense_Retrieval](/concepts/Dense_Retrieval.md) - 综述稠密检索方法（DPR, ColBERT）
- [RAG](/concepts/RAG.md) - 讨论检索与生成的结合方式

## 提取的声明

- [claim_004](/concepts/Dense_Retrieval.md#claim_004): 稀疏检索在精确匹配场景下仍优于稠密检索
- [claim_002](/concepts/Dense_Retrieval.md#claim_002): 双编码器架构是稠密检索的最优架构选择

## 方法分类

| 类别 | 代表方法 | 优势 |
|------|---------|------|
| 稀疏检索 | BM25, SPLADE | 精确匹配 |
| 稠密检索 | DPR, ColBERT | 语义匹配 |
| 混合检索 | 两者结合 | 综合优势 |

## 相关来源

- [source_001](/sources/source_001.md) - DPR 方法
- [source_009](/sources/source_009.md) - SimCSE 对比学习
