---
type: Source
title: 面向知识密集型任务的检索与生成联合训练
description: 研究检索器与生成器的端到端联合训练方法
tags: [RAG, Joint Training, Knowledge-Intensive]
timestamp: "2026-05-01T10:00:00Z"
round_created: 1
round_updated: 1
okf_version: 0.1
authors: "Sachan D, Reddy S, Hamilton W, Dyer C, Yogatama D"
year: 2021
source_id: source_008
---

# 面向知识密集型任务的检索与生成联合训练

> Sachan D, Reddy S, Hamilton W, Dyer C, Yogatama D (2021)

---
type: Source
title: 面向知识密集型任务的检索与生成联合训练
description: 研究检索器与生成器的端到端联合训练方法
tags: [RAG, Joint Training, Knowledge-Intensive]
timestamp: "2026-05-01T10:00:00Z"
round_created: 1
round_updated: 1
okf_version: 0.1
authors: "Sachan D, Reddy S, Hamilton W, Dyer C, Yogatama D"
year: 2021
source_id: source_008
---


> Sachan D, Reddy S, Hamilton W, Dyer C, Yogatama D (2021)

> Sachan D, Reddy S, Hamilton W, Dyer C, Yogatama D. (2021)

## 摘要

研究检索器与生成器的端到端可微联合训练方法，允许梯度从生成器流回检索器。

## 提取的概念

- [RAG](/concepts/RAG.md) - 检索生成联合训练

## 提取的声明

- [claim_009](/concepts/RAG.md#claim_009): 检索与生成的联合训练可以提升两方面性能

## 关键发现

联合训练可提升检索和生成质量，但计算成本显著高于分离训练，且存在训练不稳定的问题。

## 相关来源

- [source_002](/sources/source_002.md) - RAG 分阶段训练
- [source_006](/sources/source_006.md) - FiD 多段落融合

<!-- DATASET_MAPPING_PROVENANCE -->

## 数据集映射说明（Dataset Mapping Provenance）

> 本 slot 在实验数据集中实际采用的论文（原始 source 预告的论文为虚构或仅近似）。

- **实际论文**: Distilling Knowledge from Reader to Retriever for Question Answering
- **arXiv ID**: [`2012.04584`](https://arxiv.org/abs/2012.04584)
- **映射类型**: `replace`
- **所在轮次**: round_1
- **说明**: Original 'Sachan 2021 joint training' not cleanly on arXiv; replaced with reader->retriever distillation, same joint-optimization theme.

完整转换文本见 `data/converted/round_1/source_008.md`（MinerU 从 PDF 解析）。

<!-- /DATASET_MAPPING_PROVENANCE -->
