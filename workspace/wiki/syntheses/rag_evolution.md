---
type: Synthesis
title: RAG 技术演进综合报告
description: RAG 技术演进综合报告 - 跨概念综合分析。
tags: [synthesis]
timestamp: "2026-05-10T16:00:00Z"
round_created: 3
round_updated: 3
okf_version: 0.1
---

# RAG 技术演进综合报告

## 概述

本文综合分析了 RAG 技术从 2020 年到 2024 年的发展演进，基于 30 篇核心论文的系统梳理。

## 阶段一：基础奠基（Round 1）

2020-2022年是RAG基础框架的建立期。核心工作包括：

1. **DPR** (Karpukhin et al., 2020): 稠密检索替代BM25，奠定检索基础
2. **RAG** (Lewis et al., 2020): 检索+生成端到端框架正式确立
3. **REALM** (Guu et al., 2020): 检索增强预训练
4. **FiD** (Izacard & Grave, 2021): 多段落融合方案
5. **SimCSE** (Gao et al., 2021): 对比学习优化检索表示

此阶段的主要特征是"检索+生成"的简单流水线，检索和生成组件各自独立优化。

## 阶段二：范式的多元化（Round 2）

2023-2024年，RAG范式开始从单一流水线向多元架构演进：

1. **GraphRAG** (Edge et al., 2024): 引入知识图谱结构
2. **Agentic RAG** (Wang et al., 2024): 智能体作为控制器
3. **Self-RAG** (Asai et al., 2023): 自反思检-生-判循环
4. **CRAG** (Yan et al., 2024): 纠错机制增强鲁棒性
5. **Adaptive RAG** (Jeong et al., 2024): 查询复杂度驱动的自适应检索
6. **KG-RAG** (Sun et al., 2024): 知识图谱与向量检索混合

## 阶段三：反思与批判（Round 3）

2024年，领域进入自我反思阶段：

1. **RAG vs 长上下文**: 检索是否仍然必要的核心争议
2. **GraphRAG vs 向量RAG**: 图结构复杂性的价值质疑
3. **概念重复**: 约49%的"创新"实为重复概念
4. **失效分析**: 35%边缘案例下产生不可靠输出
5. **评估批判**: 自动化评估框架的系统性偏差

## 关键趋势

1. 从静态到动态：检索策略越来越智能化
2. 从单模态到多模态：跨模态RAG成为新方向
3. 从单一到混合：图+向量、检索+微调等多方案融合
4. 从构建到维护：知识库的持续维护和退化问题受到关注

## 相关页面

- [rag_conflicts](/syntheses/rag_conflicts.md) - 主要争论与冲突观点
- [kb_health](/syntheses/kb_health.md) - 知识库健康状态分析
- [RAG](/concepts/RAG.md) - RAG 概念页面
