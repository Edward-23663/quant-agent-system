Technical
**「技术面分析分智能体 (Technical Agent)」**。

基本面决定了“买什么”，而技术面决定了**“何时买、何时卖”**。这个智能体将化身为一位经验丰富的 CMT（注册市场技术分析师），通过纯粹的数学与统计算法（移动平均、动量震荡、量价分布）来寻找最佳的交易买卖点，并给出具体的支撑/阻力位。

---

### 🗂️ 一、 目录结构概览

```text
quant_agent_system/
├── agents/
│   └── specialized/
│       └── technical_agent.py          # 🌟 新增：技术面分析分智能体
│
└── skills/sub_skills/technical_agent/  # 🌟 新增：技术面卡带专属目录
    ├── atomic_trend_indicators/        # 原子：趋势指标 (MA均线系统, MACD, BOLL布林带)
    ├── atomic_momentum_oscillators/    # 原子：动量震荡指标 (RSI, KDJ 超买超卖)
    ├── atomic_volume_price_action/     # 原子：量价形态 (OBV能量潮, 均量线突破)
    ├── composite_signal_consensus/     # 组合：多指标信号共振与背离检测
    └── business_trading_plan/          # 业务：生成具体支撑阻力位与右侧交易计划
```

---

### 🤖 二、 智能体定义代码

在 `agents/specialized/` 目录下新建 `technical_agent.py`：

**`agents/specialized/technical_agent.py`**

```python
from agents.base_sub_agent import BaseSubAgent

class TechnicalAgent(BaseSubAgent):
    def __init__(self):
        super().__init__(
            agent_name="技术面分析分智能体",
            role_desc="你是一位顶尖的 CMT (注册市场技术分析师)。你完全不关心公司的财务和基本面，你只信仰'价格包容一切'。你通过量价关系、趋势线、动量指标 (MACD, RSI, KDJ, BOLL) 来判断资金的博弈状态，寻找最精准的右侧买卖点，并制定包含支撑位和阻力位的交易计划。",
            skills_dir="skills/sub_skills/technical_agent"
        )
```

*(记得在 `agents/specialized/__init__.py` 中导出它)*

---

### 🧱 三、 原子级 Skills (Atomic Level)

#### 1. `atomic_trend_indicators` (趋势指标: MA, MACD, BOLL)

* **`config.json`**

```json
{
  "required_data": [
    {"table": "market_daily_qfq", "min_records": 100, "description": "计算长周期均线和MACD至少需要100天数据"}
  ]
}
```

* **`skill.md`**

```markdown
# 技能名称: atomic_trend_indicators
## 功能描述
计算标的的趋势指标，包括移动平均线 (MA5/MA20/MA60) 的多空排列、MACD (平滑异同移动平均线) 的金叉死叉状态，以及 BOLL (布林带) 的轨道位置。
## 入参格式 (JSON)
- ticker (str): 股票代码
- target_date (str): 观察日期
```

* **`script.py`**

