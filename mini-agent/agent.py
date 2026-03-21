"""
Agent 核心模块 - 实现 Agent Loop（智能体循环）

Agent 的核心原理非常简单：
1. 把用户消息 + 工具定义发给 LLM
2. LLM 决定是直接回复，还是调用工具
3. 如果调用工具 → 执行工具 → 把结果返回给 LLM → 回到第 2 步
4. 如果直接回复 → 返回给用户

这个循环就是所谓的 "Agent Loop" 或 "ReAct Loop"
"""

import json
from openai import OpenAI
from tools import TOOL_DEFINITIONS, execute_tool


class MiniAgent:
    """最小化的 Agent 实现"""

    def __init__(self, client: OpenAI, model: str = "gpt-4o-mini"):
        """
        初始化 Agent
        
        参数:
            client: OpenAI 客户端实例
            model: 使用的模型名称
        """
        self.client = client
        self.model = model
        # 对话历史：Agent 的 "记忆"
        self.messages = [
            {
                "role": "system",
                "content": (
                    "你是一个有用的 AI 助手。你可以使用工具来帮助用户。"
                    "回答时使用中文。如果需要计算或查询信息，请使用提供的工具。"
                ),
            }
        ]
        # 最大工具调用轮数，防止无限循环
        self.max_iterations = 10

    def chat(self, user_input: str) -> str:
        """
        处理用户输入，返回 Agent 的回复
        
        这是 Agent Loop 的核心实现：
        用户输入 → LLM 思考 → (可能调用工具) → 最终回复
        
        参数:
            user_input: 用户的输入文本
        返回:
            Agent 的最终回复文本
        """
        # 第 1 步：将用户消息加入对话历史
        self.messages.append({"role": "user", "content": user_input})

        # 第 2 步：开始 Agent Loop
        for i in range(self.max_iterations):
            print(f"  [Agent] 第 {i + 1} 轮思考中...")

            # 调用 LLM，传入对话历史和工具定义
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",  # 让 LLM 自己决定是否调用工具
            )

            # 获取 LLM 的回复
            message = response.choices[0].message

            # 将 LLM 的回复加入对话历史（无论是文本还是工具调用）
            self.messages.append(message)

            # 第 3 步：判断 LLM 是否要调用工具
            if not message.tool_calls:
                # LLM 选择直接回复，Agent Loop 结束
                print("  [Agent] 思考完成，直接回复")
                return message.content

            # 第 4 步：LLM 要调用工具，逐个执行
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                # 解析 LLM 传来的参数（JSON 字符串 → 字典）
                arguments = json.loads(tool_call.function.arguments)

                print(f"  [Agent] 调用工具: {tool_name}({arguments})")

                # 执行工具
                result = execute_tool(tool_name, arguments)
                print(f"  [Agent] 工具返回: {result}")

                # 第 5 步：将工具执行结果加入对话历史
                # 注意：必须用 tool_call_id 关联，LLM 才能知道这是哪个调用的结果
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )

            # 回到循环顶部，让 LLM 根据工具结果继续思考

        # 超过最大轮数，强制结束
        return "抱歉，我思考了太多轮还没得出结论，请简化你的问题。"

    def reset(self):
        """重置对话历史（保留 system prompt）"""
        self.messages = self.messages[:1]
        print("  [Agent] 对话已重置")
