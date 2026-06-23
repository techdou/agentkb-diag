# AgentKB-Diag 产品需求与系统设计文档

## 0. 项目定位

### 0.1 项目名称

**AgentKB-Diag：面向智能体维护知识库的可检索性退化诊断系统**

### 0.2 一句话定位

AgentKB-Diag 是一个面向智能体维护 Wiki 型知识库的学术可视分析系统，用于诊断知识库在多轮自动维护过程中出现的引用缺失、概念孤岛、重复概念、知识冲突和检索失败等问题，并解释这些结构性问题如何导致可检索性退化。

### 0.3 通俗类比

知识库像图书馆。LLM Agent 负责不断买书、分类、写目录、贴标签、建立索引。时间一长，可能出现目录错乱、同一本书放了多个书架、旧标签没更新、关键书没人能搜到。AgentKB-Diag 不是新造一个图书馆，而是做一个“图书馆体检仪”，告诉用户哪里乱了、为什么影响检索、修复后是否变好。

### 0.4 研究定位

本系统不以提升单次问答效果为核心目标，而是研究：

> 由 LLM Agent 持续维护的 Wiki 型知识库是否会在多轮更新后发生可检索性退化？如果会，如何发现、归因和修复？

### 0.5 论文关键词

- LLM Agent，大语言模型智能体
- Knowledge Base，知识库
- Wiki-RAG，Wiki 型检索增强生成
- Retrievability Degradation，可检索性退化
- Knowledge Health Diagnosis，知识健康诊断
- Visual Analytics，可视分析
- Citation Coverage，引用覆盖率
- Orphan Concept，概念孤岛
- Duplicate Concept，重复概念
- Retrieval Failure Attribution，检索失败归因

---

## 1. 产品需求 PRD

## 1.1 目标用户

### 主要用户

1. **科研人员 / 研究生**
   - 长期阅读论文、博客、项目文档。
   - 希望自动维护个人科研知识库。
   - 关心知识是否可靠、是否可追溯、是否容易检索。

2. **RAG / Agent 系统开发者**
   - 需要调试由 Agent 自动维护的知识库。
   - 需要知道检索失败不是“模型笨”，而是知识库结构出了问题。

3. **论文审稿视角下的系统使用者**
   - 关注系统是否有明确任务、数据模型、指标体系和案例验证。

### 非目标用户

1. 只想做日常笔记管理的普通用户。
2. 只想要炫酷知识图谱大屏的展示型用户。
3. 只关注最终答案生成质量、不关心知识结构的人。

---

## 1.2 核心用户故事

### 用户故事 1：发现知识库是否退化

作为研究者，我希望看到知识库从 Round 1 到 Round 3 的健康指标变化，以便判断多轮 Agent 维护是否导致知识库结构变差。

验收标准：

- 可以看到 Citation Coverage、Orphan Rate、Duplicate Rate、Conflict Density、Recall@3、MRR 的轮次变化。
- 可以看到 Round 3 是否比 Round 1 出现更多结构问题。
- 可以看到 Repair 后检索指标是否恢复。

### 用户故事 2：定位知识结构异常

作为开发者，我希望看到 Wiki 页面之间的链接结构，快速发现孤立页面、重复概念和冲突概念。

验收标准：

- 页面以节点形式展示。
- 页面链接以边展示。
- 孤岛页面、重复概念、冲突页面有明显标记。
- 点击节点后，右侧显示该页面的诊断问题和修复建议。

### 用户故事 3：解释具体查询为什么失败

作为系统调试者，我希望输入一个查询后，系统不仅显示 Top-k 检索结果，还能解释为什么期望页面没有被召回。

验收标准：

- 显示 query、expected pages、retrieved pages。
- 标出命中 / 未命中。
- 给出失败归因：别名缺失、概念重复、页面孤岛、断链、无引用主张等。
- 给出可执行修复建议。

### 用户故事 4：追踪知识主张的来源

作为科研用户，我希望看到 Wiki 页面中的关键知识主张来自哪些原始资料，以便判断它们是否可信。

验收标准：

- 每条 claim 绑定 source_id。
- 无来源 claim 被标红。
- 可以从 claim 回溯到 source。
- 可以显示 claim 是否与其他 claim 存在冲突。

### 用户故事 5：验证修复是否有效

作为论文实验者，我希望根据系统建议修复知识库后重新运行检索评估，以便证明诊断系统不只是发现问题，还能改善检索可靠性。

验收标准：

- 支持保存 Before Repair 和 After Repair 的指标。
- 支持对比 Recall@3、MRR、Duplicate Rate、Orphan Rate 等指标。
- 支持导出实验表格。

---

## 1.3 MVP 范围

### 必做功能 P0

