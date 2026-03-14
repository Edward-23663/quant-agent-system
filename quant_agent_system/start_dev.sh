#!/bin/bash
# 启动前后端服务

cd "$(dirname "$0")"

echo "启动后端 API..."
python -m uvicorn web_ui.backend.api_server:app --host 0.0.0.0 --port 8000 &

echo "启动前端..."
cd web_ui/frontend && npm run dev &

echo "服务已启动: 前端 http://localhost:5173, 后端 http://localhost:8000"
