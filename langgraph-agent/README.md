# 🤖 LangGraph 多 Agent 协作 Demo

用 LangGraph 实现 3 个 Agent 协作完成内容创作。

## 什么是 LangGraph？

LangGraph 是 LangChain 团队开发的多 Agent 编排框架。
核心思想：用**图（Graph）**来定义 Agent 之间的协作流程。

```
类比 Java：
- Graph ≈ Spring State Machine（状态机）
- Node ≈ 每个处理步骤（一个方法）
- Edge ≈ 步骤之间的跳转规则
- State ≈ Context 对象（共享数据）
```

## 协作流程

```
用户输入主题
    ↓
🔍 研究员 Agent（搜索资料）
    ↓
✍️  写手 Agent（撰写文章）
    ↓
📋 审核员 Agent（审核质量）
    ↓
  PASS → 📝 输出最终文章
  REVISE → 🔄 回到写手修改（最多 2 次）
```

## 快速开始

```bash
cd langgraph-agent
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 API Key

python main.py
```

## 试试这些主题

```
请输入主题: AI Agent
请输入主题: Python 学习路线
请输入主题: RAG 技术
```

## 文件结构

```
langgraph-agent/
├── main.py            # 入口文件
├── graph.py           # LangGraph 流程编排（核心）
├── agents.py          # Agent 定义（prompt + LLM 配置）
├── tools.py           # 工具定义
├── .env.example       # 环境变量模板
├── requirements.txt   # 依赖
└── README.md          # 本文件
```

## 核心概念

| LangGraph 概念 | Java 类比 | 说明 |
|----------------|-----------|------|
| StateGraph | State Machine | 状态机，定义整个流程 |
| State | Context | 所有节点共享的数据 |
| Node | Handler/Method | 处理节点，执行具体逻辑 |
| Edge | Transition | 固定的跳转规则 |
| Conditional Edge | 条件分支 | 根据结果动态决定下一步 |
| compile() | build() | 编译图，生成可执行的工作流 |

## 五个项目的演进

```
mini-agent（手写 Agent Loop）
  → langchain-agent（框架简化）
    → fastapi-agent（HTTP API）
      → rag-agent（知识库问答）
        → langgraph-agent（多 Agent 协作）← 你在这里
```