1. 原始资料导入
2. 三轮知识库构建
3. Wiki 页面生成与浏览
4. Claim、Citation、Concept、Link 数据结构生成
5. 知识健康诊断
6. 检索评估
7. 演化总览视图
8. 知识结构图视图
9. 检索失败归因视图
10. 实验结果导出

### 应做功能 P1

1. Claim-Citation 主张溯源图
2. 修复前后对比视图
3. Alias 别名映射管理
4. 页面合并建议
5. 诊断报告 Markdown 导出

### 可延后 P2

1. 用户研究任务记录
2. 多用户协作
3. Obsidian 插件集成
4. 复杂 3D 图谱
5. 全自动修复提交
6. 多模态资料处理

---

## 1.4 非目标功能

第一版不做：

1. 不做完整多 Agent 问答协作诊断。
2. 不做复杂 AgentRAG-Diag 的跨 Agent 噪声传播追踪。
3. 不做模型训练。
4. 不追求 RAG 问答 SOTA。
5. 不做炫酷大屏。
6. 不做商业知识库管理系统。

---

## 2. 核心概念定义

## 2.1 KB

KB 是 Knowledge Base，中文为知识库。本文中的 KB 指由 LLM Agent 自动维护的 Wiki 型知识库。

## 2.2 AgentKB

AgentKB 指由一个或多个 LLM Agent 负责维护的知识库。Agent 可以完成资料导入、摘要生成、概念抽取、Wiki 编写、链接维护和检索问答等任务。

## 2.3 Diag

Diag 是 Diagnosis / Diagnostic 的缩写，中文为诊断。AgentKB-Diag 指面向 AgentKB 的诊断系统。

## 2.4 Claim

Claim 推荐翻译为“知识主张”。它是一句可以被证据支持或反驳的结论性陈述。

例子：

> GraphRAG 通过图结构增强复杂关系型问题的检索能力。[source_003]

这句话就是一个 claim，因为它能被来源资料验证。

## 2.5 Citation

Citation 是引用关系，表示某个 claim 由哪个 source 支持。

## 2.6 Concept

Concept 是概念，例如 RAG、GraphRAG、Agentic RAG、Citation Faithfulness。

## 2.7 Orphan Concept

Orphan Concept 是概念孤岛，指没有入链或出链的概念页面。它可能导致知识库中已有内容无法通过链接路径或检索扩展被找到。

## 2.8 Duplicate Concept

Duplicate Concept 是重复概念，指多个页面描述高度相似或相同概念，但没有建立合并或别名关系。

例如：

- Agentic_RAG.md
- RAG_Agent.md
- Agent-based_RAG.md

## 2.9 Retrievability Degradation

可检索性退化，指知识仍然存在于知识库中，但因为结构、链接、索引或命名问题，导致检索系统难以稳定召回正确页面或证据。

---

## 3. Wiki 知识库架构设计

## 3.1 设计原则

1. **Plain files first**：优先使用 Markdown + JSON，便于调试、复现和论文展示。
2. **Source traceable**：每条关键知识主张必须能回溯到原始资料。
3. **Link explicit**：概念之间的关系尽量通过显式 wikilink 表达。
4. **Round aware**：所有页面、claim、link 都要记录产生或更新轮次。
5. **Diagnosis friendly**：数据结构必须天然支持诊断指标计算。
6. **Experiment reproducible**：每一轮的输入、输出、指标、日志都可以保存。

---

## 3.2 推荐目录结构

```text
agentkb-diag/
  data/
    raw/
      round_1/
      round_2/
      round_3/
    converted/
      round_1/
      round_2/
      round_3/

  workspace/
    wiki/
      index.md
      overview.md
      log.md
      sources/
        source_001.md
        source_002.md
      concepts/
        RAG.md
        GraphRAG.md
        Agentic_RAG.md
      syntheses/
        rag_evaluation_summary.md

    index/
      source_index.json
      claim_index.json
      concept_index.json
      link_graph.json
      citation_graph.json
      alias_map.json
      retrieval_tests.json

    rounds/
      round_1/
        build_snapshot.json
        health_report.json
        retrieval_eval.json
      round_2/
        build_snapshot.json
        health_report.json
        retrieval_eval.json
      round_3/
        build_snapshot.json
        health_report.json
        retrieval_eval.json
      round_3_repair/
        build_snapshot.json
        health_report.json
        retrieval_eval.json

    reports/
      health_report_round_1.md
      health_report_round_2.md
      health_report_round_3.md
      repair_report.md
      experiment_table.csv

  backend/
  frontend/
  docs/
```

---

## 3.3 与 llm-wiki-agent 的关系

可以参考 llm-wiki-agent 的结构思想，但不要完全照搬。

### 可以参考的点

