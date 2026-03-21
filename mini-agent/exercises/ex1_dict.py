"""
练习 1：字典操作 + ** 解包

知识点：
- 创建字典
- 往字典里添加键值对
- 用 ** 把字典展开为函数参数

完成下面的 TODO 部分
"""

# ============================================================
# 第 1 题：创建字典
# ============================================================

# TODO: 创建一个字典 config，包含 "name" -> "mini-agent", "version" -> "1.0"
config = {"name": "mini-agent", "version": "1.0"}

# ============================================================
# 第 2 题：动态添加键值对
# ============================================================

# TODO: 给 config 字典添加一个键 "debug"，值为 True
# 写在这里：
config["debug"] = True

# ============================================================
# 第 3 题：** 解包
# ============================================================

def create_client(api_key, base_url="https://api.openai.com"):
    """模拟创建客户端，返回配置信息"""
    return f"客户端已创建: key={api_key}, url={base_url}"


# TODO: 创建一个字典 kwargs，然后用 ** 解包传给 create_client
# 要求：api_key 为 "sk-test123"，base_url 为 "https://api.deepseek.com"
kwargs = {"api_key":"sk-test123", "base_url":"https://api.deepseek.com"}  # 改这行
result = create_client(**kwargs)  # 取消这行注释


# ============================================================
# 自测（写完后运行 python ex1_dict.py）
# ============================================================
if __name__ == "__main__":
    print("=" * 40)
    print("练习 1 自测")
    print("=" * 40)

    # 测试第 1 题
    assert config is not None, "❌ 第 1 题：config 还是 None，请创建字典"
    assert config.get("name") == "mini-agent", "❌ 第 1 题：name 的值不对"
    assert config.get("version") == "1.0", "❌ 第 1 题：version 的值不对"
    print("✅ 第 1 题通过")

    # 测试第 2 题
    assert config.get("debug") is True, "❌ 第 2 题：debug 键不存在或值不对"
    print("✅ 第 2 题通过")

    # 测试第 3 题
    assert kwargs is not None, "❌ 第 3 题：kwargs 还是 None"
    result = create_client(**kwargs)
    assert "sk-test123" in result, "❌ 第 3 题：api_key 不对"
    assert "deepseek" in result, "❌ 第 3 题：base_url 不对"
    print("✅ 第 3 题通过")

    print("\n🎉 练习 1 全部通过！")
