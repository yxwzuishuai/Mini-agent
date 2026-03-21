"""
练习 7：进阶 Python 技巧（Agent 开发常用）

知识点：
- 列表推导式
- 异常处理（try/except/finally）
- 装饰器基础
- *args 和 **kwargs
- 三元表达式

完成下面的 TODO 部分
"""

import time

from pyexpat.errors import messages

# ============================================================
# 第 1 题：列表推导式
# Agent 开发中经常需要从列表中筛选/转换数据
# ============================================================

messages = [
    {"role": "system", "content": "你是助手"},
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！"},
    {"role": "user", "content": "帮我算个数"},
    {"role": "assistant", "content": None, "tool_calls": ["call_001"]},
    {"role": "tool", "content": "42"},
    {"role": "assistant", "content": "结果是 42"},
]

# TODO: 用列表推导式，从 messages 中筛选出所有 role 为 "user" 的消息
# 提示：[x for x in 列表 if 条件]
user_messages = [message["role"] for message in messages if message["role"] == "user"]  # 改这行

# TODO: 用列表推导式，提取所有消息的 content（包括 None）
# 提示：[x["key"] for x in 列表]
all_contents = [message["content"] for message in messages]

# TODO: 用列表推导式，提取所有 content 不为 None 的 content 值   这里不用if message["content"] 因为会把 ""也过滤掉
non_none_contents = [message["content"] for message in messages if message["content"] is not None]


# ============================================================
# 第 2 题：异常处理
# API 调用经常会失败，必须会处理异常
# ============================================================

def safe_divide(a, b):
    """
    安全除法：
    - 正常情况返回 a / b 的结果（浮点数）
    - 如果 b 为 0，返回字符串 "除数不能为零"
    - 如果 a 或 b 不是数字，返回字符串 "参数必须是数字"
    
    TODO: 用 try/except 实现
    提示：除以零会抛 ZeroDivisionError，类型错误会抛 TypeError
    """
    try:
        return a / b
    except ZeroDivisionError:
        return "除数不能为零"
    except TypeError:
        return "参数必须是数字"

# ============================================================
# 第 3 题：装饰器
# Agent 开发中常用装饰器做日志、重试、计时等
# ============================================================

def timer(func):
    """
    计时装饰器：打印函数执行耗时
    
    TODO: 实现这个装饰器
    要求：
    1. 定义内部函数 wrapper，接收 *args 和 **kwargs
    2. 记录开始时间 start = time.time()
    3. 调用原函数 result = func(*args, **kwargs)
    4. 计算耗时 elapsed = time.time() - start
    5. 打印 f"{func.__name__} 耗时 {elapsed:.4f} 秒"
    6. 返回 result
    7. 返回 wrapper
    
    提示：这就是装饰器的标准模板
    """
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} 耗时 {elapsed:.4f} 秒")
        return result
    return wrapper


# 写完装饰器后取消下面的注释来测试
# @timer
# def slow_function():
#     time.sleep(0.1)
#     return "完成"


# ============================================================
# 第 4 题：*args 和 **kwargs
# 理解可变参数，Agent 的工具调用大量使用 **kwargs
# ============================================================

def flexible_log(*args, **kwargs):
    """
    灵活的日志函数：
    - 把所有 args 用空格拼接成一个字符串
    - 如果 kwargs 中有 "level"，在前面加上 "[LEVEL] " 前缀（大写）
    - 如果没有 "level"，前缀为 "[INFO] "
    
    示例：
    flexible_log("hello", "world") → "[INFO] hello world"
    flexible_log("出错了", level="error") → "[ERROR] 出错了"
    flexible_log("a", "b", "c", level="debug") → "[DEBUG] a b c"
    
    TODO: 实现这个函数
    提示：
    - " ".join(args) 可以把 args 拼成字符串
    - kwargs.get("level", "info") 可以取 level，没有就用默认值
    """
    args = " ".join(args)
    level = kwargs.get("level", "info").upper()

    return f"[{level}] {args}"



