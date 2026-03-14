import os, sys, json, re

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.vector_store import VectorStore

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    if len(text) > 500:
        text = text[:500] + "..."
    return text

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker", "")
    query = params.get("query", f"{ticker} 最新重大新闻")
    limit = params.get("limit", 10)

    try:
        vs = VectorStore()
        results = vs.search(query=query, limit=limit, where_clause=f"ticker = '{ticker}'")
    except Exception as e:
        results = []

    if not results:
        raise ValueError(f"DATA_MISSING: 向量库中缺乏 {ticker} 的相关新闻，请触发新闻采集。")

    news_list = []
    for r in results:
        raw_text = r.get("text", "")
        cleaned_text = clean_text(raw_text)
        if not cleaned_text:
            continue
        news_list.append({
            "text": cleaned_text,
            "source": r.get("source", "unknown"),
            "date": r.get("date", "2023-01-01")
        })

    if not news_list:
        raise ValueError(f"DATA_MISSING: 向量库中缺乏 {ticker} 的相关新闻，请触发新闻采集。")

    print(json.dumps({
        "ticker": ticker,
        "retrieved_count": len(news_list),
        "news_items": news_list
    }))

if __name__ == "__main__": main()