```python
import os, json, duckdb
import pandas as pd

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker")
    target_date = params.get("target_date")

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    query = "SELECT trade_date, close_qfq FROM market_daily_qfq WHERE ticker=? AND trade_date<=? ORDER BY trade_date DESC LIMIT 100"
    df = db.execute(query, (ticker, target_date)).df()
    if len(df) < 60: raise ValueError("DATA_MISSING: 行情数据不足以计算趋势指标")
    
    # 逆序转为时间正序
    df = df.iloc[::-1].reset_index(drop=True)
    close = df['close_qfq']
    current_price = close.iloc[-1]

    # 1. MA 均线系统
    ma5 = close.rolling(5).mean().iloc[-1]
    ma20 = close.rolling(20).mean().iloc[-1]
    ma60 = close.rolling(60).mean().iloc[-1]
    ma_trend = "多头排列 (Bullish)" if current_price > ma5 > ma20 > ma60 else ("空头排列 (Bearish)" if current_price < ma5 < ma20 < ma60 else "震荡交织 (Ranging)")

    # 2. MACD (12, 26, 9)
    exp1 = close.ewm(span=12, adjust=False).mean()
    exp2 = close.ewm(span=26, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line
    
    macd_status = "金叉 (Golden Cross)" if macd_line.iloc[-1] > signal_line.iloc[-1] and macd_line.iloc[-2] <= signal_line.iloc[-2] else \
                  "死叉 (Death Cross)" if macd_line.iloc[-1] < signal_line.iloc[-1] and macd_line.iloc[-2] >= signal_line.iloc[-2] else \
                  "多头区间" if histogram.iloc[-1] > 0 else "空头区间"

    # 3. BOLL 布林带 (20, 2)
    std20 = close.rolling(20).std()
    upper_band = ma20 + 2 * std20.iloc[-1]
    lower_band = ma20 - 2 * std20.iloc[-1]
    
    boll_pos = "突破上轨 (Overbought)" if current_price > upper_band else \
               "跌破下轨 (Oversold)" if current_price < lower_band else "中轨运行"

    print(json.dumps({
        "current_price": float(current_price),
        "ma_system": {"ma5": float(ma5), "ma20": float(ma20), "ma60": float(ma60), "trend": ma_trend},
        "macd_system": {"macd_val": float(macd_line.iloc[-1]), "signal_val": float(signal_line.iloc[-1]), "hist": float(histogram.iloc[-1]), "status": macd_status},
        "boll_system": {"upper": float(upper_band), "mid": float(ma20), "lower": float(lower_band), "position": boll_pos}
    }))

if __name__ == "__main__": main()
```

#### 2. `atomic_momentum_oscillators` (动量震荡指标: RSI, KDJ)

* **`config.json`**

```json
{
  "required_data": [
    {"table": "market_daily_qfq", "min_records": 60}
  ]
}
```

* **`skill.md`**

```markdown
# 技能名称: atomic_momentum_oscillators
## 功能描述
计算 RSI(14) 和 KDJ(9,3,3) 震荡指标，识别当前价格是否处于严重的超买（即将回调）或超卖（即将反弹）状态。
## 入参格式 (JSON)
- ticker (str)
- target_date (str)
```

* **`script.py`**

```python
import os, json, duckdb
import pandas as pd

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker")
    target_date = params.get("target_date")

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    query = "SELECT trade_date, high_qfq, low_qfq, close_qfq FROM market_daily_qfq WHERE ticker=? AND trade_date<=? ORDER BY trade_date DESC LIMIT 60"
    df = db.execute(query, (ticker, target_date)).df()
    if len(df) < 30: raise ValueError("DATA_MISSING: 数据不足计算RSI/KDJ")
    
    df = df.iloc[::-1].reset_index(drop=True)
    
    # 1. RSI (14)
    delta = df['close_qfq'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-5)
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1]
    
    rsi_status = "超卖 (Oversold)" if current_rsi < 30 else ("超买 (Overbought)" if current_rsi > 70 else "中性 (Neutral)")

    # 2. KDJ (9, 3, 3)
    low_min = df['low_qfq'].rolling(9).min()
    high_max = df['high_qfq'].rolling(9).max()
    rsv = (df['close_qfq'] - low_min) / (high_max - low_min + 1e-5) * 100
    k = rsv.ewm(com=2, adjust=False).mean()
    d = k.ewm(com=2, adjust=False).mean()
    j = 3 * k - 2 * d
    
    current_k, current_d, current_j = k.iloc[-1], d.iloc[-1], j.iloc[-1]
    
    kdj_cross = "金叉 (Golden Cross)" if current_k > current_d and k.iloc[-2] <= d.iloc[-2] else \
                "死叉 (Death Cross)" if current_k < current_d and k.iloc[-2] >= d.iloc[-2] else "无交叉"

    print(json.dumps({
        "RSI_14": {"value": round(float(current_rsi), 1), "status": rsi_status},
        "KDJ_9_3_3": {"K": round(float(current_k), 1), "D": round(float(current_d), 1), "J": round(float(current_j), 1), "cross_signal": kdj_cross}
    }))

if __name__ == "__main__": main()
```

#### 3. `atomic_volume_price_action` (量价形态: OBV, 均量线)

