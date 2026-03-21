# 🦜 LangChain Agent Demo

用 LangChain 实现的 Agent，功能和 mini-agent 完全一样，对比看看框架帮你省了多少代码。

## mini-agent vs LangChain 对比

| 部分 | mini-agent（手写） | LangChain（框架） |
|------|-------------------|-------------------|
| 工具定义 | 手写 JSON Schema + 函数 + 注册表 | `@tool` 装饰器，自动生成 Schema |
| Agent Loop | 手写 for 循环 + 判断 tool_calls | `create_react_agent()` 一行搞定 |
| 消息管理 | 手动维护 messages 列表 | 框架自动管理 |
| 调用方式 | `agent.chat("你好")` | `agent.invoke({"messages": [...]})` |

## 快速开始

```bash
cd langchain-agent
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 API Key
python main.py
```

## 文件结构

```
langchain-agent/
├── .env.example      # 环境变量模板
├── requirements.txt  # 依赖
├── tools.py          # 工具定义（用 @tool 装饰器）
├── main.py           # 入口文件（创建 Agent + 对话循环）
└── README.md         # 本文件
```

## 核心代码就这几行

```python
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_react_agent(llm, tools)
result = agent.invoke({"messages": [("user", "现在几点了？")]})
```

你在 mini-agent 里手写了 100 多行的 Agent Loop，LangChain 3 行就搞定了。
但因为你理解了底层原理，用框架时就不会觉得是黑盒。
