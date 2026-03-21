"""
练习 5：工具定义 + JSON Schema + 注册表模式

知识点：
- 用字典定义 JSON Schema（OpenAI Function Calling 格式）
- 工具注册表模式
- json.loads 解析 JSON 字符串

这个练习模拟 tools.py 的完整结构

完成下面的 TODO 部分
"""

import json
from datetime import datetime

# ============================================================
# 第 1 题：定义工具的 JSON Schema
# ============================================================

# TODO: 补全 TOOL_DEFINITIONS 列表
# 需要定义两个工具：
#
# 工具 1：get_greeting
#   - 描述："根据名字生成问候语"
#   - 参数：name (string, 必填, 描述："要问候的人的名字")
#
# 工具 2：get_time
#   - 描述："获取当前时间"
#   - 参数：无
#
# 格式参考 tools.py 中的 TOOL_DEFINITIONS

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_greeting",
            "description": "根据名字生成问候语",
            "parameters": {
                "name": "string",
                "required": True,
                "description": "要问候的人的名字"
            }
        }

    },

    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "获取当前时间"
        }
    }
]


# ============================================================
# 第 2 题：实现工具函数
# ============================================================

# TODO: 实现 get_greeting 函数
# - 参数：name (str)
# - 返回：f"你好，{name}！欢迎使用 Mini Agent。"

# 写在这里：
def get_greeting(name) -> str:
    return f"你好，{name}！欢迎使用 Mini Agent。"


# TODO: 实现 get_time 函数
# - 无参数
# - 返回：当前时间字符串，格式 "%Y-%m-%d %H:%M:%S"

# 写在这里：

def get_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ============================================================
# 第 3 题：创建工具注册表 + 执行函数
# ============================================================

# TODO: 创建 TOOL_REGISTRY 字典，映射工具名到函数
TOOL_REGISTRY = {"get_greeting": get_greeting, "get_time": get_time()}  # 改这行


# TODO: 实现 execute_tool 函数
# - 参数：tool_name (str), arguments (dict)
# - 从 TOOL_REGISTRY 找到函数并用 **arguments 调用
# - 如果工具不存在，返回 f"未知工具: {tool_name}"
# - 如果执行出错，返回 f"执行错误: {错误信息}"

# 写在这里：
def execute_tool(tool_name : str, arguments) -> str:
    try:
        if tool_name in TOOL_REGISTRY:
            return TOOL_REGISTRY[tool_name](**arguments)
        else:
            return f"未知工具: {tool_name}"
    except Exception as e:
            return f"执行错误: {e}"


# ============================================================
# 第 4 题：模拟 LLM 返回的工具调用并执行
# ============================================================

def process_tool_call(tool_call_json: str) -> str:
    """
    模拟处理 LLM 返回的工具调用
    
    LLM 返回的工具调用是 JSON 格式，例如：
    {"name": "get_greeting", "arguments": "{\"name\": \"小明\"}"}
    
    注意：arguments 本身也是一个 JSON 字符串，需要二次解析
    
    TODO:
    1. 用 json.loads 解析 tool_call_json 得到字典
    2. 取出 "name" 和 "arguments"
    3. 用 json.loads 再解析 arguments（因为它是字符串形式的 JSON）
    4. 调用 execute_tool 执行工具
    5. 返回执行结果
    """
    # 写在这里：
    name = json.loads(tool_call_json)["name"]
    arguments = json.loads(tool_call_json)["arguments"]
    return execute_tool(name, json.loads(arguments))



# ============================================================
# 自测
# ============================================================
if __name__ == "__main__":
    print("=" * 40)
    print("练习 5 自测")
    print("=" * 40)

    # 测试第 1 题
    assert len(TOOL_DEFINITIONS) == 2, "❌ 第 1 题：应该有 2 个工具定义"
    names = [t["function"]["name"] for t in TOOL_DEFINITIONS]
    assert "get_greeting" in names, "❌ 第 1 题：缺少 get_greeting"
    assert "get_time" in names, "❌ 第 1 题：缺少 get_time"
    print("✅ 第 1 题通过")

    # 测试第 2 题
    assert get_greeting("测试") == "你好，测试！欢迎使用 Mini Agent。", "❌ 第 2 题：get_greeting 返回值不对"
    time_result = get_time()
    assert len(time_result) == 19, "❌ 第 2 题：get_time 格式不对，应该是 YYYY-MM-DD HH:MM:SS"
    print("✅ 第 2 题通过")

    # 测试第 3 题
    assert TOOL_REGISTRY is not None, "❌ 第 3 题：TOOL_REGISTRY 还是 None"
    assert execute_tool("get_greeting", {"name": "世界"}) == "你好，世界！欢迎使用 Mini Agent。", "❌ 第 3 题：execute_tool 不对"
    assert "未知工具" in execute_tool("not_exist", {}), "❌ 第 3 题：未知工具处理不对"
    print("✅ 第 3 题通过")

    # 测试第 4 题
    test_json = json.dumps({"name": "get_greeting", "arguments": json.dumps({"name": "小明"})})
    result = process_tool_call(test_json)
    assert result == "你好，小明！欢迎使用 Mini Agent。", "❌ 第 4 题：process_tool_call 不对"
    print("✅ 第 4 题通过")

    print("\n🎉 练习 5 全部通过！")
