import os
import json
import re

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    raw_events = params.get("raw_events", [])
    
    impact_dict = {
        r"扭亏为盈|重组成功|获批上市": 9,
        r"业绩大幅增长|翻倍|暴增|百亿合同": 8,
        r"超预期|上调评级|纳入指数": 6,
        r"中标|战略合作|新品发布": 5,
        r"增持|回购|股权激励": 4,
        r"政策支持|补贴|免税": 3
    }
    
    scored_events = []
    for event in raw_events:
        text = event.get("text", "")
        if not text:
            continue
        
        score = 0
        matched_tags = []
        
        for pattern, weight in impact_dict.items():
            if re.search(pattern, text):
                score = max(score, weight)
                matched_tags.append(pattern.split('|')[0])
                
        if score > 0:
            scored_events.append({
                "event_summary": text[:60] + "...",
                "impact_score": score,
                "event_type_tags": matched_tags,
                "date": event.get("date")
            })

    scored_events = sorted(scored_events, key=lambda x: x['impact_score'], reverse=True)

    print(json.dumps({
        "valid_catalysts_count": len(scored_events),
        "top_catalyst_score": scored_events[0]['impact_score'] if scored_events else 0,
        "scored_events": scored_events
    }))

if __name__ == "__main__":
    main()
