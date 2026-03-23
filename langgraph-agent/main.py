"""
LangGraph 多 Agent 协作 Demo

场景：内容创作团队
- 研究员 Agent：搜索收集资料
- 写手 Agent：根据资料写文章
- 审核员 Agent：审核质量，不合格打回重写

运行方式：
    python main.py
"""

import os
from dotenv import load_dotenv
from graph import build_graph

load_dotenv()


def main():
    # 检查 API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("sk-your"):
        print("❌ 请先在 .env 文件中设置 OPENAI_API_KEY")
        return

    # 构建工作流图
    print("🏗️  构建多 Agent 工作流...")
    workflow = build_graph()

    print("=" * 50)
    print("🤖 多 Agent 协作系统已启动")
    print("   输入一个主题，3 个 Agent 会协作完成文章")
    print("   输入 'quit' 退出")
    print("=" * 50)
    print()

    while True:
        try:
            topic = input("请输入主题: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 再见！")
            break

        if not topic:
            continue
        if topic.lower() == "quit":
            print("👋 再见！")
            break

        print(f"\n🚀 开始处理主题：{topic}")
        print("-" * 50)

        # 运行工作流（传入初始 state）
        result = workflow.invoke({
            "topic": topic,
            "research": "",
            "draft": "",
            "review": "",
            "revision_count": 0,
            "final_result": "",
        })

        # 输出最终结果
        print(result["final_result"])
        print()


if __name__ == "__main__":
    main()
