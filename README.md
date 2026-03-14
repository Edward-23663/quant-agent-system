# Quant Agent System - 金融量化分析AI Agent系统

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/AI-Agent-9%20Agents-orange.svg" alt="Agents">
</p>

## 项目简介

Quant Agent System 是一个基于大语言模型(LLM)的金融量化分析AI Agent系统，包含9大专业子智能体，支持DCF/PE/PB估值、杜邦分析、行业轮动、舆情分析、事件催化、风险测算、技术分析、商业逻辑与第一性原理分析等全面的金融分析功能。

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     Main Orchestrator                           │
│                  (主智能体编排器)                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │ Industry │ │Fundamen- │ │Valuation │ │Sentiment │         │
│  │  Agent   │ │  tal     │ │  Agent   │ │  Agent   │         │
│  │ 行业分析 │ │ 基本面   │ │ 估值分析 │ │ 舆情分析 │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                       │
│  │ Catalyst │ │Comprehen-│ │   Risk   │                       │
│  │  Agent   │ │  sive    │ │  Agent   │                       │
│  │ 事件催化 │ │ 综合模型 │ │ 风险评估 │                       │
│  └──────────┘ └──────────┘ └──────────┘                       │
├─────────────────────────────────────────────────────────────────┤
│                     Skills (30+ 技能卡带)                        │
├─────────────────────────────────────────────────────────────────┤
│  Core: LLM Adapter | Redis Bus | Vector Store | Exceptions    │
├─────────────────────────────────────────────────────────────────┤
│                     Data Layer                                  │
│         DuckDB | Tushare | AkShare | Web Scrapers              │
└─────────────────────────────────────────────────────────────────┘
```

## 9大专业智能体

| 智能体 | 职责 | 核心技能数 |
|--------|------|------------|
| **industry_agent** | 查行业地位、周期轮动 | 5 |
| **fundamental_agent** | 查财务报表、杜邦分析、盈利健康度 | 5 |
| **valuation_agent** | 算DCF、PE/PB估值、蒙特卡洛模拟 | 5 |
| **sentiment_agent** | 查新闻、测算舆情情绪极性 | 5 |
| **catalyst_agent** | 找重大事件、催化剂 | 4 |
| **comprehensive_agent** | 高阶物理/数学模型、测算Hurst分形 | 6 |
| **risk_agent** | 测算最大回撤、波动率、VaR尾部暴跌风险、止损线与仓位控制 | 5 |
| **technical_agent** | 技术指标、趋势判断、量价分析、交易计划 | 5 |
| **business_logic_agent** | 商业模式、护城河、单位经济模型、第一性原理分析 | 4 |

### 智能体详细说明

#### 1. Industry Agent (行业分析智能体)
- **职责**: 分析行业地位、周期轮动、板块轮动
- **技能**:
  - `atomic_constituents_fetch` - 获取成分股数据
  - `atomic_industry_mapping` - 行业映射
  - `atomic_trend_calc` - 趋势计算
  - `business_cost_effect` - 成本效益分析
  - `composite_rotation_cycle` - 行业轮动周期

#### 2. Fundamental Agent (基本面智能体)
- **职责**: 财务报表分析、杜邦分析、盈利健康度评估
- **技能**:
  - `atomic_financial_parsing` - 财务数据解析
  - `atomic_dupont_analysis` - 杜邦分析
  - `atomic_five_ratios` - 五大财务比率
  - `business_risk_value` - 风险价值分析
  - `composite_health_scoring` - 综合健康评分

#### 3. Valuation Agent (估值智能体)
- **职责**: DCF估值、相对估值、蒙特卡洛模拟
- **技能**:
  - `atomic_dcf_calc` - DCF现金流折现
  - `atomic_relative_val` - PE/PB历史分位数
  - `atomic_monte_carlo` - 蒙特卡洛模拟
  - `composite_cross_valid` - 多模型交叉验证
  - `business_val_range` - 估值区间计算

#### 4. Sentiment Agent (舆情智能体)
- **职责**: 新闻舆情分析、情绪极性测算
- **技能**:
  - `atomic_sentiment_scraping` - 舆情抓取
  - `atomic_polarity_scoring` - 情绪极性评分
  - `atomic_heat_calc` - 热度计算
  - `business_risk_assess` - 舆情风险评估
  - `composite_price_corr` - 价格相关性分析

#### 5. Catalyst Agent (事件催化智能体)
- **职责**: 重大事件识别、催化剂分析
- **技能**:
  - `atomic_event_scraping` - 事件抓取
  - `atomic_impact_scoring` - 影响评分
  - `business_catalyst_list` - 催化剂清单
  - `composite_event_val_corr` - 事件估值相关性

#### 6. Comprehensive Agent (综合模型智能体)
- **职责**: 高阶物理/数学模型、分形分析
- **技能**:
  - `atomic_quantum_prob` - 量子概率模型
  - `atomic_chaos_model` - 混沌模型
  - `atomic_relativity_factor` - 相对论因子
  - `atomic_bayesian_valid` - 贝叶斯验证
  - `business_nonlinear_gen` - 非线性生成
  - `composite_model_fusion` - 模型融合

#### 7. Risk Agent (风险评估智能体)
- **职责**: 风险量化、仓位控制、止损策略
- **技能**:
  - `atomic_market_risk` - 市场风险(波动率/回撤)
  - `atomic_tail_risk` - 尾部风险(VaR/CVaR)
  - `atomic_liquidity_risk` - 流动性风险
  - `composite_risk_matrix` - 多维风险矩阵
  - `business_risk_control` - 仓位控制与止损

#### 8. Technical Agent (技术分析智能体)
- **职责**: 技术指标、趋势判断、量价分析、交易计划
- **技能**:
  - `atomic_trend_indicators` - 趋势指标(MA/EMA)
  - `atomic_momentum_oscillators` - 动量震荡指标(MACD/RSI)
  - `atomic_volume_price_action` - 量价分析
  - `composite_signal_consensus` - 多指标信号共识
  - `business_trading_plan` - 交易计划与仓位建议

#### 9. Business Logic Agent (商业逻辑与第一性原理智能体)
- **职责**: 商业模式分析、护城河评估、单位经济模型
- **技能**:
  - `atomic_unit_economics` - 单位经济模型
  - `atomic_moat_extraction` - 护城河定性证据
  - `composite_first_principles` - 第一性原理分析
  - `business_model_sustainability` - 商业模式可持续性

## 技能卡带规范

每个技能目录包含3个必需文件：

```
skill_name/
├── skill.md      # 技能描述 (LLM可见)
├── config.json   # 数据依赖声明
└── script.py    # 纯计算脚本
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

