"""
练习 3：函数定义 + 类型提示 + 默认参数

知识点：
- 函数定义、参数类型提示、返回值类型提示
- 默认参数
- **kwargs 接收任意关键字参数

完成下面的 TODO 部分
"""


# ============================================================
# 第 1 题：基本函数 + 类型提示
# ============================================================

# TODO: 定义一个函数 greet
# - 参数：name (str 类型)
# - 返回值：str 类型
# - 功能：返回 "你好，{name}！"
# 提示：def greet(name: str) -> str:

# 写在这里：
def greet(name: str) -> str:
    return f"你好，{name}！"


# ============================================================
# 第 2 题：默认参数
# ============================================================

# TODO: 定义一个函数 connect
# - 参数：host (str)，port (int，默认值 8080)
# - 返回值：str
# - 功能：返回 "连接到 {host}:{port}"

# 写在这里：
def connect(host: str, port: int = 8080) -> str:
    return f"连接到 {host}:{port}"


# ============================================================
# 第 3 题：用字典做函数注册表
# ============================================================

def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


# TODO: 创建一个字典 operations，把函数名（字符串）映射到函数本身
# 格式：{"add": add, "subtract": subtract, "multiply": multiply}
operations = {"add": add, "subtract": subtract, "multiply": multiply}  # 改这行


# TODO: 定义一个函数 execute_operation
# - 参数：op_name (str), a (数字), b (数字)
# - 功能：从 operations 字典中找到对应函数并调用
# - 如果 op_name 不存在，返回 "未知操作"
# 提示：这就是 tools.py 中 execute_tool 的简化版

# 写在这里：
def execute_operation(op_name, a, b) -> str:
    if operations.__contains__(op_name):
        return operations.get(op_name)(a, b)
    else:
        return "未知操作"


# ============================================================
# 自测
# ============================================================
if __name__ == "__main__":
    print("=" * 40)
    print("练习 3 自测")
    print("=" * 40)

    # 测试第 1 题
    assert greet("小明") == "你好，小明！", "❌ 第 1 题：返回值不对"
    print("✅ 第 1 题通过")

    # 测试第 2 题
    assert connect("localhost") == "连接到 localhost:8080", "❌ 第 2 题：默认端口不对"
    assert connect("example.com", 3000) == "连接到 example.com:3000", "❌ 第 2 题：自定义端口不对"
    print("✅ 第 2 题通过")

    # 测试第 3 题
    assert operations is not None, "❌ 第 3 题：operations 还是 None"
    assert execute_operation("add", 3, 4) == 7, "❌ 第 3 题：add 不对"
    assert execute_operation("subtract", 10, 3) == 7, "❌ 第 3 题：subtract 不对"
    assert execute_operation("multiply", 2, 5) == 10, "❌ 第 3 题：multiply 不对"
    assert execute_operation("divide", 1, 2) == "未知操作", "❌ 第 3 题：未知操作处理不对"
    print("✅ 第 3 题通过")

    print("\n🎉 练习 3 全部通过！")
