import subprocess
import time
import sys
import os
import signal
from data.init_db import init_database

processes = []

def signal_handler(sig, frame):
    print("\n🛑 正在关闭所有智能体微服务...")
    for p in processes:
        p.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def launch_worker(name, script_path):
    print(f"🚀 正在启动 {name}...")
    p = subprocess.Popen([sys.executable, script_path])
    processes.append(p)
    return p

def main():
    print("====================================================")
    print("🧠 金融量化分析智能体系统 (Agentic Workflow) 启动器")
    print("====================================================\n")

    print("📂 检查数据库状态...")
    init_database()

    launch_worker("独占写库守护进程 (Writer)", "data/workers/data_writer_worker.py")
    time.sleep(1)
    launch_worker("Tushare 结构化采集器", "data/workers/tushare_fetcher.py")
    launch_worker("Tavily 舆情爬虫 (国际)", "data/workers/tavily_scraper.py")
    launch_worker("Bocha 公告爬虫 (国内)", "data/workers/bocha_scraper.py")

    print("🌐 正在启动后端 API 服务 (Port: 8000)...")
    api_p = subprocess.Popen([
        "uvicorn", "web_ui.backend.api_server:app", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ])
    processes.append(api_p)

    print("\n✅ 系统已就绪！")
    print("👉 前端 UI 请在 web_ui/frontend 目录下运行: npm run dev")
    print("👉 API 文档访问: http://localhost:8000/docs")
    print("👉 Redis 监控访问: http://localhost:8001")
    print("\n按 Ctrl+C 停止所有服务...\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