1. `raw/` 存放原始资料。
2. `wiki/index.md` 作为页面目录。
3. `wiki/log.md` 作为追加式操作记录。
4. `wiki/overview.md` 作为动态综述页。
5. `wiki/sources/` 存放每个 source 的摘要页面。
6. `wiki/concepts/` 存放概念页面。
7. `wiki/syntheses/` 存放查询后形成的综合页面。
8. `graph/graph.json` 存储节点和边。
9. 使用 `[[wikilink]]` 表示显式链接。
10. lint 检查孤岛、断链、矛盾和信息缺口。

### 需要改造的点

llm-wiki-agent 更像“自动生成和维护 Wiki 的个人知识库工具”。AgentKB-Diag 的目标不是只生成 Wiki，而是研究和诊断：

1. 知识库多轮维护是否发生退化。
2. 退化具体由哪些结构问题导致。
3. 这些结构问题如何影响检索性能。
4. 修复后检索性能是否恢复。

因此 AgentKB-Diag 需要额外设计：

1. Round-aware metadata：记录每条数据属于哪一轮。
2. Claim-level citation graph：支持引用覆盖率计算。
3. Retrieval test set：支持 Recall@k 和 MRR 评估。
4. Failure attribution：支持查询失败归因。
5. Repair logging：记录修复前后指标变化。
6. Visual analytics API：服务前端多层次可视分析。

---

## 3.4 Source 页面模板

```markdown
---
type: source
source_id: source_001
title: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
year: 2020
round: 1
tags: [RAG, Dense Retrieval]
---

# source_001: Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks

## Bibliographic Info
- Title: ...
- Authors: ...
- Year: ...
- Venue: ...

## Summary
简要总结该来源的核心内容。

## Key Contributions
- Contribution 1
- Contribution 2

## Extracted Concepts
- [[RAG]]
- [[Dense Retrieval]]
- [[Knowledge-Intensive NLP]]

## Extracted Claims
- Claim: RAG combines parametric generation with non-parametric retrieval. [source_001]
- Claim: Retrieval can improve knowledge-intensive NLP tasks. [source_001]

## Notes
其他备注。
```

---

## 3.5 Concept 页面模板

```markdown
---
type: concept
concept_id: concept_rag
canonical_name: RAG
aliases: [Retrieval-Augmented Generation, 检索增强生成]
round_created: 1
round_updated: 2
status: active
---

# RAG

## Definition
RAG，Retrieval-Augmented Generation，中文为检索增强生成，是一种将外部知识检索与大语言模型生成相结合的方法。

## Key Claims
- Claim c_001: RAG 通过检索外部文档增强生成模型的知识访问能力。[source_001]
- Claim c_002: RAG 的效果依赖检索质量和生成器对证据的利用能力。[source_004]

## Related Concepts
- [[Dense Retrieval]]
- [[Citation Faithfulness]]
- [[GraphRAG]]
- [[Agentic RAG]]

## Evidence Sources
- source_001
- source_004

## Open Issues
- 是否存在与其他页面的重复？
- 是否存在旧定义未更新？

## Update History
- Round 1: created from source_001.
- Round 2: updated with source_004.
```

---

## 3.6 Synthesis 页面模板

```markdown
---
type: synthesis
synthesis_id: synthesis_001
query: "GraphRAG 和普通 RAG 有什么区别？"
round_created: 3
sources: [source_003, source_006]
---

# GraphRAG 和普通 RAG 的区别

## Answer Summary
综合回答。

## Supporting Claims
- c_011
- c_018

## Retrieved Pages
- [[GraphRAG]]
- [[RAG]]
- [[Knowledge Graph]]

## Gaps Found
- 缺少 GraphRAG 失败场景资料。
- KG-RAG 与 GraphRAG 的别名关系未明确。
```

---

## 3.7 JSON 数据结构

### source_index.json

```json
{
  "sources": [
    {
      "source_id": "source_001",
      "title": "...",
      "year": 2020,
      "round": 1,
      "path": "wiki/sources/source_001.md",
      "concepts": ["RAG", "Dense Retrieval"]
    }
  ]
}
```

### claim_index.json

```json
{
  "claims": [
    {
      "claim_id": "c_001",
      "text": "RAG 通过检索外部文档增强生成模型的知识访问能力。",
      "page_id": "RAG",
      "source_ids": ["source_001"],
      "round_created": 1,
      "round_updated": 1,
      "status": "supported"
    }
  ]
}
```

### concept_index.json

```json
{
  "concepts": [
    {
      "concept_id": "concept_rag",
      "canonical_name": "RAG",
      "aliases": ["Retrieval-Augmented Generation", "检索增强生成"],
      "page_id": "RAG",
      "round_created": 1,
      "round_updated": 2
    }
  ]
}
```

### link_graph.json

```json
{
  "nodes": [
    {
      "id": "RAG",
      "type": "concept_page",
      "label": "RAG",
      "round_created": 1,
      "issue_flags": []
    }
  ],
  "edges": [
    {
      "source": "RAG",
      "target": "GraphRAG",
      "type": "wikilink",
      "round_created": 2,
      "confidence": 1.0
    }
  ]
}
```

