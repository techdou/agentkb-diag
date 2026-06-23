---
type: Source
title: FiD：融合解码器——多检索段落的知识融合方法
description: 提出FiD架构，每个段落分别编码后解码器融合所有段落信息
tags: [RAG, Fusion-in-Decoder, Multi-Paragraph Reasoning]
timestamp: "2026-05-01T10:00:00Z"
round_created: 1
round_updated: 1
okf_version: 0.1
authors: "Izacard G, Grave E"
year: 2021
source_id: source_006
---

# FiD：融合解码器——多检索段落的知识融合方法

> Izacard G, Grave E (2021)

---
type: Source
title: FiD：融合解码器——多检索段落的知识融合方法
description: 提出FiD架构，每个段落分别编码后解码器融合所有段落信息
tags: [RAG, Fusion-in-Decoder, Multi-Paragraph Reasoning]
timestamp: "2026-05-01T10:00:00Z"
round_created: 1
round_updated: 1
okf_version: 0.1
authors: "Izacard G, Grave E"
year: 2021
source_id: source_006
---


> Izacard G, Grave E (2021)

> Izacard G, Grave E. (2021)

## 摘要

提出 FiD 架构，每个检索到的段落与问题拼接后分别编码，解码器融合所有段落信息。

## 提取的概念

- [RAG](/concepts/RAG.md) - 多段落融合方法

## 提取的声明

- [claim_006](/concepts/RAG.md#claim_006): FiD 随检索段落数增加性能持续提升

## 关键创新

FiD 突破了此前方法在段落过多时性能下降的瓶颈。实验表明，随着检索段落数量增加，FiD 的性能持续提升。

## 相关来源

- [source_002](/sources/source_002.md) - RAG 基础框架
- [source_008](/sources/source_008.md) - 检索生成联合训练
