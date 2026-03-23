"""
单元测试 - tools.py
使用 pytest + unittest.mock 隔离外部依赖
"""

import os
import pytest
from unittest.mock import patch, MagicMock

import tools


@pytest.fixture(autouse=True)
def reset_retriever_cache():
    """每个测试前重置 retriever 缓存"""
    tools._retriever_cache = None
    yield
    tools._retriever_cache = None


# --- Req 1.1: search_knowledge 使用 @tool 装饰器且接受 query 参数 ---

def test_search_knowledge_is_langchain_tool():
    """search_knowledge 应该是 LangChain BaseTool 实例"""
    from langchain_core.tools import BaseTool
    assert isinstance(tools.search_knowledge, BaseTool)


def test_search_knowledge_accepts_query_param():
    """search_knowledge 应接受 query 字符串参数"""
    schema = tools.search_knowledge.args_schema.schema()
    assert "query" in schema["properties"]
    assert schema["properties"]["query"]["type"] == "string"


# --- Req 1.2: 工具描述包含"本地文档知识库" ---

def test_search_knowledge_description_contains_keyword():
    """工具描述应包含'本地文档知识库'"""
    assert "本地文档知识库" in tools.search_knowledge.description


# --- Req 3.2: CHROMA_PATH 默认值 ---

@patch.dict(os.environ, {}, clear=True)
@patch("tools.os.path.exists", return_value=True)
@patch("tools.OpenAIEmbeddings")
@patch("tools.Chroma")
def test_chroma_path_default(mock_chroma, mock_embeddings, mock_exists):
    """CHROMA_PATH 未设置时应使用默认路径 ../rag-agent/chroma_db"""
    mock_vs = MagicMock()
    mock_chroma.return_value = mock_vs

    tools._get_retriever()

    mock_exists.assert_called_with("../rag-agent/chroma_db")
    mock_chroma.assert_called_once()
    assert mock_chroma.call_args[1]["persist_directory"] == "../rag-agent/chroma_db"


# --- Req 3.4: OPENAI_EMBEDDING_MODEL 默认值 ---

@patch.dict(os.environ, {}, clear=True)
@patch("tools.os.path.exists", return_value=True)
@patch("tools.OpenAIEmbeddings")
@patch("tools.Chroma")
def test_embedding_model_default(mock_chroma, mock_embeddings, mock_exists):
    """OPENAI_EMBEDDING_MODEL 未设置时应使用默认值 text-embedding-3-small"""
    mock_vs = MagicMock()
    mock_chroma.return_value = mock_vs

    tools._get_retriever()

    mock_embeddings.assert_called_once()
    assert mock_embeddings.call_args[1]["model"] == "text-embedding-3-small"


# --- Req 6.1: ALL_TOOLS 包含三个工具 ---

def test_all_tools_contains_three_tools():
    """ALL_TOOLS 应包含恰好 3 个工具"""
    assert len(tools.ALL_TOOLS) == 3


def test_all_tools_contains_expected_tools():
    """ALL_TOOLS 应包含 get_current_time, calculate, search_knowledge"""
    tool_names = [t.name for t in tools.ALL_TOOLS]
    assert "get_current_time" in tool_names
    assert "calculate" in tool_names
    assert "search_knowledge" in tool_names


# --- Req 4.1: ChromaDB 路径不存在时返回入库脚本提示 ---

@patch("tools.os.path.exists", return_value=False)
def test_search_knowledge_db_not_found(mock_exists):
    """ChromaDB 路径不存在时应返回入库脚本提示"""
    result = tools.search_knowledge.invoke({"query": "测试查询"})
    assert "入库脚本" in result or "ingest" in result.lower()


# --- Req 4.2: Embedding API 失败时返回服务不可用 ---

@patch("tools.os.path.exists", return_value=True)
@patch("tools.OpenAIEmbeddings")
@patch("tools.Chroma")
def test_search_knowledge_api_failure(mock_chroma, mock_embeddings, mock_exists):
    """Embedding API 失败时应返回服务不可用信息"""
    mock_vs = MagicMock()
    mock_chroma.return_value = mock_vs

    # 模拟 retriever.invoke 抛出 OpenAI API 异常
    mock_retriever = MagicMock()
    mock_vs.as_retriever.return_value = mock_retriever

    # 使用动态创建的异常类，模块名包含 "openai"
    OpenAIError = type("OpenAIError", (Exception,), {"__module__": "openai.error"})
    api_error = OpenAIError("connection failed")
    mock_retriever.invoke.side_effect = api_error

    result = tools.search_knowledge.invoke({"query": "测试查询"})
    assert "不可用" in result or "暂时" in result


# --- Req 5.1, 5.2, 5.3: requirements.txt 包含所需依赖 ---

def test_requirements_contains_chromadb():
    """requirements.txt 应包含 chromadb"""
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    with open(req_path, "r") as f:
        content = f.read()
    assert "chromadb" in content


def test_requirements_contains_langchain_community():
    """requirements.txt 应包含 langchain-community"""
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    with open(req_path, "r") as f:
        content = f.read()
    assert "langchain-community" in content


def test_requirements_contains_langchain_text_splitters():
    """requirements.txt 应包含 langchain-text-splitters"""
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    with open(req_path, "r") as f:
        content = f.read()
    assert "langchain-text-splitters" in content
