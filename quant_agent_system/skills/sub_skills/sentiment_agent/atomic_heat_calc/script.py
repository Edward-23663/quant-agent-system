import os, json

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    count = params.get("retrieved_count", 0)
    polarity = params.get("average_polarity", 0.0)
    
    base_heat = min(100, count * 10) 
    
    emotion_multiplier = 1.0 + abs(polarity) * 0.5
    
    final_heat = min(100, base_heat * emotion_multiplier)
    
    heat_level = "NORMAL (平稳)"
    if final_heat > 80: heat_level = "BOILING (沸腾)"
    elif final_heat > 50: heat_level = "ACTIVE (活跃)"

    print(json.dumps({
        "heat_index_100": round(final_heat, 1),
        "heat_level": heat_level,
        "attention_advice": "舆情沸腾，请密切关注股价异动。" if final_heat > 80 else "舆情平稳。"
    }))

if __name__ == "__main__": main()
