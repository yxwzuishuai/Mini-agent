"""
练习 6：完整 Agent Loop（最终挑战）

知识点：
- 把前面所有练习的知识组合起来
- 实现一个不依赖 OpenAI 的模拟 Agent Loop
- 理解 Agent 的消息流转过程

我们用一个 FakeLLM 来模拟 OpenAI 的行为，
这样不需要 API Key 也能跑通整个 Agent Loop。

完成下面的 TODO 部分
"""

import json


# ============================================================
# 预置代码：模拟 LLM（不需要修改）
# ============================================================

class FakeToolCall:
    """模拟 OpenAI 的 tool_call 对象"""

    def __init__(self, call_id, name, arguments):
        self.id = call_id
        self.function = type("Function", (), {"name": name, "arguments": json.dumps(arguments)})()


class FakeMessage:
    """模拟 OpenAI 的 message 对象"""

    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls
        self.role = "assistant"


class FakeLLM:
    """
    模拟 LLM 的行为：
    - 如果用户问时间 → 调用 get_time 工具
    - 如果用户问计算 → 调用 calculate 工具
    - 否则 → 直接回复
    """

    def create(self, model, messages, tools, tool_choice):
        last_msg = messages[-1]

        # 如果上一条是工具结果，直接生成回复
        if last_msg.get("role") == "tool":
            tool_result = last_msg["content"]
            content = f"根据查询结果：{tool_result}"
            msg = FakeMessage(content=content)
            return type("Response", (), {"choices": [type("Choice", (), {"message": msg})()]})()

        user_text = last_msg.get("content", "")

        # 判断是否需要调用工具
        if "时间" in user_text or "几点" in user_text:
            tool_call = FakeToolCall("call_001", "get_time", {})
            msg = FakeMessage(tool_calls=[tool_call])
        elif "计算" in user_text or "+" in user_text or "-" in user_text:
            expr = user_text.replace("计算", "").strip()
            tool_call = FakeToolCall("call_002", "calculate", {"expression": expr})
            msg = FakeMessage(tool_calls=[tool_call])
        else:
            msg = FakeMessage(content=f"你说的是：{user_text}")

        return type("Response", (), {"choices": [type("Choice", (), {"message": msg})()]})()


# ============================================================
# 预置代码：工具（不需要修改）
# ============================================================

from datetime import datetime


def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate(expression):
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"计算错误: {e}"


TOOL_REGISTRY = {
    "get_time": get_time,
    "calculate": calculate,
}


