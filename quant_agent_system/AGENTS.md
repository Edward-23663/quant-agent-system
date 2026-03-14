# quant_agent_system AGENTS.md

## 项目概述

quant_agent_system 是一个金融量化分析 AI Agent 系统，包含 6 个专业 Agent、5 个核心模块、30+ 技能卡带，支持 DCF/PE/PB 估值、杜邦分析、行业轮动、舆情分析、事件催化等分析功能。

## 环境要求

- Python 3.10+
- Redis (通过 docker-compose 启动)
- Node.js 18+ (前端)
- Tushare API token
- OpenAI API key

## 快速启动

```bash
cd quant_agent_system

# 1. 安装 Python 依赖
pip install -r requirements.txt

# 2. 启动 Redis (docker-compose)
docker-compose up -d

# 3. 配置环境变量
cp .env.example .env  # 编辑填入 API keys

# 4. 初始化数据库
python data/init_db.py

# 5. 启动后端 API
python web_ui/backend/api_server.py

# 6. 启动前端 (新终端)
cd web_ui/frontend && npm install && npm run dev
```

## 构建/测试命令

### Python 后端

```bash
# 运行单个测试文件
python -m pytest tests/test_llm_adapter.py -v
python -m pytest tests/test_skills/atomic_dcf_calc_test.py -v

# 运行所有测试
python -m pytest tests/ -v

# 语法检查
python -m py_compile core/llm_adapter.py
python -m py_compile agents/main_orchestrator.py

# 代码格式化 (推荐)
pip install ruff
ruff check quant_agent_system/  # Lint
ruff format quant_agent_system/  # Format

# 类型检查 (推荐)
pip install mypy
mypy quant_agent_system/core/ --ignore-missing-imports
mypy quant_agent_system/agents/ --ignore-missing-imports
```

### 前端

```bash
cd web_ui/frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build

# Lint
npm run lint

# 单文件检查
npx vue-tsc --noEmit src/components/ReportPreview.vue
```

### 数据库

```bash
# 初始化/重置数据库
python data/init_db.py

# DuckDB CLI 检查数据
duckdb data/db/quant_data.duckdb
# > SELECT * FROM financial_statements LIMIT 5;
```

## 代码风格指南

### Python (后端)

#### 导入顺序 (PEP 8)
```python
# 1. 标准库
import os
import json
import logging
from typing import Dict, Any, Optional

# 2. 第三方库
import duckdb
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI

# 3. 本地模块 (相对导入)
from core.redis_bus import RedisBus
from agents.specialized import ValuationAgent
```

#### 命名约定
- **类名**: PascalCase (`MainOrchestrator`, `LLMAdapter`)
- **函数/变量**: snake_case (`execute_task`, `db_path`)
- **常量**: UPPER_SNAKE_CASE (`MAX_RETRIES`, `DEFAULT_WACC`)
- **私有方法/变量**: 前缀 `_` (`_execute_script`, `_check_data`)

#### 类型注解
```python
from typing import Type, TypeVar, Any, Optional, Dict, List

T = TypeVar('T', bound=BaseModel)

def generate_structured(
    response_model: Type[T],
    system_prompt: str,
    user_prompt: str,
    max_retries: int = 2
) -> T:
    ...
```

#### Pydantic 模型
```python
from pydantic import BaseModel, Field

class AgentDecision(BaseModel):
    is_final_answer: bool = Field(
        ..., 
        description="如果已经收集到足够信息可以回答用户，设为 true"
    )
    skill_name: Optional[str] = Field(
        None, 
        description="要调用的技能文件夹名称"
    )
```

#### 错误处理
```python
import logging
logger = logging.getLogger(__name__)

try:
    result = db.execute(query, params).fetchone()
except duckdb.CatalogException:
    logger.warning(f"表不存在: {table}")
    return None
except Exception as e:
    logger.error(f"数据库查询失败: {e}")
    raise
```

#### 日志规范
```python
import logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("开始初始化数据库...")
logger.warning(f"缺少表 {table} 的数据")
logger.error(f"LLM 调用失败: {e}")
```

### 前端 (Vue 3 + Vite)

#### 组件结构
```vue
<template>
  <div class="component-name">
    <!-- 模板内容 -->
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { PropType } from 'vue'

interface Props {
  title: string
  data: Record<string, any>[]
}

const props = defineProps<Props>()
const isLoading = ref(false)

const filteredData = computed(() => {
  return props.data.filter(item => item.active)
})
</script>

<style scoped>
.component-name {
  /* 样式 */
}
</style>
```

## 技能卡带规范

每个技能目录必须包含 3 个文件：

