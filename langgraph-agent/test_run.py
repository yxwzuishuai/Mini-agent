"""一次性测试脚本，验证 graph 能跑通"""
import os
from dotenv import load_dotenv
from graph import build_graph

load_dotenv()

workflow = build_graph()
result = workflow.invoke({
    "topic": "AI Agent",
    "research": "",
    "draft": "",
    "review": "",
    "revision_count": 0,
    "final_result": "",
})
print(result["final_result"])