def execute_tool(name, arguments):
    if name not in TOOL_REGISTRY:
        return f"未知工具: {name}"
    return TOOL_REGISTRY[name](**arguments)


    # ============================================================
    # TODO：实现 MiniAgent 类
    # ============================================================

    # TODO: 定义 MiniAgent 类，包含以下内容：
    #
    # __init__ 方法：
    #   - 参数：llm（FakeLLM 实例），model（str，默认 "fake-model"）
    #   - 初始化 self.llm = llm
    #   - 初始化 self.model = model
    #   - 初始化 self.messages 为列表，包含一条 system 消息：
    #     {"role": "system", "content": "你是一个有用的助手。"}
    #   - 初始化 self.max_iterations = 10
    #
    # chat 方法：
    #   - 参数：user_input (str)
    #   - 返回值：str（Agent 的最终回复）
    #   - 实现 Agent Loop：
    #     1. 把 user_input 作为 user 消息追加到 self.messages
    #     2. 循环最多 max_iterations 次：
    #        a. 调用 self.llm.create(model=..., messages=..., tools=[], tool_choice="auto")
    #        b. 取出 response.choices[0].message
    #        c. 把 message 追加到 self.messages（注意：追加的是字典格式）
    #           - 如果没有 tool_calls：追加 {"role": "assistant", "content": message.content}
    #           - 如果有 tool_calls：追加 {"role": "assistant", "content": None, "tool_calls": [...]}
    #             （这步可以简化，直接追加 {"role": "assistant", "content": message.content} 即可）
    #        d. 如果 message.tool_calls 为 None 或空 → 返回 message.content（循环结束）
    #        e. 如果有 tool_calls → 遍历每个 tool_call：
    #           - 取出 tool_call.function.name 和 json.loads(tool_call.function.arguments)
    #           - 调用 execute_tool 执行
    #           - 把结果追加到 self.messages：
    #             {"role": "tool", "tool_call_id": tool_call.id, "content": 结果}
    #        f. 继续下一轮循环
    #     3. 如果超过 max_iterations，返回 "超过最大轮数"
    #
    # reset 方法：
    #   - 无参数
    #   - 只保留 messages 的第一条（system prompt）

    # 写在这里：

    #     def __init__(self, llm: FakeLLM, model:str):
    #         self.llm = llm
    #         self.model = model
    #         self.messages = [{"role": "system", "content": "你是一个有用的助手。"}]
    #         self.max_iterations = 10
    #
    #     def chat(self, user_input):
    #         self.messages.append({"user": user_input})
    #         for _ in range(self.max_iterations):
    #             response = self.llm.create(self.llm, self.messages, TOOL_REGISTRY, "auto")
    #             message = response.choices[0].message
    #             self.messages .append({"message":message})
    #             if not message.tool_calls:
    #                 self.messages.append({"role": "assistant", "content": message.content})
    #             else:
    #                 self.messages.append({"role": "assistant", "content": None, "tool_calls": message.tool_calls})
    #             if not message.tool_calls:
    #                 return message.content
    #             else:
    #                 for tool_call in message.tool_calls:
    #                     self.messages.append({"execute_tool", execute_tool(tool_call.function.name, json.loads(tool_call.function.arguments))})


class MiniAgent:


    def chat(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        for _ in range(self.max_iterations):
            response = self.llm.create(model=self.model, messages=self.messages, tools=[], tool_choice="auto")
            message = response.choices[0].message
            # 追加 assistant 消息
            self.messages.append({"role": "assistant", "content": message.content})
            # 没有工具调用，直接返回
            if not message.tool_calls:
                return message.content
            # 有工具调用，逐个执行
            for tool_call in message.tool_calls:
                result = execute_tool(tool_call.function.name, json.loads(tool_call.function.arguments))
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        return "超过最大轮数"


def reset(self):
    self.messages = self.messages[:1]


# ============================================================
# 自测
# ============================================================
if __name__ == "__main__":
    print("=" * 40)
    print("练习 6 自测")
    print("=" * 40)

    llm = FakeLLM()
    agent = MiniAgent(llm)

    # 测试 1：直接回复（不调用工具）
    reply = agent.chat("你好啊")
    assert "你好啊" in reply, f"❌ 测试 1：直接回复不对，得到: {reply}"
    print(f"✅ 测试 1 通过 - 直接回复: {reply}")

    # 测试 2：调用工具（时间）
    agent.reset()
    reply = agent.chat("现在几点了")
    assert "根据查询结果" in reply, f"❌ 测试 2：工具调用不对，得到: {reply}"
    print(f"✅ 测试 2 通过 - 工具调用: {reply}")

    # 测试 3：调用工具（计算）
    agent.reset()
    reply = agent.chat("计算 2 + 3")
    assert "根据查询结果" in reply, f"❌ 测试 3：计算不对，得到: {reply}"
    print(f"✅ 测试 3 通过 - 计算: {reply}")

    # 测试 4：reset 后消息历史应该只有 1 条
    agent.reset()
    assert len(agent.messages) == 1, "❌ 测试 4：reset 后消息数量不对"
    assert agent.messages[0]["role"] == "system", "❌ 测试 4：reset 后第一条不是 system"
    print("✅ 测试 4 通过 - reset 正常")

    print("\n🎉 练习 6 全部通过！你已经理解了 Agent Loop 的核心原理！")
    print("下一步：回到 mini-agent/ 目录，用真实的 OpenAI API 跑一下 main.py 试试。")