### alias_map.json

```json
{
  "aliases": [
    {
      "alias": "RAG Agent",
      "canonical": "Agentic RAG",
      "confidence": 0.87,
      "status": "suggested"
    }
  ]
}
```

### retrieval_tests.json

```json
{
  "tests": [
    {
      "query_id": "q_001",
      "query": "GraphRAG 和普通 RAG 的区别是什么？",
      "expected_pages": ["GraphRAG", "RAG"],
      "expected_claims": ["c_011", "c_018"],
      "query_type": "comparison"
    }
  ]
}
```

---

## 4. 系统架构设计

## 4.1 总体架构

```text
Raw Sources
  ↓
Document Conversion
  ↓
Agent Maintenance Pipeline
  ↓
Wiki Knowledge Base
  ↓
Knowledge Health Diagnosis
  ↓
Retrieval Evaluation
  ↓
Visual Analytics Frontend
```

---

## 4.2 后端模块

### 4.2.1 Ingest Service

职责：

- 接收 Markdown、PDF 转换文本或手动输入资料。
- 分配 source_id。
- 存储到 raw / converted。
- 记录 round 信息。

核心 API：

```http
POST /api/sources/upload
POST /api/sources/import-demo
GET /api/sources
GET /api/sources/{source_id}
```

---

### 4.2.2 Agent Pipeline Service

职责：

- 调用不同 Agent 生成 Wiki 内容。
- 支持规则模式和 LLM 模式。
- 记录 agent logs。

Agent 划分：

1. Ingest Agent：资料导入。
2. Summary Agent：生成摘要。
3. Concept Agent：抽取概念。
4. Claim Agent：抽取知识主张。
5. Wiki Writer Agent：生成页面。
6. Link Agent：生成链接。
7. Update Agent：多轮更新旧页面。

核心 API：

```http
POST /api/pipeline/build?round=1
GET /api/pipeline/logs
GET /api/pipeline/status
```

---

### 4.2.3 Wiki Service

职责：

- 读取 Wiki 页面。
- 更新 Wiki 页面。
- 提供页面列表、页面内容、页面元数据。

核心 API：

```http
GET /api/wiki/pages
GET /api/wiki/pages/{page_id}
PUT /api/wiki/pages/{page_id}
GET /api/wiki/overview
```

---

### 4.2.4 Diagnosis Service

职责：

- 计算知识健康指标。
- 输出问题列表。
- 给出修复建议。

诊断模块：

1. Citation Diagnosis：引用缺失诊断。
2. Orphan Diagnosis：概念孤岛诊断。
3. Duplicate Diagnosis：重复概念诊断。
4. Conflict Diagnosis：知识冲突诊断。
5. Link Diagnosis：断链诊断。
6. Retrieval Failure Attribution：检索失败归因。

核心 API：

```http
POST /api/diagnosis/run?round=3
GET /api/diagnosis/summary?round=3
GET /api/diagnosis/issues?round=3
GET /api/diagnosis/issues/{issue_id}
```

---

### 4.2.5 Retrieval Service

职责：

- 对 Wiki 页面和 claim 建索引。
- 执行查询。
- 返回 Top-k 结果。
- 计算 Recall@k、MRR。

核心 API：

```http
POST /api/retrieval/search
POST /api/retrieval/evaluate?round=3
GET /api/retrieval/eval-summary?round=3
GET /api/retrieval/failures?round=3
```

---

### 4.2.6 Experiment Service

职责：

- 管理实验轮次。
- 保存每轮快照。
- 生成实验表格。
- 支持修复前后对比。

核心 API：

```http
POST /api/experiments/run-round
POST /api/experiments/run-all
GET /api/experiments/rounds
GET /api/experiments/metrics
GET /api/experiments/export
```

---

### 4.2.7 Graph Service

职责：

- 提供前端图数据。
- 支持按 round、issue type、query 过滤图结构。

核心 API：

```http
GET /api/graph/knowledge?round=3
GET /api/graph/provenance?claim_id=c_001
GET /api/graph/failure?query_id=q_001
```

---

## 4.3 前端模块

推荐技术栈：

- React + TypeScript + Vite
- React Flow：知识结构图
- Recharts / ECharts：趋势图与指标图
- react-markdown：Wiki 页面渲染
- lucide-react：图标
- Zustand 或 useReducer：状态管理

---

## 5. 可视化产品设计

## 5.1 设计风格

目标风格：

> 清晰、克制、信息密度高、能解释问题。

不要做：

- 炫酷科技大屏
- 花哨渐变
- 复杂 3D 图
- 无意义动画
- 普通 CRUD 后台

要做：

- 学术可视分析系统
- 多视图协调联动
- 指标、图结构、证据、失败归因统一呈现
- 图表要能回答研究问题

