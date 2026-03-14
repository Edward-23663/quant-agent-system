import os
import sys
import json

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.vector_store import VectorStore

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker", "")
    query = params.get("event_keywords", "业绩预增 重大合同 中标 政策利好 新品发布 战略合作")
    
    try:
        vs = VectorStore()
        results = vs.search(query=f"{ticker} {query}", limit=8, where_clause=f"ticker = '{ticker}'")
    except Exception as e:
        results = []

    if not results:
        raise ValueError(f"DATA_MISSING: 未检索到 {ticker} 的近期催化剂事件，请触发新闻/公告采集。")

    events = []
    for r in results:
        events.append({
            "text": r.get("text", ""),
            "source": r.get("source", "公告/新闻"),
            "date": r.get("date", "最新")
        })

    print(json.dumps({
        "ticker": ticker,
        "extracted_events_count": len(events),
        "raw_events": events
    }))

if __name__ == "__main__":
    main()
