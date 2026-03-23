"""
运单号识别 API - FastAPI 接口

接口：
1. POST /recognize/upload   - 上传图片文件识别
2. POST /recognize/base64   - base64 编码图片识别
3. POST /recognize/url      - 图片 URL 识别

并发处理：
- 使用 asyncio + 信号量控制并发（500次/分钟 ≈ 8-9次/秒）
- 超过并发限制时排队等待
"""

import asyncio
import base64
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from ocr_service import recognize_from_base64, recognize_from_url

load_dotenv()

# ============================================================
# 并发控制
# 500次/分钟 ≈ 8.3次/秒，设置信号量限制同时处理的请求数
# 类比 Java：类似 Semaphore（信号量）
# ============================================================
MAX_CONCURRENT = 10  # 最大同时处理 10 个请求
semaphore = asyncio.Semaphore(MAX_CONCURRENT)

# 简单的统计计数器
stats = {"total": 0, "success": 0, "manual": 0, "error": 0}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("🚀 运单识别服务启动")
    yield
    print("👋 运单识别服务关闭")


app = FastAPI(
    title="运单号识别 API",
    description="调用通义千问 Qwen VL 模型识别运单标签上的运单号",
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================
# 请求/响应模型
# ============================================================

class Base64Request(BaseModel):
    """base64 图片请求"""
    image: str  # base64 编码的图片


class UrlRequest(BaseModel):
    """图片 URL 请求"""
    url: str  # 图片的 URL 地址


class TrackingNumber(BaseModel):
    """运单号"""
    carrier: str  # 承运商（UPS/USPS/FedEx 等）
    number: str   # 运单号


class RecognizeResponse(BaseModel):
    """识别结果"""
    success: bool                          # 是否成功
    tracking_numbers: list[TrackingNumber]  # 识别到的运单号列表
    need_manual: bool                      # 是否需要人工处理
    cost_ms: int                           # 耗时（毫秒）
    error: str | None = None               # 错误信息


# ============================================================
# 接口实现
# ============================================================

@app.post("/recognize/upload", response_model=RecognizeResponse)
async def recognize_upload(file: UploadFile = File(...)):
    """
    上传图片文件识别运单号

    支持 jpg/png/webp/pdf 格式（PDF 会逐页识别）
    """
    allowed_types = ["image/jpeg", "image/png", "image/webp", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="只支持 jpg/png/webp/pdf 格式")

    content = await file.read()

    # PDF 文件：先转成图片，再逐页识别
    if file.content_type == "application/pdf":
        return await _do_recognize_pdf(content)

    # 图片文件：直接转 base64 识别
    image_base64 = base64.b64encode(content).decode("utf-8")
    return await _do_recognize_base64(image_base64)


@app.post("/recognize/base64", response_model=RecognizeResponse)
async def recognize_base64(req: Base64Request):
    """
    base64 编码图片识别运单号

    请求体：{"image": "base64编码的图片"}
    """
    return await _do_recognize_base64(req.image)


@app.post("/recognize/url", response_model=RecognizeResponse)
async def recognize_url(req: UrlRequest):
    """
    图片 URL 识别运单号

    请求体：{"url": "图片URL地址"}
    """
    start = time.time()

    async with semaphore:  # 并发控制
        # 在线程池中运行同步的 API 调用（避免阻塞事件循环）
        result = await asyncio.to_thread(recognize_from_url, req.url)

    cost_ms = int((time.time() - start) * 1000)
    _update_stats(result)

    return RecognizeResponse(
        success=result["success"],
        tracking_numbers=result.get("tracking_numbers", []),
        need_manual=result.get("need_manual", True),
        cost_ms=cost_ms,
        error=result.get("error"),
    )


async def _do_recognize_pdf(pdf_bytes: bytes) -> RecognizeResponse:
    """
    PDF 识别逻辑：
    1. 用 PyMuPDF 把 PDF 每页转成图片
    2. 逐页调用 Qwen VL 识别
    3. 合并所有页的识别结果
    """
    import fitz  # PyMuPDF

    start = time.time()
    all_tracking = []
    need_manual = False

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        for page_num in range(len(doc)):
            page = doc[page_num]
            # 将页面渲染为图片（分辨率 200 DPI，够用且不会太大）
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")
            img_base64 = base64.b64encode(img_bytes).decode("utf-8")

            # 识别这一页
            async with semaphore:
                result = await asyncio.to_thread(recognize_from_base64, img_base64)

            if result.get("tracking_numbers"):
                all_tracking.extend(result["tracking_numbers"])
            if result.get("need_manual"):
                need_manual = True

        doc.close()

    except Exception as e:
        cost_ms = int((time.time() - start) * 1000)
        stats["total"] += 1
        stats["error"] += 1
        return RecognizeResponse(
            success=False, tracking_numbers=[], need_manual=True,
            cost_ms=cost_ms, error=f"PDF 处理失败: {e}",
        )

    cost_ms = int((time.time() - start) * 1000)

    # 如果一页都没识别出来，标记人工处理
    if not all_tracking:
        need_manual = True

    stats["total"] += 1
    if need_manual and not all_tracking:
        stats["manual"] += 1
    else:
        stats["success"] += 1

    return RecognizeResponse(
        success=True,
        tracking_numbers=all_tracking,
        need_manual=need_manual,
        cost_ms=cost_ms,
    )


async def _do_recognize_base64(image_base64: str) -> RecognizeResponse:
    """base64 识别的通用逻辑"""
    start = time.time()

    async with semaphore:  # 并发控制（类似 Java 的 Semaphore.acquire()）
        # asyncio.to_thread：把同步函数放到线程池执行，不阻塞主线程
        # 类比 Java：CompletableFuture.supplyAsync(() -> recognize(...))
        result = await asyncio.to_thread(recognize_from_base64, image_base64)

    cost_ms = int((time.time() - start) * 1000)
    _update_stats(result)

    return RecognizeResponse(
        success=result["success"],
        tracking_numbers=result.get("tracking_numbers", []),
        need_manual=result.get("need_manual", True),
        cost_ms=cost_ms,
        error=result.get("error"),
    )


def _update_stats(result: dict):
    """更新统计"""
    stats["total"] += 1
    if result.get("error"):
        stats["error"] += 1
    elif result.get("need_manual"):
        stats["manual"] += 1
    else:
        stats["success"] += 1


@app.get("/stats")
async def get_stats():
    """获取识别统计"""
    return stats


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok"}
