"""
工具定义 - 和 langchain-agent 的一样
"""

import math
import os
from datetime import datetime
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


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


_retriever_cache = None


def _get_retriever():
    """
    初始化并返回 ChromaDB Retriever（带模块级缓存）。

    Returns:
        Chroma retriever 实例
    Raises:
        FileNotFoundError: ChromaDB 路径不存在
        Exception: Embedding 或 ChromaDB 初始化失败
    """
    global _retriever_cache
    if _retriever_cache is not None:
        return _retriever_cache

    chroma_path = os.environ.get("CHROMA_PATH", "../rag-agent/chroma_db")
    embedding_model = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    if not os.path.exists(chroma_path):
        raise FileNotFoundError(f"ChromaDB 路径不存在: {chroma_path}")

    embedding_kwargs = {
        "model": embedding_model,
        "api_key": os.environ.get("OPENAI_API_KEY"),
    }
    base_url = os.environ.get("OPENAI_BASE_URL")
    if base_url:
        embedding_kwargs["base_url"] = base_url

    embeddings = OpenAIEmbeddings(**embedding_kwargs)
    vectorstore = Chroma(persist_directory=chroma_path, embedding_function=embeddings)
    _retriever_cache = vectorstore.as_retriever(search_kwargs={"k": 3})
    return _retriever_cache


@tool
def search_knowledge(query: str) -> str:
    """
    从本地文档知识库中检索信息，适用于需要查找技术文档、教程、指南等知识性问题。
    参数 query: 用户的查询问题
    """
    try:
        retriever = _get_retriever()
        docs = retriever.invoke(query)
        if not docs:
            return f"未找到与 '{query}' 相关的内容"
        return "\n\n---\n\n".join([doc.page_content for doc in docs])
    except FileNotFoundError:
        return "知识库未初始化，请先运行文档入库脚本（python ingest.py）"
    except Exception as e:
        if "openai" in str(type(e).__module__).lower() or "api" in str(e).lower():
            return "知识库检索服务暂时不可用，请稍后再试"
        return f"知识库检索出错: {e}"



ALL_TOOLS = [get_current_time, calculate, search_knowledge]
