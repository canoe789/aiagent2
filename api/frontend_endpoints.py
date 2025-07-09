"""
Frontend API endpoints for the MVP
最简化的API端点，专门服务于前端MVP
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["frontend"])

# 模拟的任务存储（实际应该使用数据库）
jobs_store = {}

class CreateJobRequest(BaseModel):
    chat_input: str

class JobResponse(BaseModel):
    job_id: str
    status: str
    created_at: str
    error_message: Optional[str] = None

@router.post("/jobs", response_model=JobResponse)
async def create_job(request: CreateJobRequest):
    """
    创建新的生成任务
    """
    # 生成唯一的job_id（实际应该使用UUID）
    job_id = f"job_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 创建任务记录
    job = {
        "id": job_id,
        "status": "pending",
        "input": request.chat_input,
        "created_at": datetime.now().isoformat(),
        "error_message": None,
        "result": None
    }
    
    jobs_store[job_id] = job
    
    # 异步启动处理任务（不阻塞响应）
    asyncio.create_task(process_job(job_id))
    
    return JobResponse(
        job_id=job_id,
        status="pending",
        created_at=job["created_at"]
    )

@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    获取任务状态
    """
    if job_id not in jobs_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_store[job_id]
    
    return {
        "job_id": job_id,
        "status": job["status"],
        "created_at": job["created_at"],
        "error_message": job["error_message"]
    }

@router.get("/jobs/{job_id}/result", response_class=HTMLResponse)
async def get_job_result(job_id: str):
    """
    获取生成的HTML结果
    """
    if job_id not in jobs_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_store[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    if job["result"] is None:
        raise HTTPException(status_code=500, detail="No result available")
    
    return HTMLResponse(content=job["result"])

async def process_job(job_id: str):
    """
    模拟异步处理任务
    实际应该调用Agent链
    """
    try:
        # 更新状态为处理中
        jobs_store[job_id]["status"] = "processing"
        
        # 模拟处理时间（实际应该调用Agent）
        await asyncio.sleep(10)  # 模拟10秒处理时间
        
        # 模拟生成的HTML结果
        mock_html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h1 style="color: #2563eb;">AI生成的演示文稿</h1>
            <p><strong>原始需求：</strong> {jobs_store[job_id]["input"]}</p>
            <hr>
            <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h2>第1页：开场介绍</h2>
                <p>这是基于您的需求生成的演示文稿...</p>
            </div>
            <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h2>第2页：核心内容</h2>
                <p>AI系统已经分析了您的需求，生成了相应的内容结构...</p>
            </div>
            <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h2>第3页：总结</h2>
                <p>感谢您使用HELIX AI创意生产系统！</p>
            </div>
            <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </div>
        """
        
        # 保存结果
        jobs_store[job_id]["result"] = mock_html
        jobs_store[job_id]["status"] = "completed"
        
    except Exception as e:
        jobs_store[job_id]["status"] = "failed"
        jobs_store[job_id]["error_message"] = str(e)

# 集成到主应用的示例代码
"""
# 在 main.py 中添加：

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from api.frontend_endpoints import router

app = FastAPI()

# 添加CORS支持（开发环境）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(router)

# 挂载静态文件（前端）
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
"""