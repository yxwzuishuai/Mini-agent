"""
工具定义 - 给 Agent 使用的工具

这里用模拟工具演示，实际项目中可以替换成真实 API
"""

from langchain_core.tools import tool


@tool
def search_web(query: str) -> str:
    """搜索网络获取信息（模拟）"""
    # 模拟搜索结果，实际项目中可以接入 Google/Bing API
    fake_results = {
        "python": "Python 是一种解释型、面向对象的高级编程语言。广泛用于 Web 开发、数据分析、AI 等领域。",
        "ai agent": "AI Agent 是能自主决策和执行任务的智能体。核心组件包括：LLM 大脑、工具调用、记忆系统、规划能力。",
        "langgraph": "LangGraph 是 LangChain 团队开发的多 Agent 编排框架，基于图（Graph）结构定义 Agent 之间的协作流程。",
        "rag": "RAG（检索增强生成）通过检索外部知识库来增强 LLM 的回答能力，解决了 LLM 知识过时和幻觉问题。",
    }
    # 简单的关键词匹配
    for key, value in fake_results.items():
        if key in query.lower():
            return f"搜索结果：{value}"
    return f"搜索结果：关于「{query}」的信息 - 这是一个重要的技术话题，涉及多个方面的知识。"


@tool
def count_words(text: str) -> str:
    """统计文本字数"""
    count = len(text)
    return f"文本共 {count} 个字符"
