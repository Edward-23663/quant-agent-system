import os
import json
import duckdb
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

    recent_high = df['high_qfq'].max()
    recent_low = df['low_qfq'].min()
    pivot = (recent_high + recent_low + current_price) / 3

    r1 = (2 * pivot) - recent_low
    r2 = pivot + (recent_high - recent_low)

    s1 = (2 * pivot) - recent_high
    s2 = pivot - (recent_high - recent_low)

    action = "观望"
    entry_zone = "暂无"
    target = 0.0
    stop_loss = 0.0

    if "Buy" in consensus or "多" in consensus:
        action = "右侧建仓买入"
        entry_zone = f"{current_price} 附近，或回踩第一支撑位 {round(s1, 2)} 时介入"
        target = round(r1, 2)
        stop_loss = round(s2, 2)
    elif "Sell" in consensus or "空" in consensus:
        action = "逢高减仓/做空"
        entry_zone = f"反弹至第一阻力位 {round(r1, 2)} 附近时离场"
        target = round(s1, 2)
        stop_loss = round(r2, 2)

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


if __name__ == "__main__":
    main()