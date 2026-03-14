import os, json

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    p_a = params.get("prior_prob", 0.5)
    likelihood_ratio = params.get("evidence_strength", 1.0)
    
    prior_odds = p_a / (1 - p_a + 1e-5)
    posterior_odds = prior_odds * likelihood_ratio
    
    posterior_prob = posterior_odds / (1 + posterior_odds)

    print(json.dumps({
        "prior_probability": round(p_a, 4),
        "likelihood_ratio": round(likelihood_ratio, 2),
        "posterior_probability": round(posterior_prob, 4),
        "belief_shift": round(posterior_prob - p_a, 4)
    }))

if __name__ == "__main__": main()
