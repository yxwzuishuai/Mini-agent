"""
工具模块 - 定义 Agent 可以调用的工具

每个工具包含两部分：
1. 工具的 JSON Schema 描述（告诉 LLM 这个工具是什么、参数是什么）
2. 工具的实际执行函数（LLM 决定调用后，由我们的代码执行）
"""

import json
import math
from datetime import datetime


# ============================================================
# 第一部分：工具的 JSON Schema 定义
# 这些定义会发送给 LLM，让它知道有哪些工具可用
# ============================================================

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间",
            "parameters": {
                "type": "object",
                "properties": {},  # 这个工具不需要参数
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学计算，支持加减乘除、幂运算、开方等",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式，例如: '2 + 3 * 4' 或 'sqrt(16)'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "从知识库中搜索信息（模拟）",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词",
                    }
                },
                "required": ["query"],
            },
        },
    },
]


# ============================================================
# 第二部分：工具的实际执行函数
# ============================================================

def get_current_time() -> str:
    """获取当前时间"""
    now = datetime.now()
    return now.strftime("%Y年%m月%d日 %H:%M:%S")


def calculate(expression: str) -> str:
    """
    安全地计算数学表达式
    使用 math 模块提供的函数，避免使用 eval 的安全风险
    """
    # 允许使用的数学函数
    safe_dict = {
        "sqrt": math.sqrt,
        "pow": math.pow,
        "abs": abs,
        "round": round,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "pi": math.pi,
        "e": math.e,
        "log": math.log,
        "log10": math.log10,
    }
    try:
        # 在受限环境中执行计算
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"


def search_knowledge(query: str) -> str:
    """
    模拟知识库搜索
    实际项目中，这里可以接入向量数据库、搜索引擎等
    """
    # 模拟的知识库
    knowledge_base = {
        "python": "Python 是一种高级编程语言，以简洁易读著称。由 Guido van Rossum 于 1991 年创建。",
        "agent": "AI Agent（智能体）是能够感知环境、做出决策并采取行动的 AI 系统。核心是 LLM + 工具调用的循环。",
        "langchain": "LangChain 是一个用于开发 LLM 应用的框架，提供了链式调用、记忆、工具等抽象。",
        "openai": "OpenAI 是一家 AI 研究公司，开发了 GPT 系列模型。其 API 支持 Function Calling 功能。",
    }

    # 简单的关键词匹配搜索
    results = []
    for key, value in knowledge_base.items():
        if key in query.lower() or query.lower() in key:
            results.append(value)

    if results:
        return "\n".join(results)
    return f"未找到与 '{query}' 相关的信息"


# ============================================================
# 工具注册表：将工具名称映射到执行函数
# Agent 收到 LLM 的工具调用指令后，通过这个字典找到对应的函数执行
# ============================================================

TOOL_REGISTRY = {
    "get_current_time": get_current_time,
    "calculate": calculate,
    "search_knowledge": search_knowledge,
}


def execute_tool(tool_name: str, arguments: dict) -> str:
    """
    执行指定的工具
    
    参数:
        tool_name: 工具名称
        arguments: 工具参数（字典）
    返回:
        工具执行结果（字符串）
    """
    if tool_name not in TOOL_REGISTRY:
        return f"错误: 未知工具 '{tool_name}'"

    func = TOOL_REGISTRY[tool_name]
    try:
        result = func(**arguments)
        return result
    except Exception as e:
        return f"工具执行错误: {e}"
