---
type: Source
title: 基于对比学习的稠密检索表示优化
description: 提出SimCSE框架，通过对比学习优化稠密检索表示
tags: [RAG, Contrastive Learning, Dense Retrieval]
timestamp: "2026-05-01T10:00:00Z"
round_created: 1
round_updated: 1
okf_version: 0.1
authors: "Gao T, Yao X, Chen D"
year: 2021
source_id: source_009
---

# 基于对比学习的稠密检索表示优化

> Gao T, Yao X, Chen D (2021)

> Gao T, Yao X, Chen D. (2021)

## 摘要

提出 SimCSE 框架，利用对比学习优化稠密检索中的表示学习。

## 提取的概念

- [Dense_Retrieval](/concepts/Dense_Retrieval.md) - 对比学习改进稠密检索

## 提取的声明

- [claim_007](/concepts/Dense_Retrieval.md#claim_007): 对比学习可以显著提升稠密检索的表示质量

## 核心方法

使用 Dropout 噪声构造正样本对，在无监督语料上通过对比学习训练。

## 相关来源

- [source_001](/sources/source_001.md) - DPR 基础方法
- [source_003](/sources/source_003.md) - 检索方法综述
