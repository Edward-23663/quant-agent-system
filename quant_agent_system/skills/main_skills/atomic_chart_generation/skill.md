# 技能名称: atomic_chart_generation
## 功能描述
基于传入的时间序列或分类数据，使用 Matplotlib 生成本地图表，并返回图片的相对路径。
## 入参格式 (JSON)
- title (str): 图表标题
- chart_type (str): "line" 或 "bar"
- data (List[Dict]): 数据点，格式 [{"x": "2023Q1", "y": 100}, ...]
- task_id (str): 任务ID，用于命名文件
