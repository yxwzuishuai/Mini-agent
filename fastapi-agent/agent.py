"""
Agent 实例 - 创建一个全局的 LangChain Agent

对比之前的项目：
- mini-agent：手写 Agent Loop
- langchain-agent：用 create_react_agent，在终端交互
- fastapi-agent：同样的 Agent，但通过 HTTP API 对外提供服务
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from tools import ALL_TOOLS

load_dotenv()


def create_agent():
    """创建并返回 Agent 实例"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("sk-your"):
        raise ValueError("请在 .env 文件中设置 OPENAI_API_KEY")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm_kwargs = {"model": model, "api_key": api_key}
    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        llm_kwargs["base_url"] = base_url

    llm = ChatOpenAI(**llm_kwargs)
    return create_react_agent(llm, ALL_TOOLS)


# 全局 Agent 实例，应用启动时创建一次，所有请求共用
agent = create_agent()
