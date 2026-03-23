"""
运单号识别服务 - 调用通义千问 Qwen VL（视觉语言模型）

流程：
1. 接收 label 图片（base64 或 URL）
2. 调用 Qwen 视觉模型识别图片中的运单号
3. 返回识别结果，识别不出则标记为人工处理
"""

import os
import base64
import httpx
from openai import OpenAI

# Qwen 视觉模型的 prompt
# 明确告诉模型只提取运单号，减少幻觉
SYSTEM_PROMPT = """你是一个专业的物流运单识别助手。
你的任务是从运单标签图片中提取所有运单号（tracking number）。

规则：
1. 只提取运单号，不要提取其他信息
2. 运单号通常在 "TRACKING #" 或 "TRACKING NUMBER" 附近
3. 常见格式：
   - UPS: 1Z 开头，18位（如 1Z V57 J62 YW 9806 4807）
   - USPS: 通常 20-34 位数字（如 9261 2903 7721 7154 1497 8829 86）
   - FedEx: 12-15 位数字
   - DHL: 10 位数字
4. 去掉运单号中的空格，返回连续的字符串
5. 如果识别不出任何运单号，返回空数组

请严格按以下 JSON 格式返回：
{"tracking_numbers": [{"carrier": "承运商", "number": "运单号"}]}
"""


def create_client() -> OpenAI:
    """创建 Qwen API 客户端"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("请设置 DASHSCOPE_API_KEY 环境变量")

    # 通义千问兼容 OpenAI 接口格式
    return OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )


def recognize_from_base64(image_base64: str) -> dict:
    """
    从 base64 编码的图片识别运单号

    参数：
        image_base64: 图片的 base64 编码字符串
    返回：
        {"success": True/False, "tracking_numbers": [...], "need_manual": True/False}
    """
    import time
    client = create_client()
    model = os.getenv("QWEN_VL_MODEL", "qwen-vl-plus")

    try:
        start = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            },
                        },
                        {"type": "text", "text": "请识别这张运单标签上的所有运单号"},
                    ],
                },
            ],
            temperature=0.1,
        )
        llm_cost_ms = int((time.time() - start) * 1000)
        print(f"🕐 Qwen VL 请求耗时: {llm_cost_ms}ms (base64)")

        result = _parse_response(response.choices[0].message.content)
        result["llm_cost_ms"] = llm_cost_ms
        return result

    except Exception as e:
        return {
            "success": False,
            "tracking_numbers": [],
            "need_manual": True,
            "error": str(e),
            "llm_cost_ms": int((time.time() - start) * 1000),
        }


def recognize_from_url(image_url: str) -> dict:
    """
    从图片 URL 识别运单号

    参数：
        image_url: 图片的 URL 地址
    返回：
        {"success": True/False, "tracking_numbers": [...], "need_manual": True/False, "llm_cost_ms": int}
    """
    import time
    client = create_client()
    model = os.getenv("QWEN_VL_MODEL", "qwen-vl-plus")

    try:
        start = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url},
                        },
                        {"type": "text", "text": "请识别这张运单标签上的所有运单号"},
                    ],
                },
            ],
            temperature=0.1,
        )
        llm_cost_ms = int((time.time() - start) * 1000)
        print(f"🕐 Qwen VL 请求耗时: {llm_cost_ms}ms (URL: {image_url[:80]})")

        result = _parse_response(response.choices[0].message.content)
        result["llm_cost_ms"] = llm_cost_ms
        return result

    except Exception as e:
        return {
            "success": False,
            "tracking_numbers": [],
            "need_manual": True,
            "error": str(e),
            "llm_cost_ms": int((time.time() - start) * 1000),
        }


def _parse_response(content: str) -> dict:
    """
    解析模型返回的内容

    尝试从返回文本中提取 JSON，如果提取不到则标记为人工处理
    """
    import json
    import re

    try:
        # 尝试从返回内容中提取 JSON
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            tracking_numbers = data.get("tracking_numbers", [])

            if tracking_numbers:
                return {
                    "success": True,
                    "tracking_numbers": tracking_numbers,
                    "need_manual": False,
                }

        # 没有识别到运单号 → 需要人工处理
        return {
            "success": True,
            "tracking_numbers": [],
            "need_manual": True,
            "raw_response": content,
        }

    except (json.JSONDecodeError, Exception):
        # 解析失败 → 需要人工处理
        return {
            "success": False,
            "tracking_numbers": [],
            "need_manual": True,
            "raw_response": content,
        }
