# 🤖 Mini Agent - 最小化 Python Agent 项目

一个用 **纯 Python + OpenAI SDK** 实现的最小化 AI Agent，帮助你理解 Agent 的核心原理。

## 什么是 Agent？

Agent（智能体）的核心就是一个循环：

```
用户输入
  → LLM 思考（要不要用工具？）
    → 需要工具 → 调用工具 → 拿到结果 → 回到 LLM 继续思考
    → 不需要工具 → 直接回复用户
```

这个循环叫做 **Agent Loop**（也叫 ReAct Loop）。本项目用最少的代码实现了这个循环。

## 项目结构

```
mini-agent/
├── README.md           # 你正在看的这个文件
├── requirements.txt    # Python 依赖
├── .env.example        # 环境变量模板
├── tools.py            # 工具定义与实现
├── agent.py            # Agent 核心循环
└── main.py             # 入口文件
```

## 各文件详解

### `tools.py` - 工具模块

Agent 的 "能力" 来自工具。每个工具有两部分：

1. **JSON Schema 描述**：发给 LLM，告诉它工具的名称、用途、参数格式
2. **执行函数**：LLM 决定调用后，由我们的代码实际执行

本项目包含 3 个示例工具：

| 工具名 | 功能 | 说明 |
|--------|------|------|
| `get_current_time` | 获取当前时间 | 无参数的简单工具 |
| `calculate` | 数学计算 | 支持四则运算、开方、三角函数等 |
| `search_knowledge` | 知识库搜索 | 模拟搜索，实际项目可接入向量数据库 |

### `agent.py` - Agent 核心

实现了 `MiniAgent` 类，核心是 `chat()` 方法中的 Agent Loop：

```python
for i in range(max_iterations):
    response = client.chat.completions.create(
        model=model,
        messages=messages,      # 对话历史
        tools=TOOL_DEFINITIONS, # 可用工具
        tool_choice="auto",     # LLM 自己决定是否调用工具
    )
    
    if not message.tool_calls:
        return message.content  # 直接回复，循环结束
    
    # 有工具调用 → 执行工具 → 结果放回 messages → 继续循环
```

### `main.py` - 入口文件

负责加载配置、创建 Agent 实例、启动交互式对话。

## 快速开始

### 1. 安装依赖

```bash
cd mini-agent
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，填入你的 API Key
```

支持以下 LLM 服务（任选其一）：

| 服务 | 配置 |
|------|------|
| OpenAI | 只需设置 `OPENAI_API_KEY` |
| DeepSeek | 设置 `OPENAI_BASE_URL=https://api.deepseek.com/v1` 和 `OPENAI_MODEL=deepseek-chat` |
| 通义千问 | 设置 `OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1` 和 `OPENAI_MODEL=qwen-plus` |

### 3. 运行

```bash
python main.py
```

### 4. 试试这些对话

```
你: 现在几点了？
Agent: (调用 get_current_time 工具) 现在是 2025年01月15日 14:30:22

你: 计算一下 sqrt(144) + 3^2
Agent: (调用 calculate 工具) sqrt(144) + 3² = 12 + 9 = 21

你: 什么是 AI Agent？
Agent: (调用 search_knowledge 工具) AI Agent 是能够感知环境、做出决策并采取行动的 AI 系统...

你: 帮我算一下，如果我每月存 3000 元，年利率 3%，5 年后有多少钱？
Agent: (可能多次调用 calculate) 让我帮你计算...
```

## 核心概念图解

```
┌─────────────────────────────────────────────┐
│                 Agent Loop                   │
│                                             │
│  用户输入 ──→ [LLM 思考] ──→ 直接回复？──→ 返回给用户
│                  │                           │
│                  ↓ 需要工具                    │
│            [调用工具函数]                      │
│                  │                           │
│                  ↓                           │
│            [工具返回结果]                      │
│                  │                           │
│                  ↓                           │
│            [结果放入消息历史] ──→ 回到 LLM 思考  │
│                                             │
└─────────────────────────────────────────────┘
```

## 关键概念

### Function Calling（函数调用）

这是 Agent 的核心机制。流程是：

1. 我们告诉 LLM："你有这些工具可以用"（通过 JSON Schema）
2. LLM 分析用户需求，决定是否需要工具
3. 如果需要，LLM 返回：调用哪个工具 + 传什么参数
4. 我们的代码执行工具，把结果返回给 LLM
5. LLM 根据结果生成最终回复

**LLM 不会直接执行工具**，它只是"说"要调用什么，实际执行由我们的代码完成。

### Messages（消息历史）

Agent 的 "记忆" 就是一个消息列表，包含 4 种角色：

| 角色 | 说明 |
|------|------|
| `system` | 系统提示词，定义 Agent 的行为 |
| `user` | 用户的输入 |
| `assistant` | LLM 的回复（可能包含工具调用） |
| `tool` | 工具执行的结果 |

## 下一步学习

掌握了这个最小 Agent 后，你可以：

1. **添加更多工具**：文件读写、网络请求、数据库查询等
2. **添加记忆持久化**：把对话历史存到文件或数据库
3. **添加流式输出**：使用 `stream=True` 实现打字机效果
4. **学习 Agent 框架**：LangChain、LangGraph、CrewAI
5. **实现多 Agent 协作**：多个 Agent 分工合作完成复杂任务

## 常见问题

**Q: 支持国产大模型吗？**
A: 支持任何兼容 OpenAI 接口的服务。在 `.env` 中设置 `OPENAI_BASE_URL` 和 `OPENAI_MODEL` 即可。

**Q: 为什么用 `eval` 做计算？**
A: 这里用了受限的 `eval`（禁用了 `__builtins__`），只允许数学函数。生产环境建议用 `sympy` 等专业库。

**Q: 如何添加新工具？**
A: 三步走：
1. 在 `tools.py` 中添加 JSON Schema 定义到 `TOOL_DEFINITIONS`
2. 编写对应的执行函数
3. 在 `TOOL_REGISTRY` 中注册函数名和函数的映射