# ============================================================
# 第 5 题：三元表达式 + 字典的 get 方法
# ============================================================

def get_model_config(provider):
    """
    根据 provider 返回模型配置
    
    规则：
    - "openai" → {"model": "gpt-4o-mini", "base_url": "https://api.openai.com/v1"}
    - "deepseek" → {"model": "deepseek-chat", "base_url": "https://api.deepseek.com/v1"}
    - 其他 → {"model": "unknown", "base_url": ""}
    
    TODO: 用字典 + get 方法实现（不要用 if/elif/else）
    提示：
    configs = {"openai": {...}, "deepseek": {...}}
    return configs.get(provider, 默认值)
    """

    configs = {"openai":{"model": "gpt-4o-mini", "base_url": "https://api.openai.com/v1"}, "deepseek":{"model": "deepseek-chat", "base_url": "https://api.deepseek.com/v1"}
               , "其他":{"model": "unknown", "base_url": ""}
               }

    return configs.get(provider, {"model": "unknown", "base_url": ""})

# ============================================================
# 自测
# ============================================================
if __name__ == "__main__":
    print("=" * 40)
    print("练习 7 自测")
    print("=" * 40)

    # 测试第 1 题
    assert user_messages is not None, "❌ 1a：user_messages 还是 None"
    assert len(user_messages) == 2, f"❌ 1a：应该有 2 条 user 消息，得到 {len(user_messages)}"
    assert all_contents is not None, "❌ 1b：all_contents 还是 None"
    assert len(all_contents) == 7, f"❌ 1b：应该有 7 个 content，得到 {len(all_contents)}"
    assert None in all_contents, "❌ 1b：应该包含 None"
    assert non_none_contents is not None, "❌ 1c：non_none_contents 还是 None"
    assert len(non_none_contents) == 6, f"❌ 1c：应该有 6 个非 None content，得到 {len(non_none_contents)}"
    assert None not in non_none_contents, "❌ 1c：不应该包含 None"
    print("✅ 第 1 题通过")

    # 测试第 2 题
    assert safe_divide(10, 3) == 10 / 3, "❌ 2：正常除法不对"
    assert safe_divide(10, 0) == "除数不能为零", "❌ 2：除以零处理不对"
    assert safe_divide("a", 2) == "参数必须是数字", "❌ 2：类型错误处理不对"
    print("✅ 第 2 题通过")

    # 测试第 3 题
    assert timer is not None, "❌ 3：timer 还是 None"


    @timer
    def test_func(x):
        return x * 2


    result = test_func(5)
    assert result == 10, f"❌ 3：装饰器应该返回原函数的结果，得到 {result}"
    print("✅ 第 3 题通过")

    # 测试第 4 题
    assert flexible_log("hello", "world") == "[INFO] hello world", \
        f"❌ 4：无 level 时不对，得到: {flexible_log('hello', 'world')}"
    assert flexible_log("出错了", level="error") == "[ERROR] 出错了", \
        f"❌ 4：有 level 时不对，得到: {flexible_log('出错了', level='error')}"
    assert flexible_log("a", "b", "c", level="debug") == "[DEBUG] a b c", \
        f"❌ 4：多参数不对，得到: {flexible_log('a', 'b', 'c', level='debug')}"
    print("✅ 第 4 题通过")

    # 测试第 5 题
    openai_config = get_model_config("openai")
    assert openai_config["model"] == "gpt-4o-mini", "❌ 5：openai model 不对"
    deepseek_config = get_model_config("deepseek")
    assert deepseek_config["model"] == "deepseek-chat", "❌ 5：deepseek model 不对"
    other_config = get_model_config("xxx")
    assert other_config["model"] == "unknown", "❌ 5：未知 provider 处理不对"
    print("✅ 第 5 题通过")

    print("\n🎉 练习 7 全部通过！")