## 快速开始

### 环境要求

- Python 3.10+
- Redis (通过 docker-compose 启动)
- Node.js 18+ (前端)
- Tushare API token
- OpenAI API key

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/Edward-23663/quant-agent-system.git
cd quant-agent-system/quant_agent_system

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动 Redis (docker-compose)
docker-compose up -d

# 5. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API keys

# 6. 初始化数据库
python data/init_db.py

# 7. 启动后端 API
python web_ui/backend/api_server.py

# 8. 启动前端 (新终端)
cd web_ui/frontend
npm install
npm run dev
```

### 环境变量配置 (.env)

```env
# OpenAI 配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4-turbo

# Tushare 配置 (获取token: https://tushare.pro/)
TUSHARE_TOKEN=your_tushare_token

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 数据库配置
DB_PATH=data/db/quant_data.duckdb
```

## 使用方式

### API 调用示例

```python
import requests

response = requests.post(
    "http://localhost:8000/api/analyze",
    json={
        "prompt": "分析贵州茅台(600519.SH)的投资价值",
        "ticker": "600519.SH"
    }
)

print(response.json())
```

### Web UI

访问 `http://localhost:5173` 使用可视化界面。

## 项目结构

```
quant_agent_system/
├── agents/                      # Agent模块
│   ├── main_orchestrator.py    # 主编排器
│   ├── base_sub_agent.py       # Agent基类
│   └── specialized/             # 9大专业智能体
│       ├── industry_agent.py
│       ├── fundamental_agent.py
│       ├── valuation_agent.py
│       ├── sentiment_agent.py
│       ├── catalyst_agent.py
│       ├── comprehensive_agent.py
│       ├── risk_agent.py
│       ├── technical_agent.py
│       └── business_logic_agent.py
├── core/                        # 核心模块
│   ├── llm_adapter.py          # LLM适配器
│   ├── redis_bus.py            # Redis消息总线
│   └── vector_store.py         # 向量存储
├── skills/                      # 技能卡带
│   ├── main_skills/            # 主编排器技能
│   └── sub_skills/             # 子智能体技能
│       ├── industry_agent/
│       ├── fundamental_agent/
│       ├── valuation_agent/
│       ├── sentiment_agent/
│       ├── catalyst_agent/
│       ├── comprehensive_agent/
│       ├── risk_agent/
│       ├── technical_agent/
│       └── business_logic_agent/
├── data/                        # 数据层
│   ├── init_db.py              # 数据库初始化
│   ├── workers/                # 数据获取 workers
│   └── sync_service.py         # 数据同步服务
├── web_ui/                      # Web界面
│   ├── backend/                # FastAPI后端
│   └── frontend/               # Vue3前端
└── docker-compose.yml          # Docker配置
```

## 运行测试

```bash
# 运行单个测试文件
python -m pytest tests/test_llm_adapter.py -v

# 运行所有测试
python -m pytest tests/ -v

# 语法检查
python -m py_compile core/llm_adapter.py
python -m py_compile agents/main_orchestrator.py

# 代码格式化
ruff check quant_agent_system/
ruff format quant_agent_system/
```

## 核心特性

1. **智能路由**: 基于关键词和语义理解的智能任务分发
2. **DAG任务调度**: 支持并行/串行任务编排
3. **35+技能卡带**: 覆盖估值、分析、风险、技术、商业逻辑全流程
4. **防前视偏差**: 所有金融数据使用 announce_date 过滤
5. **异步消息队列**: Redis驱动的高效任务调度
6. **可视化报告**: 自动生成Markdown/PDF分析报告

## 技术栈

- **LLM**: OpenAI GPT-4 / Claude
- **Python**: 3.10+, Pydantic, Instructor
- **数据库**: DuckDB (分析), Redis (消息队列)
- **数据源**: Tushare, AkShare
- **前端**: Vue 3, Vite, Pinia
- **后端**: FastAPI

## 注意事项

- **禁止硬编码API Key**: 使用 `os.getenv()` 从环境变量读取
- **禁止提交secrets**: `.env` 文件已加入 `.gitignore`
- **前视偏差红线**: 金融数据必须使用 `announce_date <= target_date` 过滤
- **长运行任务**: 使用Redis消息队列异步处理，避免阻塞

## License

MIT License
