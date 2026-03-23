# 📦 运单号识别 API

调用通义千问 Qwen VL（视觉语言模型）识别运单标签上的运单号。
识别不出来的自动标记为人工处理。

## 架构

```
客户端上传图片 → FastAPI 接口 → Qwen VL 视觉模型 → 返回运单号
                    ↓                                    ↓
              信号量并发控制                    识别不出 → need_manual: true
```

## 快速开始

```bash
cd label-ocr
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入通义千问 API Key

# 启动服务
uvicorn main:app --reload --port 8000
```

## API 接口

### 1. 上传图片识别
```bash
curl -X POST http://localhost:8000/recognize/upload \
  -F "file=@label.jpg"
```

### 2. Base64 识别
```bash
curl -X POST http://localhost:8000/recognize/base64 \
  -H "Content-Type: application/json" \
  -d '{"image": "base64编码的图片"}'
```

### 3. URL 识别
```bash
curl -X POST http://localhost:8000/recognize/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/label.jpg"}'
```

### 返回格式
```json
{
  "success": true,
  "tracking_numbers": [
    {"carrier": "UPS", "number": "1ZV57J62YW98064807"},
    {"carrier": "USPS", "number": "92612903772171541497882986"}
  ],
  "need_manual": false,
  "cost_ms": 2300,
  "error": null
}
```

### 4. 统计接口
```bash
curl http://localhost:8000/stats
```

## 并发设计

- 500次/分钟 ≈ 8.3次/秒
- 使用 asyncio.Semaphore 控制最大并发数（默认 10）
- 超过并发限制的请求会排队等待
- 类比 Java：类似 `Semaphore` + `CompletableFuture`

## API 文档

启动后访问：http://localhost:8000/docs
