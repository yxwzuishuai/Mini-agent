"""
工具定义 - 和 langchain-agent 的一样
"""

import math
from datetime import datetime
from langchain_core.tools import tool


@tool
def get_current_time() -> str:
    """获取当前的日期和时间"""
    return datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")


@tool
def calculate(expression: str) -> str:
    """
    执行数学计算，支持加减乘除、幂运算、开方等。
    参数 expression: 要计算的数学表达式，例如 '2 + 3 * 4' 或 'sqrt(16)'
    """
    safe_dict = {
        "sqrt": math.sqrt, "pow": math.pow, "abs": abs,
        "round": round, "sin": math.sin, "cos": math.cos,
        "pi": math.pi, "e": math.e, "log": math.log,
    }
    try:
        return str(eval(expression, {"__builtins__": {}}, safe_dict))
    except Exception as e:
        return f"计算错误: {e}"


@tool
def search_knowledge(query: str) -> str:
    """
    从知识库中搜索信息。
    参数 query: 搜索关键词
    """
    kb = {
        "python": "Python 是一种高级编程语言，以简洁易读著称。",
        "agent": "AI Agent 是能够感知环境、做出决策并采取行动的 AI 系统。",
        "langchain": "LangChain 是一个用于开发 LLM 应用的框架。",
        "fastapi": "FastAPI 是一个高性能的 Python Web 框架，基于 Starlette 和 Pydantic。",
    }
    results = [v for k, v in kb.items() if k in query.lower()]
    return "\n".join(results) if results else f"未找到与 '{query}' 相关的信息"


ALL_TOOLS = [get_current_time, calculate, search_knowledge]
