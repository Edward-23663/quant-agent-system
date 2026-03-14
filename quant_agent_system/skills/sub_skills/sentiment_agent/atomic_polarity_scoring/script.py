import os, json
try:
    from snownlp import SnowNLP
except ImportError:
    SnowNLP = None

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    news_items = params.get("news_items", [])
    
    if not news_items:
        print(json.dumps({"error": "No news items provided"}))
        return

    total_polarity = 0
    scored_items = []
    
    for item in news_items:
        text = item.get("text", "")
        if not text: continue
        
        if SnowNLP:
            s = SnowNLP(text)
            polarity = (s.sentiments - 0.5) * 2
        else:
            pos_words = ['增长', '突破', '利好', '增持', '大涨', '创新高']
            neg_words = ['下滑', '跌', '亏损', '减持', '造假', '立案', '暴跌']
            pos_count = sum(1 for w in pos_words if w in text)
            neg_count = sum(1 for w in neg_words if w in text)
            polarity = (pos_count - neg_count) / (pos_count + neg_count + 1e-5)
            polarity = max(-1.0, min(1.0, polarity))

        total_polarity += polarity
        scored_items.append({"text": text[:50] + "...", "polarity": round(polarity, 3)})

    avg_polarity = total_polarity / len(scored_items) if scored_items else 0

    print(json.dumps({
        "average_polarity": round(avg_polarity, 3),
        "sentiment_label": "POSITIVE" if avg_polarity > 0.2 else ("NEGATIVE" if avg_polarity < -0.2 else "NEUTRAL"),
        "scored_details": scored_items
    }))

if __name__ == "__main__": main()