```
skill_name/
├── skill.md      # 技能描述 (LLM 可见)
├── config.json    # 数据依赖声明
└── script.py     # 纯计算脚本
```

### skill.md 格式
```markdown
# 技能名称

## 功能描述
简明扼要描述此技能的功能。

## 输入参数
- `ticker`: 股票代码
- `target_date`: 目标日期

## 输出格式
返回 JSON 格式结果，包含字段说明。

## 注意事项
任何红线约束或特殊逻辑说明。
```

### config.json 格式
```json
{
  "required_data": [
    {
      "table": "financial_statements",
      "min_records": 12,
      "description": "过去3年已公告财报"
    }
  ]
}
```

### script.py 规范
```python
import os
import json
import duckdb

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params['ticker']
    
    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    
    # 红线：必须使用 announce_date <= target_date 防止前视偏差
    query = """
        SELECT * FROM table_name 
        WHERE ticker = ? AND announce_date <= ? 
        ORDER BY report_date DESC
    """
    
    result = db.execute(query, (ticker, params['target_date'])).df()
    
    # 计算逻辑...
    
    print(json.dumps({"result": value}))

if __name__ == "__main__":
    main()
```

## Redis 消息规范

- **状态发布**: `task_status:{task_id}` - Agent 执行进度
- **数据队列**: `data_fetch_queue` - 待获取数据任务
- **信号通道**: 使用 `SYSTEM_SIGNAL:DATA_READY` 表示数据就绪

## 数据库规范

- **主键**: 复合主键使用 (ticker, date) 或 (ticker, date, type)
- **索引**: 为常用查询字段创建索引
- **防前视偏差**: 所有 WHERE 条件必须包含 `announce_date <= target_date`
- **只读连接**: 读取使用 `read_only=True`

## 常见任务

### 智能体架构铁律 (必须遵守)

添加新智能体时，必须同时修改以下3个位置：

#### 1. Literal 类型约束 (main_orchestrator.py)
```python
from typing import Literal

class SubTask(BaseModel):
    target_agent: Literal[
        "industry_agent",
        "fundamental_agent",
        "valuation_agent",
        "sentiment_agent",
        "catalyst_agent",
        "comprehensive_agent",
        "risk_agent",  # 👈 新增智能体必须加这里
    ] = Field(..., description="负责处理此任务的分智能体名称标识")
```

#### 2. Agent 注册表 (main_orchestrator.py)
```python
self.agent_registry = {
    "industry_agent": IndustryAgent(),
    # ...其他智能体
    "risk_agent": RiskAgent()  # 👈 新增智能体必须加这里
}
```

#### 3. System Prompt 路由规则
在 `_plan_dag` 方法的 sys_prompt 中添加：
```
【强制路由规则】：
- 包含"关键词1"、"关键词2"、"关键词3" → 必须调用 new_agent
```

#### 为什么必须用 Literal？
- **防止漏调**: 大模型可能"忘记"调用某个智能体
- **架构级约束**: 在API层面强制限制输出选项
- **0柔性**: 自然语言Prompt易被忽略，Literal是代码级锁死

### 添加新技能
1. 在 `skills/sub_skills/{agent_name}/` 下创建目录
2. 编写 `skill.md`, `config.json`, `script.py`
3. 测试脚本: `python skills/sub_skills/{agent_name}/{skill_name}/script.py`

### 添加新 Agent
> ⚠️ **警告**: 添加新智能体时必须同时修改以下3处，否则系统无法识别！

1. 在 `agents/specialized/` 创建 `{name}_agent.py`，继承 `BaseSubAgent` 类
2. 在 `main_orchestrator.py` 的 `SubTask.target_agent` 的 `Literal` 类型中添加新智能体名称
3. 在 `main_orchestrator.py` 的 `agent_registry` 字典中注册新智能体实例
4. 在 `_plan_dag` 方法的 sys_prompt 中添加关键词路由规则

### 添加数据库表
1. 在 `data/init_db.py` 添加 CREATE TABLE 语句
2. 添加必要的索引
3. 重新运行: `python data/init_db.py`

## 注意事项

- **禁止硬编码 API Key**: 使用 `os.getenv()` 从环境变量读取
- **禁止提交 secrets**: `.env` 文件已加入 `.gitignore`
- **前视偏差红线**: 金融数据必须使用 `announce_date <= target_date` 过滤
- **长运行任务**: 使用 Redis 消息队列异步处理，避免阻塞
- **ReAct 循环步数**: 子智能体的 `execute` 方法 `max_steps` 默认值需 >= 10，确保多技能调用链完整执行（每个技能至少1步 + 最终总结1步）
