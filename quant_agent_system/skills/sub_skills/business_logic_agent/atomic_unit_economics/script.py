import os
import json
import duckdb


def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker")
    target_date = params.get("target_date")

    db = duckdb.connect("data/db/quant_data.duckdb", read_only=True)
    try:
        query = """
            SELECT total_revenue, gross_profit, selling_expense, rd_expense 
            FROM financial_statements 
            WHERE ticker=? AND announce_date<=? 
            ORDER BY report_date DESC LIMIT 4
        """
        df = db.execute(query, (ticker, target_date)).df()
    except Exception as e:
        raise ValueError(f"DATA_MISSING: 财报字段缺失，无法拆解单位经济模型。详细: {e}")

    if len(df) < 1:
        raise ValueError("DATA_MISSING: 无财报数据")

    rev = df['total_revenue'].mean() + 1e-5
    gross_margin = df['gross_profit'].mean() / rev
    sales_ratio = df['selling_expense'].mean() / rev
    rd_ratio = df['rd_expense'].mean() / rev

    driver = "未知驱动"
    if gross_margin > 0.5 and rd_ratio > 0.1:
        driver = "高壁垒技术驱动 (高毛利+高研发)"
    elif gross_margin > 0.5 and sales_ratio > 0.2:
        driver = "品牌与渠道驱动 (高毛利+高营销)"
    elif gross_margin < 0.2:
        driver = "规模与成本驱动 (低毛利，依赖极致供应链)"

    print(json.dumps({
        "unit_economics": {
            "gross_margin_pct": round(gross_margin * 100, 1),
            "selling_expense_ratio_pct": round(sales_ratio * 100, 1),
            "rd_expense_ratio_pct": round(rd_ratio * 100, 1)
        },
        "business_driver_hypothesis": driver
    }))


if __name__ == "__main__":
    main()