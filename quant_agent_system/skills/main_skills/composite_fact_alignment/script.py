import os
import json

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    f_score = params.get("fundamental_score", 50)
    v_rating = params.get("valuation_rating", "HOLD")
    s_polarity = params.get("sentiment_polarity", 0.0)
    
    conflicts = []
    
    if f_score < 30 and v_rating == "STRONG BUY":
        conflicts.append("【高危冲突】基本面评分极低(<=30)，但估值分智能体给出了STRONG BUY。存在严重的价值陷阱风险，建议降低估值模型权重。")
        
    if f_score > 80 and v_rating in ["BUY", "STRONG BUY"] and s_polarity < -0.6:
        conflicts.append("【逻辑背离】标的基本面优秀且估值合理，但当前遭遇极端负面舆情(极性<-0.6)。需警惕黑天鹅事件导致的历史财务数据失效。")
        
    print(json.dumps({
        "is_aligned": len(conflicts) == 0,
        "conflict_warnings": conflicts,
        "alignment_score": 100 - (len(conflicts) * 30)
    }))

if __name__ == "__main__":
    main()
