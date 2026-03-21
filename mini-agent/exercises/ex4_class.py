"""
练习 4：类 + __init__ + self

知识点：
- 定义类
- __init__ 构造方法
- self 和实例属性
- 实例方法

完成下面的 TODO 部分
"""


# ============================================================
# 第 1 题：定义一个简单的类
# ============================================================

# TODO: 定义一个类 ChatHistory
# - __init__ 方法：接收参数 system_prompt (str，默认值 "你是一个助手")
#   - 初始化 self.messages 为一个列表，包含一条 system 消息：
#     {"role": "system", "content": system_prompt}
#
# - add_message 方法：接收 role (str) 和 content (str)
#   - 往 self.messages 列表追加 {"role": role, "content": content}
#
# - get_length 方法：无参数
#   - 返回 self.messages 的长度
#
# - reset 方法：无参数
#   - 只保留第一条消息（system prompt），删除其余的
#   - 提示：self.messages = self.messages[:1]

# 写在这里：

class ChatHistory:
    def __init__(self, system_prompt: str="你是一个助手"):
        self.messages = [{"role": "system", "content": system_prompt}]

    def add_message(self, role:str, content:str):
        self.messages.append({"role": role, "content": content})

    def get_length(self)-> int:
        return len(self.messages)

    def reset(self):
        self.messages = self.messages[:1]


# ============================================================
# 自测
# ============================================================
if __name__ == "__main__":
    print("=" * 40)
    print("练习 4 自测")
    print("=" * 40)

    # 测试构造方法
    history = ChatHistory("你是一个 AI 助手")
    assert history.messages[0]["role"] == "system", "❌ 第一条消息的 role 应该是 system"
    assert history.messages[0]["content"] == "你是一个 AI 助手", "❌ system prompt 内容不对"
    print("✅ 构造方法通过")

    # 测试默认参数
    h2 = ChatHistory()
    assert h2.messages[0]["content"] == "你是一个助手", "❌ 默认 system prompt 不对"
    print("✅ 默认参数通过")

    # 测试 add_message
    history.add_message("user", "你好")
    history.add_message("assistant", "你好！有什么可以帮你的？")
    assert history.get_length() == 3, "❌ 添加消息后长度应该是 3"
    assert history.messages[1]["role"] == "user", "❌ 第二条消息的 role 不对"
    print("✅ add_message 通过")

    # 测试 reset
    history.reset()
    assert history.get_length() == 1, "❌ reset 后长度应该是 1"
    assert history.messages[0]["role"] == "system", "❌ reset 后应该保留 system 消息"
    print("✅ reset 通过")

    print("\n🎉 练习 4 全部通过！")