---

## 5.2 总体布局

```text
┌──────────────────────────────────────────────────────────┐
│ Top Bar: Dataset / Round / Run Experiment / Export        │
├───────────────┬───────────────────────────┬──────────────┤
│ Sidebar       │ Main View                 │ Inspector    │
│               │                           │              │
│ Overview      │ Trend Chart / Graph       │ Selected     │
│ Structure     │ Retrieval Case            │ Issues       │
│ Provenance    │ Experiment Table          │ Repair Tips  │
│ Failure       │                           │              │
│ Experiment    │                           │              │
└───────────────┴───────────────────────────┴──────────────┘
```

左侧：导航。
顶部：数据集、轮次、运行按钮。
中间：主可视化区域。
右侧：详情检查器。

---

## 5.3 页面 1：Evolution Overview，演化总览

### 目标

回答：

> 知识库健康是否随着 Agent 多轮维护发生退化？退化是否影响检索性能？

### 主要组件

1. Metric Cards 指标卡片
   - Citation Coverage
   - Orphan Rate
   - Duplicate Rate
   - Conflict Density
   - Recall@3
   - MRR

2. Health Evolution Chart
   - X 轴：Round 1、Round 2、Round 3、Repair
   - Y 轴：健康指标与检索指标

3. Key Findings Panel
   - 自动总结本轮主要问题。

4. Round Snapshot Table
   - 每轮页面数、claim 数、source 数、issue 数。

### 交互

- 点击某个指标，跳转到对应问题列表。
- 点击某个轮次，切换全局 round。
- 点击 Repair 后对比修复前后指标。

### 可视化创新点

将知识健康指标和检索性能指标放在同一演化轴上，支持用户观察“结构退化—检索退化—诊断修复”的关系。

---

## 5.4 页面 2：Knowledge Structure View，知识结构视图

### 目标

回答：

> 知识库哪里乱了？哪些页面是孤岛？哪些概念重复？哪些链接断了？

### 节点设计

| 节点类型 | 视觉编码 |
|---|---|
| 普通概念页面 | 蓝灰色圆点 |
| 孤岛页面 | 红色描边 |
| 重复概念 | 橙色描边 |
| 冲突页面 | 紫色警告标记 |
| 高检索命中页面 | 节点更大 |

### 边设计

| 边类型 | 视觉编码 |
|---|---|
| wikilink | 实线 |
| inferred link | 虚线 |
| duplicate relation | 橙色虚线 |
| conflict relation | 紫色线 |

### 右侧 Inspector

点击节点后显示：

- 页面名称
- 页面类型
- 入链数 / 出链数
- 相关 claim
- 相关 source
- 诊断问题
- 修复建议

### 交互

- 按 issue type 过滤节点。
- 按 round 过滤节点。
- 点击重复边，显示两个页面的相似原因。
- 点击孤岛节点，显示可能应连接的页面。

---

## 5.5 页面 3：Claim Provenance View，主张溯源视图

### 目标

回答：

> 页面里的关键结论有没有来源？来源是否支持它？是否和其他 claim 冲突？

### 数据路径

```text
Source → Claim → Wiki Page → Query
```

### 主要组件

1. Claim List
   - 展示所有 claim。
   - 标记 supported / unsupported / conflicted。

2. Provenance Graph
   - Source 节点
   - Claim 节点
   - Page 节点
   - Query 节点

3. Evidence Inspector
   - 显示 source 摘要。
   - 显示 claim 文本。
   - 显示支持或冲突关系。

### 交互

- 点击 claim，高亮其来源和所在页面。
- 点击 unsupported claim，显示补引用建议。
- 点击 conflicted claim，显示冲突 claim pair。

---

## 5.6 页面 4：Retrieval Failure View，检索失败归因视图

### 目标

回答：

> 为什么知识库里明明有相关知识，但检索没有召回？

### 三栏布局

```text
┌──────────────┬───────────────────┬────────────────────┐
│ Query Panel  │ Retrieval Results │ Failure Attribution │
└──────────────┴───────────────────┴────────────────────┘
```

### Query Panel

- Query 文本
- Query 类型
- Expected Pages
- Expected Claims
- Round

### Retrieval Results

- Top-k 页面
- 分数
- 是否命中 expected pages
- 页面摘要
- 关键 claim

### Failure Attribution

可能原因：

1. Expected page 是孤岛。
2. Expected page 与另一个页面重复，索引分散。
3. 缺少 alias 映射。
4. 页面没有被相关概念链接。
5. 关键 claim 缺少引用。
6. Query 词与页面 canonical name 不匹配。
7. 旧页面未被新资料更新。

### 修复建议

- Add alias: KG-RAG → Knowledge Graph RAG
- Link GraphRAG ↔ KG-RAG
- Merge RAG_Agent into Agentic_RAG
- Add citation to unsupported claim
- Rebuild concept index