* **`config.json`**

```json
{
  "required_data": [
    {"table": "market_daily_qfq", "min_records": 60}
  ]
}
```

* **`skill.md`**

```markdown
# 技能名称: atomic_volume_price_action
## 功能描述
分析成交量与价格的配合关系。计算 OBV (能量潮指标) 判断资金是在潜伏吸筹还是在派发，以及成交量是否出现异动（放量突破/缩量企稳）。
## 入参格式 (JSON)
- ticker (str)
- target_date (str)
```

* **`script.py`**

```python
import os, json, duckdb
import numpy as np

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker")
    target_date = params.get("target_date")

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    query = "SELECT close_qfq, volume FROM market_daily_qfq WHERE ticker=? AND trade_date<=? ORDER BY trade_date DESC LIMIT 60"
    df = db.execute(query, (ticker, target_date)).df()
    if len(df) < 20: raise ValueError("DATA_MISSING: 缺乏成交量数据")
    
    df = df.iloc[::-1].reset_index(drop=True)
    
    # 1. 均量线异动分析
    vol_5 = df['volume'].rolling(5).mean().iloc[-1]
    vol_20 = df['volume'].rolling(20).mean().iloc[-1]
    current_vol = df['volume'].iloc[-1]
    
    vol_status = "放量 (Volume Expansion)" if current_vol > vol_20 * 1.5 else \
                 "缩量 (Volume Shrinkage)" if current_vol < vol_20 * 0.6 else "平量"

    # 2. OBV (On Balance Volume) 能量潮
    obv = [0]
    for i in range(1, len(df)):
        if df['close_qfq'].iloc[i] > df['close_qfq'].iloc[i-1]:
            obv.append(obv[-1] + df['volume'].iloc[i])
        elif df['close_qfq'].iloc[i] < df['close_qfq'].iloc[i-1]:
            obv.append(obv[-1] - df['volume'].iloc[i])
        else:
            obv.append(obv[-1])
            
    obv_series = pd.Series(obv)
    obv_ma10 = obv_series.rolling(10).mean().iloc[-1]
    
    obv_trend = "资金流入 (Accumulation)" if obv_series.iloc[-1] > obv_ma10 else "资金流出 (Distribution)"

    print(json.dumps({
        "volume_action": {"current_vol": float(current_vol), "vol_ma20": float(vol_20), "status": vol_status},
        "OBV_indicator": {"trend": obv_trend, "logic": "OBV线上穿均线代表买盘力量强于卖盘。"}
    }))

if __name__ == "__main__": main()
```

---

### 🧬 四、 组合级 Skills (Composite Level)

#### 4. `composite_signal_consensus` (多指标信号共振与背离)

* **`config.json`**

```json
{ "required_data": [] }
```

* **`skill.md`**

```markdown
# 技能名称: composite_signal_consensus
## 功能描述
汇总趋势 (MA/MACD)、动量 (RSI/KDJ) 和量价 (OBV) 的底层信号，通过规则引擎检测指标之间是否产生“共振 (Consensus)”或“背离 (Divergence)”。
## 入参格式 (JSON)
- ma_trend (str): MA趋势状态
- macd_status (str): MACD状态
- rsi_status (str): RSI状态
- kdj_cross (str): KDJ交叉信号
- vol_status (str): 成交量状态
- obv_trend (str): OBV资金趋势
```

* **`script.py`**

