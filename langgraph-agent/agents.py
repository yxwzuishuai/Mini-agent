"""
Agent 定义 - 3 个协作的 Agent

1. 研究员（Researcher）：负责搜索收集资料
2. 写手（Writer）：根据资料撰写文章
3. 审核员（Reviewer）：审核文章质量

类比 Java：每个 Agent 就像一个微服务，有自己的职责
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


def create_llm(api_key: str, base_url: str = None, model: str = "gpt-4o-mini"):
    """创建 LLM 实例（所有 Agent 共用的工厂方法）"""
    kwargs = {"model": model, "api_key": api_key, "temperature": 0.7}
    if base_url:
        kwargs["base_url"] = base_url
    return ChatOpenAI(**kwargs)


# ============================================================
# 研究员 Agent 的 system prompt
# ============================================================
RESEARCHER_PROMPT = """你是一个专业的研究员。你的任务是：
1. 根据用户的主题，搜索相关资料
2. 整理搜索结果，提取关键信息
3. 输出一份简洁的研究摘要（200字以内）

请使用 search_web 工具来搜索信息。
输出格式：
【研究摘要】
（你整理的内容）
"""

# ============================================================
# 写手 Agent 的 system prompt
# ============================================================
WRITER_PROMPT = """你是一个专业的技术写手。你的任务是：
1. 根据研究员提供的资料，撰写一篇短文（300字以内）
2. 文章要通俗易懂，适合初学者阅读
3. 使用中文撰写

输出格式：
【文章标题】
（标题）

【正文】
（文章内容）
"""

# ============================================================
# 审核员 Agent 的 system prompt
# ============================================================
REVIEWER_PROMPT = """你是一个严格的内容审核员。你的任务是：
1. 审核写手的文章质量
2. 检查内容是否准确、是否通俗易懂、是否有遗漏

你必须给出以下两种结论之一：
- PASS：文章质量合格，可以发布
- REVISE：文章需要修改，并给出具体修改建议

输出格式：
【审核结果】PASS 或 REVISE
【审核意见】（你的评价和建议）
"""
