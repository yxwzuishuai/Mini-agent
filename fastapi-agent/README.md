# 🚀 FastAPI + LangChain Agent Demo

把 LangChain Agent 包装成 HTTP API，让前端、小程序、其他服务都能调用。

## 三个项目的演进关系

```
mini-agent（手写 Agent Loop，终端交互）
  → langchain-agent（用框架简化，终端交互）
    → fastapi-agent（包装成 HTTP API，任何客户端都能调用）
```

## 快速开始

```bash
cd fastapi-agent
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 API Key

# 启动服务
uvicorn main:app --reload
```

启动后访问 http://localhost:8000/docs 可以看到自动生成的 Swagger 文档，直接在页面上测试接口。

## API 接口

### GET /
健康检查

### POST /chat
发送消息给 Agent

请求：
```json
{"message": "现在几点了？"}
```

响应：
```json
{"reply": "现在是 2025年01月15日 14:30:22", "status": "success"}
```

### POST /chat/simple
简化版，直接返回回复

## 用 curl 测试

```bash
# 健康检查
curl http://localhost:8000/

# 聊天
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "帮我算一下 sqrt(144) + 3"}'
```

## 文件结构

```
fastapi-agent/
├── .env.example      # 环境变量模板
├── requirements.txt  # 依赖
├── tools.py          # 工具定义（@tool 装饰器）
├── agent.py          # Agent 实例（全局单例）
├── main.py           # FastAPI 路由和启动入口
└── README.md         # 本文件
```

## 核心概念对比

| 概念 | Java Spring | FastAPI |
|------|------------|---------|
| 路由 | `@GetMapping` / `@PostMapping` | `@app.get` / `@app.post` |
| 请求体 | `@RequestBody` + DTO 类 | Pydantic `BaseModel` |
| 参数校验 | `@Valid` + JSR 303 | Pydantic 自动校验 |
| 异常处理 | `@ExceptionHandler` | `HTTPException` |
| API 文档 | Swagger 需要额外配置 | 自动生成，访问 `/docs` |
| 启动 | Tomcat / Netty | uvicorn |
