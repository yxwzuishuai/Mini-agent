"""
LangGraph 流程编排 - 核心文件

用图（Graph）定义多个 Agent 之间的协作流程：

    研究员 → 写手 → 审核员 → (PASS → 结束 / REVISE → 写手)

类比 Java：
- Graph 就像 Spring State Machine（状态机）
- 每个节点（node）是一个处理步骤
- 边（edge）定义了步骤之间的跳转规则

LangGraph 核心概念：
- State：在所有节点之间共享的数据（类似 Java 的 Context）
- Node：处理节点，每个节点是一个函数
- Edge：连接节点的边，决定下一步去哪里
- Conditional Edge：条件边，根据结果动态决定下一步
"""

import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from agents import create_llm, RESEARCHER_PROMPT, WRITER_PROMPT, REVIEWER_PROMPT
from tools import search_web, count_words


# ============================================================
# 第 1 步：定义 State（共享状态）
# 所有节点都能读写这个 State，类似 Java 的 Context 对象
# ============================================================
class AgentState(TypedDict):
    topic: str              # 用户输入的主题
    research: str           # 研究员的研究结果
    draft: str              # 写手的文章草稿
    review: str             # 审核员的审核意见
    revision_count: int     # 修改次数（防止无限循环）
    final_result: str       # 最终结果


# ============================================================
# 第 2 步：定义节点函数
# 每个函数接收 state，返回更新后的 state
# ============================================================

def researcher_node(state: AgentState) -> dict:
    """研究员节点：搜索资料并整理"""
    print("\n🔍 【研究员】正在搜索资料...")

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm = create_llm(api_key, base_url, model)

    # 先用工具搜索
    search_result = search_web.invoke({"query": state["topic"]})

    # 让 LLM 整理搜索结果
    messages = [
        SystemMessage(content=RESEARCHER_PROMPT),
        HumanMessage(content=f"主题：{state['topic']}\n\n搜索到的资料：\n{search_result}")
    ]
    response = llm.invoke(messages)
    print(f"   研究完成 ✅")

    return {"research": response.content}


def writer_node(state: AgentState) -> dict:
    """写手节点：根据资料写文章"""
    print("\n✍️  【写手】正在撰写文章...")

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm = create_llm(api_key, base_url, model)

    # 构建 prompt，包含研究资料和（可能的）修改意见
    content = f"主题：{state['topic']}\n\n研究资料：\n{state['research']}"
    if state.get("review"):
        content += f"\n\n上次审核意见（请根据意见修改）：\n{state['review']}"

    messages = [
        SystemMessage(content=WRITER_PROMPT),
        HumanMessage(content=content)
    ]
    response = llm.invoke(messages)
    print(f"   撰写完成 ✅")

    return {"draft": response.content}


def reviewer_node(state: AgentState) -> dict:
    """审核员节点：审核文章质量"""
    print("\n📋 【审核员】正在审核文章...")

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm = create_llm(api_key, base_url, model)

    messages = [
        SystemMessage(content=REVIEWER_PROMPT),
        HumanMessage(content=f"请审核以下文章：\n\n{state['draft']}")
    ]
    response = llm.invoke(messages)
    review_text = response.content
    print(f"   审核完成 ✅")

    return {
        "review": review_text,
        "revision_count": state.get("revision_count", 0) + 1
    }


# ============================================================
# 第 3 步：定义条件边（Conditional Edge）
# 根据审核结果决定下一步：通过 → 结束，不通过 → 回到写手
# ============================================================

def should_revise(state: AgentState) -> str:
    """
    条件函数：决定是结束还是打回重写
    返回值就是下一个节点的名字
    """
    # 最多修改 2 次，防止无限循环
    if state.get("revision_count", 0) >= 2:
        print("\n⚠️  已达到最大修改次数，强制通过")
        return "end"

    # 检查审核结果
    if "PASS" in state.get("review", ""):
        return "end"
    else:
        print("\n🔄 审核未通过，打回重写...")
        return "revise"


def format_output(state: AgentState) -> dict:
    """最终输出节点：整理结果"""
    result = f"""
{'='*50}
📝 最终文章
{'='*50}

{state['draft']}

{'='*50}
📋 审核意见：{state['review']}
🔄 修改次数：{state.get('revision_count', 0)}
{'='*50}
"""
    return {"final_result": result}


# ============================================================
# 第 4 步：构建 Graph（核心！）
# ============================================================

def build_graph():
    """
    构建 LangGraph 工作流

    流程图：
        researcher → writer → reviewer → (PASS → output → END)
                                       → (REVISE → writer → ...)
    """
    # 创建图，指定 State 类型
    graph = StateGraph(AgentState)

    # 添加节点（类似 Java 的 addState）
    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("output", format_output)

    # 添加边（定义流转顺序）
    graph.add_edge("researcher", "writer")       # 研究员 → 写手
    graph.add_edge("writer", "reviewer")          # 写手 → 审核员

    # 添加条件边（审核员之后，根据结果决定去向）
    graph.add_conditional_edges(
        "reviewer",                    # 从审核员节点出发
        should_revise,                 # 用这个函数判断
        {
            "end": "output",           # 通过 → 输出
            "revise": "writer",        # 不通过 → 回到写手
        }
    )

    graph.add_edge("output", END)                 # 输出 → 结束

    # 设置入口节点
    graph.set_entry_point("researcher")

    # 编译图（类似 Java 的 build()）
    return graph.compile()
