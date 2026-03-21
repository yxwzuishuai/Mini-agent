# 🔍 RAG Agent Demo

用 ChromaDB + LangChain 实现的 RAG（检索增强生成）系统。
让 AI 能读取你的本地文档来回答问题。

## RAG 是什么？

普通 LLM 只能回答训练数据里有的内容。RAG 让 LLM 能访问你自己的文档：

```
你的文档 → 切片 → 转成向量 → 存入 ChromaDB
                                    ↓
用户提问 → 转成向量 → 检索相关内容 → 拼到 prompt 里 → LLM 回答
```

## 快速开始

```bash
cd rag-agent
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 API Key

# 第 1 步：文档入库（只需运行一次）
python ingest.py

# 第 2 步：开始问答
python query.py
```

## 试试这些问题

```
你: Python 有哪些数据结构？
你: Agent 的工作流程是什么？
你: FastAPI 和 Spring Boot 有什么区别？
你: RAG 的优势是什么？
```

## 添加你自己的文档

把 .txt 文件放到 `docs/` 目录下，重新运行 `python ingest.py` 即可。

## 文件结构

```
rag-agent/
├── docs/                  # 文档目录（放你的 .txt 文件）
│   ├── python_basics.txt
│   ├── ai_agent.txt
│   └── fastapi_guide.txt
├── chroma_db/             # ChromaDB 数据（自动生成）
├── ingest.py              # 文档入库脚本
├── query.py               # RAG 问答脚本
├── .env.example           # 环境变量模板
├── requirements.txt       # 依赖
└── README.md              # 本文件
```

## 核心概念

| 概念 | 说明 | 类比 |
|------|------|------|
| Embedding | 把文本转成数字向量 | 给文本算一个"指纹" |
| 向量数据库 | 存储和检索向量 | 类似全文搜索引擎 |
| 切片 | 把长文档切成小块 | 把书拆成段落 |
| 检索 | 找到和问题最相关的文本块 | 在书里找相关段落 |
| RAG | 检索 + 生成 | 先查资料再回答 |

## 四个项目的演进

```
mini-agent（手写 Agent Loop）
  → langchain-agent（框架简化）
    → fastapi-agent（HTTP API）
      → rag-agent（知识库问答）← 你在这里
```
