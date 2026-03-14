import os, json

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    hurst = params.get("hurst", 0.5)
    q_up = params.get("quantum_up_prob", 0.5)
    alpha = params.get("relative_alpha", 0.0)
    bayes = params.get("posterior_prob", 0.5)
    
    avg_prob = (q_up + bayes) / 2
    entropy = 1 - abs(avg_prob - 0.5) * 2
    
    system_state = "Unknown"
    
    if hurst > 0.6 and avg_prob > 0.6 and alpha > 0:
        system_state = "Strange Attractor (正向奇异吸引子 - 趋势自我强化)"
    elif hurst > 0.6 and avg_prob < 0.4 and alpha < 0:
        system_state = "Strange Attractor (负向奇异吸引子 - 崩盘螺旋)"
    elif hurst < 0.45:
        system_state = "Limit Cycle (极限环 - 周期性均值回归)"
    elif entropy > 0.8:
        system_state = "Bifurcation Point (混沌分叉点 - 方向即将剧变)"
    else:
        system_state = "Noise (随机噪声 - 无显著特征)"

    print(json.dumps({
        "system_entropy_score": round(entropy, 2),
        "complex_system_state": system_state,
        "fusion_bullish_confidence": round(avg_prob * 100, 1)
    }))

if __name__ == "__main__": main()
