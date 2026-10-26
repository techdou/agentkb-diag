# AgentKB-Diag

> 面向 LLM Agent 维护式 Wiki 知识库的可检索性退化诊断系统

**AgentKB-Diag** 是一套面向"由 LLM Agent 持续维护的 Wiki 型知识库"的可视分析与诊断系统。它回答一个核心问题：

> **当知识库随着多轮 Agent 更新不断演化时，是否会出现"内容存在但检索不到"的结构性退化？如何发现、归因并修复？**

## ✨ 主要功能

- **7 项健康指标**：引用覆盖率、无支持声明率、孤儿率、重复率、冲突密度、Recall@3、MRR
- **5 类问题自动检测**：孤儿（orphan）、重复（duplicate）、冲突（conflict）、断链（broken link）、缺引用（missing citation）
- **统计异常修复引擎**：基于 Otsu 双模态阈值分割和间距比检验，自动识别"被污染"的声明
- **4 种基线对比**：RawDocRAG、StaticWikiRAG、AgentWikiRAG、AgentKBDiag
- **可视分析前端**：React + Recharts，支持健康度趋势、问题分布、知识图谱、检索回放

## 📁 项目结构

```
agentkb-diag/
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── routers/        # API 路由（diagnosis, retrieval, graph, ...）
│   │   ├── services/       # 核心业务（baselines, repair, diagnosis, ...）
│   │   └── core/config.py  # 配置加载（pydantic-settings）
│   ├── scripts/            # 数据采集、OKF 导入导出
│   ├── tests/              # 单元测试
│   ├── requirements.txt
│   └── .env.example        # 环境变量模板（**必读**）
│
├── frontend/               # React + Vite 前端
│   ├── src/                # 组件、页面、API 客户端
│   ├── package.json
│   ├── vite.config.ts
│   └── .env.example        # 前端环境变量模板
│
├── okf/                    # 系统自带的知识库（OKF v0.1 格式）
│   ├── concepts/           # 20 个概念页
│   ├── sources/            # 30 篇原始论文
│   └── syntheses/          # 3 篇综合分析
│
├── workspace/              # Agent 维护的 Wiki 知识库快照
│   ├── wiki/               # 当前 Wiki
│   ├── rounds/             # 各轮快照（round_1, round_2, round_3）
│   └── index/              # 检索索引
│
├── data/
│   ├── raw/                # 原始论文 PDF（不提交）
│   └── converted/          # 转换后的 Markdown（提交）
│
└── .gitignore              # 忽略 .env、报告、node_modules 等
```

## 🚀 快速开始

### 1. 克隆与初始化

```bash
git clone <your-repo-url> agentkb-diag
cd agentkb-diag
```

### 2. 配置环境变量（必读）

本项目**所有密钥、API 密钥**都通过环境变量管理，**任何 `.env` 文件都不会被 Git 追踪**。

#### 后端

```bash
cd backend
cp .env.example .env
# 编辑 .env，填入你的 LLM API 密钥
```

最小配置示例（`backend/.env`）：
```ini
# LLM 配置（必填）
LLM_PROVIDER=openai
LLM_API_KEY=sk-your-real-api-key-here
LLM_MODEL=gpt-4o-mini

# 可选：Semantic Scholar API（用于 fetch_papers）
SEMANTIC_SCHOLAR_API_KEY=
```

#### 前端

```bash
cd ../frontend
cp .env.example .env
# 默认值即可（http://localhost:8000）
```

### 3. 安装依赖

```bash
# 后端
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 前端
cd ../frontend
npm install
```

### 4. 启动服务

```bash
# 终端 1：后端（默认 http://localhost:8000）
cd backend
uvicorn app.main:app --reload --port 8000

# 终端 2：前端（默认 http://localhost:5173）
cd frontend
npm run dev
```

访问 http://localhost:5173 即可使用。

### 5. （可选）采集真实论文数据

```bash
cd backend
python -m scripts.fetch_papers --round 1 --api arxiv --max-per-query 5
python -m scripts.fetch_papers --round 2 --api semantic_scholar
python -m scripts.fetch_papers --round 3 --max-per-query 3
```

> ⚠️ `data/raw/*/source_*.pdf` 不会被 Git 追踪，克隆后本地下载。

## 🧪 运行实验

```bash
cd backend
python -m scripts.run_experiment
# 报告输出到 workspace/reports/
```

## 🛠 关键技术栈

| 层 | 技术 |
|----|------|
| 后端 | FastAPI、pydantic-settings、scikit-learn、httpx |
| 前端 | React 18、Vite、TypeScript、Recharts、React Router |
| 知识表示 | OKF v0.1（Open Knowledge Format，markdown + YAML frontmatter） |
| 检索 | TF-IDF 检索 + Agent 维护的 Wiki 索引 |
| 异常检测 | Otsu 双模态阈值分割、间距比检验 |

## 📊 评估方法

项目内置 4 种检索基线方法：

| 方法 | 说明 | 是否会退化 |
|------|------|-----------|
| `RawDocRAG` | 直接检索原始 PDF 转换后的文档 | 否（不更新） |
| `StaticWikiRAG` | 一次性构建、永远不更新的 Wiki | 否（不更新） |
| `AgentWikiRAG` | Agent 多轮更新维护的 Wiki | ✅ 是 |
| `AgentKBDiag` | Agent Wiki + 诊断-修复闭环 | ✅ 不会（自动修复） |

评估指标：Recall@k、MRR。

## 📜 许可证

本项目仅供学术研究使用。

## 🙏 致谢

- OKF v0.1 知识交换格式（2026-06）
- arXiv、Semantic Scholar 提供论文元数据
- 本项目为高级人工智能专业实践研究报告的原型实现