### 可视化创新点

普通检索系统只显示“检索失败”。本视图将失败归因到知识库演化过程中产生的结构性问题。

---

## 5.7 页面 5：Experiment Dashboard，实验面板

### 目标

回答：

> 实验设计是否可复现？可视化结果如何支撑论文表格？

### 组件

1. Round Runner
   - Run Round 1
   - Run Round 2
   - Run Round 3
   - Run Repair

2. Method Comparison Table
   - Raw-doc RAG
   - Static Wiki-RAG
   - Agent-maintained Wiki
   - AgentKB-Diag

3. Metrics Table
   - Citation Coverage
   - Orphan Rate
   - Duplicate Rate
   - Conflict Density
   - Recall@3
   - MRR

4. Export Panel
   - Export CSV
   - Export JSON
   - Export Markdown Report

---

## 6. 实验如何关联可视化

## 6.1 核心逻辑链

实验和可视化必须服务同一条论文主线：

```text
多轮 Agent 维护
  ↓
知识结构问题增加
  ↓
可检索性退化
  ↓
可视化定位退化原因
  ↓
修复后检索性能恢复
```

---

## 6.2 实验轮次与可视化映射

| 实验阶段 | 后端产物 | 前端视图 | 证明什么 |
|---|---|---|---|
| Round 1 | 初始 wiki、健康指标、检索指标 | Evolution Overview | 初始状态 |
| Round 2 | 新概念、新链接、新问题 | Structure View | 新资料引入结构变化 |
| Round 3 | 重复概念、冲突、孤岛、检索下降 | Overview + Failure View | 多轮维护导致退化 |
| Repair | 修复日志、修复后指标 | Experiment Dashboard | 诊断修复能改善检索 |

---

## 6.3 实验指标与可视化映射

| 指标 | 数据来源 | 可视化位置 | 解释作用 |
|---|---|---|---|
| Citation Coverage | claim_index | Overview / Provenance | 说明主张是否有来源 |
| Unsupported Claim Rate | claim_index | Provenance | 找无来源结论 |
| Orphan Concept Rate | link_graph | Structure View | 找孤岛页面 |
| Duplicate Concept Rate | concept_index + alias_map | Structure View | 找重复概念和命名漂移 |
| Conflict Density | claim pair / NLI | Provenance / Structure | 找知识冲突 |
| Recall@3 | retrieval_tests | Overview / Failure | 衡量检索是否命中 |
| MRR | retrieval_tests | Overview / Failure | 衡量正确结果排名 |
| Repair Gain | before/after metrics | Experiment Dashboard | 衡量修复收益 |

---

## 6.4 实验案例如何在前端展示

### 案例 1：重复概念导致检索失败

实验现象：

- Round 3 后出现 Agentic_RAG.md 和 RAG_Agent.md。
- 查询“RAG Agent 是什么？”时只召回 RAG_Agent.md，但该页面内容薄弱。
- Agentic_RAG.md 中有更完整的 claim，但未被召回。

前端展示：

1. Overview 显示 Duplicate Rate 上升。
2. Structure View 中两节点用橙色虚线连接。
3. Failure View 显示 query 未召回 expected page。
4. Attribution 显示原因：缺少 alias 映射。
5. Repair 后 Recall@3 提升。

### 案例 2：概念孤岛导致检索失败

实验现象：

- Citation_Faithfulness.md 没有入链。
- 查询“RAG 引用忠实性如何评估？”未召回该页面。

前端展示：

1. Structure View 中 Citation_Faithfulness.md 被标红。
2. Inspector 显示入链数为 0。
3. Failure View 归因：expected page is orphan。
4. 修复建议：从 RAG_Evaluation.md 添加链接。

### 案例 3：无来源 claim 影响可信性

实验现象：

- GraphRAG.md 中出现“GraphRAG 总是优于普通 RAG”的 claim，但没有 source。

前端展示：

1. Provenance View 中该 claim 标红。
2. Inspector 显示 source_ids 为空。
3. 修复建议：补充来源或降级为未验证观点。

### 案例 4：修复后检索恢复

实验现象：

- 合并重复概念、添加 alias、修复链接后，Recall@3 从 0.61 提升到 0.74。

前端展示：

1. Experiment Dashboard 显示 Before/After 对比。
2. Overview 显示 Repair 节点指标回升。
3. 导出论文表格。

---

## 7. API 设计摘要

## 7.1 Sources

```http
GET /api/sources
POST /api/sources/upload
POST /api/sources/load-demo
GET /api/sources/{source_id}
```

## 7.2 Wiki

```http
GET /api/wiki/pages
GET /api/wiki/pages/{page_id}
GET /api/wiki/overview
PUT /api/wiki/pages/{page_id}
```

## 7.3 Pipeline

