"""
练习 8：异步编程基础（Agent 开发必备）

知识点：
- async/await 基本语法
- asyncio.run 启动异步函数
- asyncio.gather 并发执行
- 异步上下文管理器概念

Agent 调用 LLM API 是网络请求，异步编程能大幅提升效率。
这个练习用 asyncio.sleep 模拟网络请求延迟。

完成下面的 TODO 部分
"""

import asyncio
import time


# ============================================================
# 第 1 题：基本的 async/await
# ============================================================

# TODO: 定义一个异步函数 async_greet
# - 参数：name (str)
# - 用 await asyncio.sleep(0.1) 模拟网络延迟
# - 返回 f"你好，{name}！"
#
# 提示：在 def 前面加 async，sleep 前面加 await

# 写在这里：

async def async_greet(name):
    await asyncio.sleep(0.1)
    return f"你好，{name}！"


# ============================================================
# 第 2 题：顺序执行 vs 并发执行
# ============================================================

async def fake_api_call(name, delay):
    """模拟一个耗时的 API 调用"""
    await asyncio.sleep(delay)
    return f"{name} 完成"


async def sequential_calls():
    """
    TODO: 顺序调用 3 次 fake_api_call，每次延迟 0.1 秒
    调用参数：("任务A", 0.1), ("任务B", 0.1), ("任务C", 0.1)
    返回：3 个结果组成的列表
    
    提示：依次 await 三次，把结果收集到列表里
    预期总耗时：约 0.3 秒（串行）
    """
    result1 = await fake_api_call("任务A", 0.1)
    result2 = await fake_api_call("任务B", 0.1)
    result3 = await fake_api_call("任务C", 0.1)
    return [result1, result2, result3]


async def concurrent_calls():
    """
    TODO: 并发调用 3 次 fake_api_call，每次延迟 0.1 秒
    调用参数：("任务A", 0.1), ("任务B", 0.1), ("任务C", 0.1)
    返回：3 个结果组成的列表
    
    提示：用 asyncio.gather() 同时发起三个调用
    预期总耗时：约 0.1 秒（并行）
    """
    return list(await asyncio.gather(
        fake_api_call("A", 0.1),

        fake_api_call("B", 0.1),

        fake_api_call("C", 0.1)
    ))


# ============================================================
# 第 3 题：异步函数中的异常处理
# ============================================================

async def safe_api_call(url):
    """
    模拟安全的 API 调用：
    - 如果 url 包含 "error"，抛出 Exception("请求失败")
    - 否则等待 0.05 秒后返回 f"响应: {url}"
    
    TODO: 实现这个函数
    """
    if "error" in url:
        raise Exception("请求失败")
    else:
        await asyncio.sleep(0.05)
        return f"响应：{url}"


async def batch_api_calls(urls):
    """
    批量调用 API，即使某个失败也不影响其他的
    
    TODO:
    - 遍历 urls 列表
    - 对每个 url 调用 safe_api_call
    - 用 try/except 捕获异常
    - 成功的结果存入列表，失败的存 f"失败: {错误信息}"
    - 返回结果列表
    """
    list1 = []
    for url in urls:
        try:
            result_url = await safe_api_call(url)
            list1.append(result_url)
        except Exception as e:
            list1.append(f"失败:{e}")
    return list1

# ============================================================
# 自测
# ============================================================
async def run_tests():
    print("=" * 40)
    print("练习 8 自测")
    print("=" * 40)

    # 测试第 1 题
    result = await async_greet("小明")
    assert result == "你好，小明！", f"❌ 1：返回值不对，得到: {result}"
    print("✅ 第 1 题通过")

    # 测试第 2 题 - 顺序执行
    start = time.time()
    seq_results = await sequential_calls()
    seq_time = time.time() - start
    assert len(seq_results) == 3, f"❌ 2a：应该有 3 个结果，得到 {len(seq_results)}"
    assert seq_time >= 0.25, f"❌ 2a：顺序执行应该 >= 0.25 秒，实际 {seq_time:.2f} 秒"
    print(f"✅ 第 2 题（顺序）通过 - 耗时 {seq_time:.2f} 秒")

    # 测试第 2 题 - 并发执行
    start = time.time()
    con_results = await concurrent_calls()
    con_time = time.time() - start
    assert len(con_results) == 3, f"❌ 2b：应该有 3 个结果，得到 {len(con_results)}"
    assert con_time < 0.2, f"❌ 2b：并发执行应该 < 0.2 秒，实际 {con_time:.2f} 秒"
    print(f"✅ 第 2 题（并发）通过 - 耗时 {con_time:.2f} 秒")

    # 测试第 3 题
    urls = ["https://api.example.com/ok", "https://api.error.com/fail", "https://api.example.com/data"]
    results = await batch_api_calls(urls)
    assert len(results) == 3, f"❌ 3：应该有 3 个结果，得到 {len(results)}"
    assert "响应" in results[0], f"❌ 3：第一个应该成功，得到: {results[0]}"
    assert "失败" in results[1], f"❌ 3：第二个应该失败，得到: {results[1]}"
    assert "响应" in results[2], f"❌ 3：第三个应该成功，得到: {results[2]}"
    print("✅ 第 3 题通过")

    print("\n🎉 练习 8 全部通过！你已经掌握了异步编程基础！")


if __name__ == "__main__":
    asyncio.run(run_tests())
