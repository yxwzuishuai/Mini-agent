"""
LangChain Agent Demo - 入口文件

对比 mini-agent：
- mini-agent：手写 Agent Loop（for 循环 + 判断 tool_calls + 执行工具）
- LangChain：create_react_agent 一行搞定，内部帮你实现了 Agent Loop

用法：
1. cp .env.example .env  # 填入 API Key
2. pip install -r requirements.txt
3. python main.py
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from tools import ALL_TOOLS


def main():
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("sk-your"):
        print("❌ 请先在 .env 文件中设置 OPENAI_API_KEY")
        return

    # 创建 LLM（对比 mini-agent 的 OpenAI 客户端）
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm_kwargs = {"model": model, "api_key": api_key}
    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        llm_kwargs["base_url"] = base_url

    llm = ChatOpenAI(**llm_kwargs)

    # 创建 Agent（对比 mini-agent 的 MiniAgent 类 + Agent Loop）
    # 这一行等价于你手写的整个 agent.py
    agent = create_react_agent(llm, ALL_TOOLS)

    print("=" * 50)
    print("🤖 LangChain Agent 已启动")
    print(f"   模型: {model}")
    print("   输入 'quit' 退出")
    print("=" * 50)
    print()

    while True:
        try:
            user_input = input("你: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 再见！")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("👋 再见！")
            break

        # 调用 Agent（对比 mini-agent 的 agent.chat()）
        result = agent.invoke({"messages": [("user", user_input)]})

        # 取最后一条 AI 回复
        reply = result["messages"][-1].content
        print(f"\nAgent: {reply}\n")


if __name__ == "__main__":
    main()