```http
POST /api/pipeline/build
GET /api/pipeline/logs
GET /api/pipeline/status
```

## 7.4 Diagnosis

```http
POST /api/diagnosis/run
GET /api/diagnosis/summary
GET /api/diagnosis/issues
GET /api/diagnosis/issues/{issue_id}
```

## 7.5 Retrieval

```http
POST /api/retrieval/search
POST /api/retrieval/evaluate
GET /api/retrieval/failures
```

## 7.6 Graph

```http
GET /api/graph/knowledge
GET /api/graph/provenance
GET /api/graph/failure
```

## 7.7 Experiment

```http
POST /api/experiments/run-round
POST /api/experiments/run-all
GET /api/experiments/metrics
GET /api/experiments/export
```

---

## 8. 前端页面详细需求

## 8.1 Sidebar

菜单：

1. Overview
2. Structure
3. Provenance
4. Failure
5. Experiment
6. Wiki Pages
7. Settings

## 8.2 Top Bar

元素：

1. 当前数据集
2. 当前 Round
3. Run Pipeline
4. Run Diagnosis
5. Run Evaluation
6. Export

## 8.3 Global State

```ts
type AppState = {
  datasetId: string;
  selectedRound: 'round_1' | 'round_2' | 'round_3' | 'repair';
  selectedPageId?: string;
  selectedClaimId?: string;
  selectedQueryId?: string;
  selectedIssueType?: string;
};
```

## 8.4 Visual Linking

联动规则：

1. 在 Overview 点击 Duplicate Rate → Structure View 过滤 duplicate issues。
2. 在 Structure 点击某个页面 → Inspector 显示页面详情。
3. 在 Failure 点击某个 query → Structure 高亮 expected pages 和 retrieved pages。
4. 在 Provenance 点击 claim → Wiki 页面中高亮该 claim。
5. 在 Experiment 点击某个轮次 → 全局 round 切换。

---

## 9. Vibe Coding 任务拆分

## 9.1 第一阶段：搭骨架

Prompt：

> 请实现 AgentKB-Diag 的 React + TypeScript 前端骨架，采用学术可视分析系统风格。页面包括 Overview、Structure、Failure、Experiment。整体布局为左侧深色导航栏、顶部控制栏、中间主视图、右侧 Inspector。要求清晰、克制、信息密度高，不要炫酷大屏风格。

验收：

- 页面可切换。
- 有统一布局。
- 有 mock 数据。
- 样式稳定。

## 9.2 第二阶段：Overview

Prompt：

> 请实现 Evolution Overview 页面，展示 Citation Coverage、Orphan Rate、Duplicate Rate、Conflict Density、Recall@3、MRR 的指标卡片和随 Round 变化的趋势图。Round 包括 Round 1、Round 2、Round 3、Repair。点击指标卡片可以设置 selectedIssueType。

验收：

- 指标卡片显示正常。
- 趋势图显示正常。
- 支持点击联动。

## 9.3 第三阶段：Structure

Prompt：

> 请使用 React Flow 实现 Knowledge Structure View。节点表示 Wiki 页面，边表示 wikilink。孤岛节点红色描边，重复概念橙色描边，冲突节点紫色标记。点击节点后右侧 Inspector 显示页面详情、入链数、出链数、相关 issue 和修复建议。

验收：

- 图能渲染。
- 节点可点击。
- issue 类型可视化清楚。
- Inspector 联动正常。

## 9.4 第四阶段：Failure

Prompt：

> 请实现 Retrieval Failure View，采用三栏布局：Query Panel、Retrieval Results、Failure Attribution。Query Panel 显示 query 和 expected pages；Retrieval Results 显示 top-k 页面、score、hit/miss；Failure Attribution 显示结构性失败原因和修复建议。

验收：

- 可以选择 query。
- 可以看到 top-k。
- 可以看到失败归因。
- 修复建议明确。

## 9.5 第五阶段：Provenance

Prompt：

> 请实现 Claim Provenance View，展示 Source → Claim → Wiki Page → Query 的溯源路径。Claim 按 supported、unsupported、conflicted 显示不同状态。点击 claim 显示其 source、所在页面和可能冲突。

验收：

- claim 列表可浏览。
- 溯源图可显示。
- unsupported claim 有明显标记。

## 9.6 第六阶段：Experiment

Prompt：

> 请实现 Experiment Dashboard，展示 Round 1、Round 2、Round 3、Repair 的实验指标表格，并支持导出 CSV。表格列包括 Citation Coverage、Orphan Rate、Duplicate Rate、Conflict Density、Recall@3、MRR。

验收：

- 指标表格显示正常。
- 支持导出。
- 可用于论文截图。

---

## 10. 后端实现任务拆分

## 10.1 数据加载

- 实现 source 上传。
- 实现 round 分类。
- 实现 demo 数据加载。

