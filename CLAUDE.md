# AgentKB-Diag

面向智能体维护知识库的可检索性退化诊断系统（可视分析 + 学术实验）。

## 项目定位

> 由 LLM Agent 持续维护的 Wiki 型知识库是否会在多轮更新后发生可检索性退化？如果会，如何发现、归因和修复？

- **不是** RAG 问答 SOTA 追逐
- **不是** 通用个人知识库产品
- **是** 知识库结构健康诊断仪 + 可视分析系统

## 核心概念

- **KB**: LLM Agent 自动维护的 Wiki 型知识库
- **AgentKB**: Agent 维护的知识库
- **Diag**: 诊断
- **Claim**: 知识主张，可被证据支持或反驳的结论性陈述
- **Citation**: Claim → Source 的引用关系
- **Concept**: 概念页面
- **Orphan Concept**: 无入链/出链的概念孤岛
- **Duplicate Concept**: 多个页面描述同一概念但未合并
- **Retrievability Degradation**: 知识存在但因结构问题无法被稳定召回
- **OKF**: Open Knowledge Format v0.1，知识库的权威可交换格式（Google Cloud 2026-06-13 发布的开放规范）。见 `okf/README.md`

## 目录结构

```
agentkb-diag/
  data/
    raw/          # 原始资料（分 round）
    converted/    # 转换后文本（分 round）
  workspace/
    wiki/         # Markdown Wiki 页面（OKF 格式，与 okf/ 同步）
    index/        # JSON 索引（从 okf/ 派生：claim, concept, link, alias 等）
    rounds/       # 每轮快照 + 诊断 + 检索评估
    reports/      # 报告导出
  okf/            # OKF v0.1 知识 bundle（权威源）
  backend/        # Python/FastAPI 后端
  frontend/       # React + TypeScript + Vite 前端
```

## OKF 知识格式

知识库遵循 [OKF v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)：
每个概念一个 markdown 文件 + YAML frontmatter（必需 `type` 字段），概念间用标准
markdown 链接 `[text](/concepts/X.md)` 关联，正文底部 `# Citations` 编号列出来源。

- **权威源**: `okf/` bundle（producer/consumer 独立，可被人或 agent 编辑）
- **派生产物**: `workspace/index/*.json`（诊断/检索 pipeline 读取，性能 + 解耦）
- **同步工具**:
  - `python backend/scripts/okf_export.py` — wiki/ + index → okf/（producer）
  - `python backend/scripts/okf_import.py` — okf/ → index（consumer）
  - `python backend/scripts/okf_check.py` — OKF 合规校验

## 架构

```
Raw Sources → Document Conversion → Agent Pipeline → Wiki KB → Diagnosis → Retrieval Eval → Frontend
```

### 后端模块

| 模块 | 职责 |
|---|---|
| Ingest Service | 资料导入与 round 分类 |
| Agent Pipeline | 调用 Agent 生成 Wiki 内容 |
| Wiki Service | Wiki 页面 CRUD |
| Diagnosis Service | 健康指标计算与问题诊断 |
| Retrieval Service | 检索评估与失败归因 |
| Experiment Service | 实验轮次管理与导出 |
| Graph Service | 前端图数据服务 |

### 前端视图

| 视图 | 回答的问题 |
|---|---|
| Evolution Overview | 多轮维护是否导致退化？ |
| Knowledge Structure | 哪里乱了？哪些孤岛/重复/冲突？ |
| Claim Provenance | 关键结论有没有来源？是否可信？ |
| Retrieval Failure | 为什么没召回？归因是什么？ |
| Experiment Dashboard | 修复前后指标是否改善？ |

## 开发命令

```bash
# 后端（在项目根目录执行）
pip install -r backend/requirements.txt
cd backend && uvicorn app.main:app --reload

# 前端
cd frontend && npm install
npm run dev
npm run build
```

## 核心指标

| 指标 | 说明 |
|---|---|
| Citation Coverage | 有来源的 claim 占比 |
| Unsupported Claim Rate | 无来源 claim 占比 |
| Orphan Concept Rate | 孤岛页面占比 |
| Duplicate Concept Rate | 重复概念占比 |
| Conflict Density | 冲突 claim 数量 / 总 claim |
| Recall@3 | Top-3 命中率 |
| MRR | 正确结果平均倒数排名 |

## 设计原则

1. Plain files first：Markdown + JSON，便于调试复现
2. Source traceable：每条 claim 可回溯到原始资料
3. Link explicit：概念间通过显式 wikilink 表达
4. Round aware：数据带轮次元数据
5. Diagnosis friendly：数据结构天然支持指标计算
6. Experiment reproducible：每轮输入/输出/指标/日志可保存

## 实验设计

- 数据集：25-30 篇论文/资料，分 3 轮导入
- 测试问题：30-50 个 query
- 对比方法：Raw-doc RAG vs Static Wiki-RAG vs Agent Wiki vs AgentKB-Diag
- 核心结论：多轮维护 → 结构退化 → 检索退化 → 诊断修复 → 检索恢复

## 风格约束

清晰、克制、信息密度高、能解释问题。
不要炫酷大屏、花哨渐变、复杂 3D、无意义动画。
