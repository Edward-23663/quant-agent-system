#!/bin/bash
# 启动金融量化分析系统

cd "$(dirname "$0")"

echo "=========================================="
echo "启动金融量化分析系统"
echo "=========================================="

# 初始化数据库
echo "[1/3] 初始化数据库..."
python data/init_db.py
sleep 1

# 启动后端 API
echo "[2/3] 启动后端 API..."
python -m uvicorn web_ui.backend.api_server:app --host 0.0.0.0 --port 8000 &
sleep 2

# 启动前端
echo "[3/3] 启动前端..."
cd web_ui/frontend && npm run dev &

sleep 2

echo "=========================================="
echo "系统启动完成！"
echo "=========================================="
echo "前端:   http://localhost:5173"
echo "后端:   http://localhost:8000"
echo "Redis:  localhost:6379"
echo "=========================================="
