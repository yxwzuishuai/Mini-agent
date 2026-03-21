"""
练习 2：环境变量 + dotenv

知识点：
- os.environ 和 os.getenv 的用法
- Python 的 falsy 值判断（not 变量）
- 字符串的 startswith 方法

完成下面的 TODO 部分
"""

import os

# ============================================================
# 第 1 题：设置和读取环境变量
# ============================================================

# TODO: 用 os.environ 设置一个环境变量 "MY_APP_NAME"，值为 "mini-agent"
# 写在这里：
os.environ["MY_APP_NAME"] = "mini-agent"
# TODO: 用 os.getenv 读取 "MY_APP_NAME"，存到变量 app_name
app_name = os.getenv("MY_APP_NAME")  # 改这行

# ============================================================
# 第 2 题：处理不存在的环境变量
# ============================================================

# TODO: 用 os.getenv 读取一个不存在的环境变量 "NOT_EXIST_VAR"
# 并提供默认值 "default_value"
# 提示：os.getenv 的第二个参数是默认值
missing_var = os.getenv("NOT_EXIST_VAR", "default_value")  # 改这行


# ============================================================
# 第 3 题：falsy 值判断
# ============================================================

def check_api_key(key):
    """
    检查 API Key 是否有效
    无效的情况：key 为 None、空字符串、或以 "sk-your" 开头
    
    TODO: 用一行 if 判断实现，返回 True（有效）或 False（无效）
    提示：参考 main.py 中的写法
    """
    # TODO: 改写下面的逻辑
    return not(not key or key.startswith("sk-your"))  # 改这行


# ============================================================
# 自测
# ============================================================
if __name__ == "__main__":
    print("=" * 40)
    print("练习 2 自测")
    print("=" * 40)

    # 测试第 1 题
    assert app_name == "mini-agent", "❌ 第 1 题：app_name 的值不对"
    print("✅ 第 1 题通过")

    # 测试第 2 题
    assert missing_var == "default_value", "❌ 第 2 题：默认值不对"
    print("✅ 第 2 题通过")

    # 测试第 3 题
    assert check_api_key(None) is False, "❌ 第 3 题：None 应该返回 False"
    assert check_api_key("") is False, "❌ 第 3 题：空字符串应该返回 False"
    assert check_api_key("sk-your-key") is False, "❌ 第 3 题：sk-your 开头应该返回 False"
    assert check_api_key("sk-abc123real") is True, "❌ 第 3 题：正常 key 应该返回 True"
    print("✅ 第 3 题通过")

    print("\n🎉 练习 2 全部通过！")
