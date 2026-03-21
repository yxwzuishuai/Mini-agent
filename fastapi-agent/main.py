"""
FastAPI + LangChain Agent Demo

这个文件展示了 FastAPI 的核心概念：
- 路由（@app.get / @app.post）
- 请求体（Pydantic 模型）
- 响应体
- 异步处理

启动方式：
    uvicorn main:app --reload

启动后访问：
    http://localhost:8000/docs  ← 自动生成的 API 文档（Swagger UI）
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import agent

# 创建 FastAPI 应用
app = FastAPI(
    title="AI Agent API",
    description="基于 LangChain 的 AI Agent HTTP 接口",
    version="1.0.0",
)


# ============================================================
# 请求和响应模型（用 Pydantic 定义）
# 类似 Java 的 DTO / VO
# ============================================================

class ChatRequest(BaseModel):
    """聊天请求体"""
    message: str  # 用户输入的消息


class ChatResponse(BaseModel):
    """聊天响应体"""
    reply: str    # Agent 的回复
    status: str   # 状态：success 或 error


# ============================================================
# API 路由
# ============================================================

@app.get("/")
async def root():
    """
    根路径 - 健康检查
    
    GET http://localhost:8000/
    相当于 Java Spring 的 @GetMapping("/")
    """
    return {"message": "AI Agent API 运行中", "docs": "访问 /docs 查看接口文档"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天接口 - 发送消息给 Agent，获取回复
    
    POST http://localhost:8000/chat
    Body: {"message": "现在几点了？"}
    
    相当于 Java Spring 的：
    @PostMapping("/chat")
    public ChatResponse chat(@RequestBody ChatRequest request) { ... }
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")

    try:
        # 调用 Agent
        result = agent.invoke({"messages": [("user", request.message)]})
        reply = result["messages"][-1].content
        return ChatResponse(reply=reply, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent 处理失败: {e}")


@app.post("/chat/simple")
async def chat_simple(request: ChatRequest):
    """
    简化版聊天接口 - 直接返回文本
    
    POST http://localhost:8000/chat/simple
    适合快速测试
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")

    try:
        result = agent.invoke({"messages": [("user", request.message)]})
        return {"reply": result["messages"][-1].content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