```python
import os, json

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ma = params.get("ma_trend", "")
    macd = params.get("macd_status", "")
    rsi = params.get("rsi_status", "")
    kdj = params.get("kdj_cross", "")
    vol = params.get("vol_status", "")
    obv = params.get("obv_trend", "")

    bullish_score = 0
    bearish_score = 0
    divergence_warnings = []

    # 1. 趋势得分
    if "Bullish" in ma or "多头" in ma: bullish_score += 2
    if "Bearish" in ma or "空头" in ma: bearish_score += 2
    if "Golden" in macd or "金叉" in macd: bullish_score += 2
    if "Death" in macd or "死叉" in macd: bearish_score += 2

    # 2. 动量得分
    if "Oversold" in rsi or "超卖" in rsi: bullish_score += 1
    if "Overbought" in rsi or "超买" in rsi: bearish_score += 1
    if "Golden" in kdj or "金叉" in kdj: bullish_score += 1
    if "Death" in kdj or "死叉" in kdj: bearish_score += 1

    # 3. 量价得分
    if "Accumulation" in obv: bullish_score += 1
    if "Distribution" in obv: bearish_score += 1

    # 4. 背离检测 (致命信号)
    if ("Bullish" in ma or "多头" in ma) and "Distribution" in obv:
        divergence_warnings.append("【顶背离警告】：价格维持多头趋势，但OBV显示资金正在暗中撤退 (量价背离)。")
    if ("Bearish" in ma or "空头" in ma) and "Accumulation" in obv:
        divergence_warnings.append("【底背离信号】：价格处于下跌趋势，但OBV显示资金正在低位暗中吸筹。")
    if "Bullish" in ma and ("Overbought" in rsi or "超买" in rsi):
        divergence_warnings.append("【回调预警】：右侧趋势极强，但RSI显示严重超买，短期随时可能面临技术性回调。")

    # 综合研判
    consensus = "震荡无方向 (Neutral)"
    if bullish_score >= 5 and bearish_score <= 1:
        consensus = "强烈看多 (Strong Buy - 指标共振)"
    elif bearish_score >= 5 and bullish_score <= 1:
        consensus = "强烈看空 (Strong Sell - 指标共振)"
    elif bullish_score > bearish_score:
        consensus = "偏多 (Bullish Bias)"
    elif bearish_score > bullish_score:
        consensus = "偏空 (Bearish Bias)"

    print(json.dumps({
        "bullish_signals_count": bullish_score,
        "bearish_signals_count": bearish_score,
        "technical_consensus": consensus,
        "divergence_warnings": divergence_warnings
    }))

if __name__ == "__main__": main()
```

---

### 🎯 五、 业务级 Skills (Business Level)

#### 5. `business_trading_plan` (生成具体支撑阻力位与交易计划)

* **`config.json`**

```json
{
  "required_data": [
    {"table": "market_daily_qfq", "min_records": 120, "description": "计算支撑阻力位需要半年数据"}
  ]
}
```

* **`skill.md`**

```markdown
# 技能名称: business_trading_plan
## 功能描述
通过寻找过去半年的局部高低点和密集成交区，计算出绝对的“第一支撑位”、“第一阻力位”。结合技术共振信号，输出一份包含入场点、目标价和严格止损价的实战交易计划。
## 入参格式 (JSON)
- ticker (str)
- target_date (str)
- technical_consensus (str): 技术面共振结论
- current_price (float): 当前股价 (从原子技能传入)
```

* **`script.py`**