## 10.2 Wiki 构建

- 规则版先跑通。
- LLM 版后接入。
- 生成 sources、concepts、claims、links。

## 10.3 诊断计算

必须实现：

1. Citation Coverage
2. Unsupported Claim Rate
3. Orphan Concept Rate
4. Broken Link Count
5. Duplicate Concept Rate
6. Conflict Density

## 10.4 检索评估

必须实现：

1. Top-k retrieval
2. Recall@3
3. MRR
4. Failure cases
5. Failure attribution

## 10.5 实验快照

每轮保存：

1. build_snapshot.json
2. health_report.json
3. retrieval_eval.json
4. issues.json
5. graph.json

---

## 11. 论文实验设计

## 11.1 数据集

建议主题：

1. RAG
2. Agentic RAG
3. GraphRAG
4. KG-RAG
5. Citation Faithfulness
6. RAG Evaluation
7. LLM Wiki
8. Personal Knowledge Base

资料数量：

- Round 1：8-10 篇基础资料
- Round 2：8-10 篇扩展资料
- Round 3：8-10 篇相似概念 / 冲突资料

总量：25-30 篇。

## 11.2 测试问题

建议 30-50 个 query。

类型：

1. 概念解释
2. 方法对比
3. 方法追溯
4. 演化查询
5. 失败案例查询

## 11.3 对比方法

1. Raw-doc RAG
2. Static Wiki-RAG
3. Agent-maintained Wiki
4. AgentKB-Diag

## 11.4 核心实验表

| 状态 | Citation Coverage | Orphan Rate | Duplicate Rate | Conflict Density | Recall@3 | MRR |
|---|---:|---:|---:|---:|---:|---:|
| Round 1 |  |  |  |  |  |  |
| Round 2 |  |  |  |  |  |  |
| Round 3 |  |  |  |  |  |  |
| Round 3 + Repair |  |  |  |  |  |  |

## 11.5 要证明的结论

1. 多轮 Agent 维护会引入结构健康问题。
2. 结构健康问题会影响检索性能。
3. AgentKB-Diag 可以定位退化原因。
4. 根据诊断修复后，Recall@3 和 MRR 可以恢复或提升。

---

## 12. 论文中如何描述 Vis 创新

推荐表述：

> 本文设计了一种面向智能体维护知识库的多层次可视诊断界面。该界面围绕可检索性退化问题，将知识库演化过程、结构健康状态、主张—引用溯源关系和查询失败归因进行统一建模与可视化。与已有面向单次 RAG pipeline 或配置空间比较的可视诊断不同，本文关注 Wiki 型知识库在多轮智能体维护后的结构退化及其对检索性能的影响。

三层任务：

| 层次 | 视图 | 任务 |
|---|---|---|
| Macro | Evolution Overview | 发现退化趋势 |
| Meso | Knowledge Structure View | 定位结构异常 |
| Micro | Provenance / Failure View | 解释 claim 与 query 级失败 |

---

## 13. 验收标准

## 13.1 产品验收

- 能导入三轮资料。
- 能生成 Wiki 页面。
- 能生成 claim、citation、concept、link 数据。
- 能运行诊断。
- 能运行检索评估。
- 能显示三大核心视图。
- 能导出实验表格。

## 13.2 论文验收

- 有清晰问题定义。
- 有明确数据结构。
- 有可计算指标。
- 有多轮实验。
- 有修复前后对比。
- 有典型案例。
- 有系统截图。

## 13.3 工程验收

- 前端 `npm run build` 通过。
- 后端测试通过。
- API 返回稳定。
- Demo 数据一键运行。
- 导出文件可用于论文。

---

## 14. 开发优先级路线图

## Week 1 / Phase 1：系统可跑

1. 完成目录结构。
2. 完成 demo 数据。
3. 完成 Wiki 构建。
4. 完成诊断指标。
5. 完成检索评估。

## Week 2 / Phase 2：前端可视化

1. Overview。
2. Structure。
3. Failure。
4. Experiment。

## Week 3 / Phase 3：论文实验

1. 准备真实资料。
2. 跑三轮实验。
3. 做修复。
4. 导出表格。
5. 截图和案例。

## Phase 4：增强

1. Provenance View。
2. What-if Repair。
3. LLM Agent 接入。
4. 用户研究。

---

## 15. 最终建议

第一版只做三个核心闭环：

```text
演化总览：发现退化
知识结构图：定位异常
检索失败归因：解释失败
```

这三个闭环能支撑系统、实验和论文叙事。

不要把系统做成“个人知识库产品”。要把它做成“可检索性退化诊断仪”。

最终产品目标：

> 清晰、克制、信息密度高、能解释问题。

最终论文目标：

> 证明智能体维护知识库会出现可检索性退化，并证明 AgentKB-Diag 能发现、解释和修复这种退化。

