---
type: Source
title: RAG 中的评估指标与基准：系统综述
description: 系统综述RAG评估指标和基准数据集
tags: [RAG, Evaluation, Metrics]
timestamp: "2026-05-01T10:00:00Z"
round_created: 1
round_updated: 1
okf_version: 0.1
authors: "Liu Y, Zhang M, Yang Y"
year: 2022
source_id: source_007
---

# RAG 中的评估指标与基准：系统综述

> Liu Y, Zhang M, Yang Y (2022)

---
type: Source
title: RAG 中的评估指标与基准：系统综述
description: 系统综述RAG评估指标和基准数据集
tags: [RAG, Evaluation, Metrics]
timestamp: "2026-05-01T10:00:00Z"
round_created: 1
round_updated: 1
okf_version: 0.1
authors: "Liu Y, Zhang M, Yang Y"
year: 2022
source_id: source_007
---


> Liu Y, Zhang M, Yang Y (2022)

> Liu Y, Zhang M, Yang Y. (2022)

## 摘要

系统综述 RAG 评估指标和基准数据集，将评估指标分为检索质量、生成质量和端到端三类。

## 提取的概念

- [RAG_Evaluation](/concepts/RAG_Evaluation.md) - RAG 评估框架

## 提取的声明

- [claim_005](/concepts/RAG.md#claim_005): 检索质量是影响端到端问答性能的首要因素

## 指标分类

1. 检索质量: Recall@k, MRR, NDCG
2. 生成质量: ROUGE, BLEU, F1
3. 端到端: 答案准确率, 忠实度

## 相关来源

- [source_018](/sources/source_018.md) - RAGAS 评估框架
- [source_026](/sources/source_026.md) - 评估框架的批判性分析

<!-- DATASET_MAPPING_PROVENANCE -->

## 数据集映射说明（Dataset Mapping Provenance）

> 本 slot 在实验数据集中实际采用的论文（原始 source 预告的论文为虚构或仅近似）。

- **实际论文**: Retrieval-Augmented Generation for AI-Generated Content: A Survey
- **arXiv ID**: [`2402.19473`](https://arxiv.org/abs/2402.19473)
- **映射类型**: `replace`
- **所在轮次**: round_1
- **说明**: Original 'Liu 2022 RAG eval survey' author was vague; replaced with Zhao et al. RAG survey (arXiv 2402.19473) covering RAG evaluation and taxonomy.

完整转换文本见 `data/converted/round_1/source_007.md`（MinerU 从 PDF 解析）。

<!-- /DATASET_MAPPING_PROVENANCE -->