```python
import os, json, duckdb
import pandas as pd

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker")
    target_date = params.get("target_date")
    consensus = params.get("technical_consensus", "Neutral")
    current_price = params.get("current_price", 0.0)

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    query = "SELECT high_qfq, low_qfq, close_qfq FROM market_daily_qfq WHERE ticker=? AND trade_date<=? ORDER BY trade_date DESC LIMIT 120"
    df = db.execute(query, (ticker, target_date)).df()
    
    if len(df) < 60 or current_price == 0:
        raise ValueError("DATA_MISSING: 数据不足，无法制定交易计划")
        
    # 简单的支撑阻力位计算：寻找近半年最高点、最低点和中枢
    recent_high = df['high_qfq'].max()
    recent_low = df['low_qfq'].min()
    pivot = (recent_high + recent_low + current_price) / 3
    
    # 阻力位 (Resistance)
    r1 = (2 * pivot) - recent_low
    r2 = pivot + (recent_high - recent_low)
    
    # 支撑位 (Support)
    s1 = (2 * pivot) - recent_high
    s2 = pivot - (recent_high - recent_low)
    
    # 制定右侧交易计划
    action = "观望"
    entry_zone = f"暂无"
    target = 0.0
    stop_loss = 0.0
    
    if "Buy" in consensus or "多" in consensus:
        action = "右侧建仓买入"
        entry_zone = f"{current_price} 附近，或回踩第一支撑位 {round(s1, 2)} 时介入"
        target = round(r1, 2)
        stop_loss = round(s2, 2) # 跌破第二支撑位无条件止损
    elif "Sell" in consensus or "空" in consensus:
        action = "逢高减仓/做空"
        entry_zone = f"反弹至第一阻力位 {round(r1, 2)} 附近时离场"
        target = round(s1, 2)
        stop_loss = round(r2, 2) # 突破第二阻力位认错止损

    # 计算盈亏比 (Reward/Risk Ratio)
    if action == "右侧建仓买入" and (current_price - stop_loss) > 0:
        rr_ratio = (target - current_price) / (current_price - stop_loss)
    else:
        rr_ratio = 0.0

    print(json.dumps({
        "key_levels": {
            "resistance_1": round(r1, 2),
            "resistance_2": round(r2, 2),
            "support_1": round(s1, 2),
            "support_2": round(s2, 2)
        },
        "trading_plan": {
            "strategy": action,
            "entry_zone": entry_zone,
            "target_price": target,
            "stop_loss_price": stop_loss,
            "reward_risk_ratio": round(rr_ratio, 2)
        },
        "execution_advice": f"当前技术面共振信号为【{consensus}】。如果执行买入，预期盈亏比为 {round(rr_ratio, 2)}。请严格遵守 {round(stop_loss, 2)} 的止损纪律！"
    }))

if __name__ == "__main__": main()
```

---

### 🚀 六、 如何将它无缝接入系统？

同样，仅需 **2 步**，系统就会拥有这个强大的技术面分析师。

**步骤 1：在主编排器中导入并注册它**
打开 `agents/main_orchestrator.py`：

```python
# 1. 导入
from agents.specialized.technical_agent import TechnicalAgent

# 2. 在 __init__ 的 agent_registry 中注册
self.agent_registry = {
    # ... 其他 agent ...
    "risk_agent": RiskAgent(),
    "technical_agent": TechnicalAgent()  # 👈 新增这行
}
```

**步骤 2：使用 Pydantic Literal 锁死路由 (极其重要)**
在同一个文件 `main_orchestrator.py` 中，更新 `SubTask` 的定义和 `sys_prompt`：

```python
class SubTask(BaseModel):
    target_agent: Literal[
        "industry_agent",
        "fundamental_agent",
        "valuation_agent",
        "sentiment_agent",
        "catalyst_agent",
        "comprehensive_agent",
        "risk_agent",
        "technical_agent"  # 👈 必须在这里加上，防止大模型遗忘
    ] = Field(..., description="负责处理此任务的分智能体名称标识")

# ... 在 _plan_dag 的 sys_prompt 中加入说明 ...
"""
8. technical_agent: 查技术面、量价背离、均线/MACD/KDJ指标、找支撑阻力位与买卖点。

【强制路由规则】：
- 如果用户提到“技术面”、“买卖点”、“支撑位”、“阻力位”、“均线”、“MACD”、“放量/缩量”等字眼，你【必须】生成一个 target_agent 为 'technical_agent' 的子任务！
"""
```

### 💡 架构师实战演示

现在，当你在前端输入：

> **“基本面我看过了，帮我看看比亚迪(002594.SZ)现在的技术面怎么样？MACD和KDJ有共振吗？给我具体的买入点和止损位。”**

系统流转将如下：

1. 主编排器精准把任务丢给 `TechnicalAgent`。
2. 它先跑 `atomic_trend_indicators`，算出均线多头排列，MACD金叉。
3. 它跑 `atomic_momentum_oscillators`，算出 KDJ 同样金叉，但 RSI 有点超买。
4. 它跑 `composite_signal_consensus`，发现量价配合良好，得出结论 **“强烈看多 (Strong Buy - 指标共振)”**。
5. 最后跑 `business_trading_plan`，精准算出**第一支撑位 250.5，阻力位 280**，并生成一份盈亏比极佳的右侧交易计划，最终排版成 Markdown 返回给你！

