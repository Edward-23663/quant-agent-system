# web_ui/backend/api_server.py
import os
import sys
import uuid
import asyncio
import json
import threading
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from typing import Optional, List

# Load environment variables from project root
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.redis_bus import RedisBus
from agents.main_orchestrator import MainOrchestrator

app = FastAPI(title="Quant Agent White-box UI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_bus = RedisBus()
orchestrator = MainOrchestrator()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

class TaskRequest(BaseModel):
    prompt: str

def run_agent_workflow(task_id: str, prompt: str):
    """后台运行主编排器工作流"""
    try:
        orchestrator.run_workflow(task_id, prompt)
    except Exception as e:
        redis_bus.publish_status(task_id, f"❌ 系统致命错误: {str(e)}")

@app.post("/api/task")
async def create_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """接收用户输入，创建任务并放入后台运行"""
    task_id = f"TASK_{uuid.uuid4().hex[:8].upper()}"
    background_tasks.add_task(run_agent_workflow, task_id, request.prompt)
    return {"task_id": task_id, "status": "started"}

@app.get("/api/stream/task/{task_id}")
async def stream_task_status(task_id: str):
    """SSE 流式接口：监听 Redis Pub/Sub 并推送到前端"""
    async def event_generator():
        import redis.asyncio as aioredis
        client = aioredis.Redis(host='localhost', port=6379, decode_responses=True)
        pubsub = client.pubsub()
        channel = f"task_status:{task_id}"
        await pubsub.subscribe(channel)
        
        try:
            yield {"event": "connected", "data": json.dumps({"msg": f"已连接到总线, 任务ID: {task_id}"})}
            
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = message["data"]
                    
                    if data.startswith("FINAL_RESULT:"):
                        md_content = data.replace("FINAL_RESULT:", "")
                        yield {"event": "final_report", "data": json.dumps({"markdown": md_content})}
                        break
                        
                    yield {"event": "message", "data": json.dumps({"msg": data})}
                    
                    if data == "FINAL_REPORT_READY":
                        break
                        
        except asyncio.CancelledError:
            pass
        finally:
            await pubsub.unsubscribe(channel)
            await client.aclose()

    return EventSourceResponse(event_generator())


# ====== 同步管理 API ======
from data.sync_service import SyncService
from data.sync_scheduler import SyncScheduler
from data.watched_stocks import WatchedStocksManager

sync_service = SyncService()
sync_scheduler = SyncScheduler(sync_service)
scheduler_thread = None

def start_scheduler_background():
    """后台启动调度器"""
    global scheduler_thread
    if not sync_scheduler.is_running():
        scheduler_thread = threading.Thread(target=sync_scheduler.start, daemon=True)
        scheduler_thread.start()

class SyncTriggerRequest(BaseModel):
    tables: Optional[List[str]] = None

@app.post("/api/sync/trigger")
async def trigger_sync(request: SyncTriggerRequest = None):
    """手动触发同步"""
    try:
        tables = request.tables if request else None
        result = sync_service.trigger_sync(tables)
        return {"success": True, "data": result}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.get("/api/sync/status")
async def get_sync_status():
    """获取同步状态"""
    try:
        status = sync_service.get_status()
        status['scheduler_running'] = sync_scheduler.is_running()
        status['next_run'] = sync_scheduler.get_next_run()
        return {"success": True, "data": status}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.get("/api/sync/logs")
async def get_sync_logs(limit: int = 100):
    """获取同步日志"""
    try:
        logs = sync_service.get_logs(limit)
        return {"success": True, "data": logs}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

# ====== 关注股票管理 API ======
watched_stocks_manager = WatchedStocksManager()

@app.get("/api/stocks/watched")
async def get_watched_stocks():
    """获取关注股票列表"""
    try:
        stocks = watched_stocks_manager.get_all()
        return {"success": True, "data": stocks}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

class AddStockRequest(BaseModel):
    ticker: str
    name: Optional[str] = None

@app.post("/api/stocks/watched")
async def add_watched_stock(request: AddStockRequest):
    """添加关注股票"""
    try:
        if not request.ticker:
            return JSONResponse({"success": False, "error": "缺少 ticker"}, status_code=400)
        
        success = watched_stocks_manager.add_stock(request.ticker, request.name, 'user')
        return {"success": success}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.delete("/api/stocks/watched/{ticker}")
async def remove_watched_stock(ticker: str):
    """删除关注股票"""
    try:
        success = watched_stocks_manager.remove_stock(ticker)
        return {"success": success}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.post("/api/stocks/watched/init-hot")
async def init_hot_stocks():
    """初始化热门股票池"""
    try:
        count = watched_stocks_manager.init_hot_stocks()
        return {"success": True, "count": count}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
