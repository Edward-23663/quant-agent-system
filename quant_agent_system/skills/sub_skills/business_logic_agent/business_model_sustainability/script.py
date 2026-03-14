import os
import json


def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    moats = params.get("first_principle_moat", ["No Moat"])
    industry = params.get("industry_level_1", "未知行业")

    disruption_risk = "MEDIUM (中等)"
    conviction = "HOLD (持有观察)"
    logic = ""

    high_disruption_sectors = ["传媒", "计算机", "通信", "商贸零售", "电子"]
    low_disruption_sectors = ["食品饮料", "煤炭", "公用事业", "医药生物", "银行"]

    if industry in high_disruption_sectors:
        if "网络效应 (Network Effect)" in moats or "无形资产 (Intangible Assets)" in moats:
            disruption_risk = "MEDIUM (中等)"
            logic = f"属于技术迭代极快的【{industry}】行业，颠覆风险本应极高，但其拥有的核心护城河提供了缓冲护垫。"
            conviction = "STRONG HOLD (坚定持有)"
        else:
            disruption_risk = "HIGH (极高)"
            logic = f"属于【{industry}】行业且缺乏核心护城河，在AI与技术浪潮下随时面临被降维打击甚至价值归零的风险。"
            conviction = "AVOID (避免长期持有)"

    elif industry in low_disruption_sectors:
        disruption_risk = "LOW (极低)"
        logic = f"属于【{industry}】行业，底层逻辑建立在人类永恒的基础需求之上，极难被新技术彻底颠覆。"
        if "无形资产 (Intangible Assets)" in moats or "成本优势 (Cost Advantage)" in moats:
            conviction = "CORE ASSET (世代传承的核心资产)"
        else:
            conviction = "HOLD (持有观察)"

    else:
        if "无宽阔护城河 (No Moat)" in moats:
            disruption_risk = "HIGH (较高)"
            conviction = "TRADE ONLY (仅适合波段交易)"
            logic = "缺乏护城河的一般性行业，容易陷入价格战泥潭，不具备穿越牛熊的长期基因。"
        else:
            disruption_risk = "LOW (较低)"
            conviction = "STRONG HOLD (坚定持有)"
            logic = "在传统行业中构建了宽阔的护城河，现金流具有较强的抗周期。"

    print(json.dumps({
        "long_term_disruption_risk": disruption_risk,
        "holding_conviction_level": conviction,
        "sustainability_insight": logic,
        "business_nature_summary": f"生意的本质：这是一家依靠【{', '.join(moats)}】在【{industry}】行业中获取超额利润的企业。"
    }))


if __name__ == "__main__":
    main()