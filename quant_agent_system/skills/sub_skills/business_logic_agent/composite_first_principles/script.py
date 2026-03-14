import os
import json
import re


def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    margin = params.get("gross_margin_pct", 20.0)
    driver = params.get("business_driver_hypothesis", "")
    evidence = " ".join(params.get("raw_evidence", []))

    moat_types = []
    reasoning = []

    if margin > 50 and (re.search(r"提价|品牌溢价|专利|特许经营|垄断", evidence)):
        moat_types.append("无形资产 (Intangible Assets)")
        reasoning.append("极高的毛利率配合定性证据中的提价/专利描述，证明其拥有强大的品牌溢价或技术垄断力。")

    if re.search(r"粘性|生态|替换成本|SaaS|续费率", evidence):
        moat_types.append("高转换成本 (Switching Costs)")
        reasoning.append("业务模式具有强客户粘性，客户一旦使用很难迁移到竞品。")

    if re.search(r"双边市场|平台|用户基数|马太效应|社交", evidence):
        moat_types.append("网络效应 (Network Effect)")
        reasoning.append("具备典型的平台型特征，用户越多，产品对其他用户的价值呈指数级增长。")

    if margin < 30 and re.search(r"规模效应|供应链|产能|低成本", evidence):
        moat_types.append("成本优势 (Cost Advantage)")
        reasoning.append("在相对较低的毛利下依然能存活并扩张，证明其具备极致的规模效应和供应链成本壁垒。")

    if not moat_types:
        moat_types.append("无宽阔护城河 (No Moat)")
        reasoning.append("数据与文本均未显示出难以逾越的竞争壁垒，可能处于完全竞争的红海市场。")

    print(json.dumps({
        "first_principle_moat": moat_types,
        "logical_deduction": reasoning
    }))


if __name__ == "__main__":
    main()