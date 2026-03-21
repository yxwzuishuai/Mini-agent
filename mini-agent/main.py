"""
入口文件 - 启动 Agent 的交互式对话

使用方法:
1. 复制 .env.example 为 .env，填入你的 API Key
2. pip install -r requirements.txt
3. python main.py
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from agent import MiniAgent


def main():
    # 加载 .env 文件中的环境变量
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("sk-your"):
        print("❌ 请先在 .env 文件中设置你的 OPENAI_API_KEY")
        print("   复制 .env.example 为 .env，然后填入你的 Key")
        return

    # 创建 OpenAI 客户端（支持自定义 base_url，兼容 DeepSeek 等服务）
    client_kwargs = {"api_key": api_key}
    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        client_kwargs["base_url"] = base_url

    client = OpenAI(**client_kwargs)

    # 读取模型名称，默认 gpt-4o-mini
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # 创建 Agent 实例
    agent = MiniAgent(client=client, model=model)

    print("=" * 50)
    print("🤖 Mini Agent 已启动")
    print(f"   模型: {model}")
    print("   输入 'quit' 退出，输入 'reset' 重置对话")
    print("=" * 50)
    print()

    # 交互式对话循环
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
        if user_input.lower() == "reset":
            agent.reset()
            continue

        # 调用 Agent 处理用户输入
        reply = agent.chat(user_input)
        print(f"\nAgent: {reply}\n")


if __name__ == "__main__":
    main()
