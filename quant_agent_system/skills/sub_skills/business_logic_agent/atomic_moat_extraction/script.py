import os
import sys
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, PROJECT_ROOT)

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker", "")
    ticker = ticker.replace(".SH", "").replace(".SZ", "").replace(".sh", "").replace(".sz", "")

    query = f"{ticker} 核心竞争力 护城河 提价 定价权 市占率 垄断 专利 用户粘性"
    results = []

    try:
        from core.vector_store import VectorStore
        vs = VectorStore()
        results = vs.search(query=query, limit=5, where_clause=f"ticker = '{ticker}'")
    except Exception as e:
        print(json.dumps({
            "ticker": ticker,
            "moat_evidence_found": False,
            "raw_evidence": [f"向量库检索失败: {str(e)}"]
        }))
        return

    if not results:
        print(json.dumps({
            "ticker": ticker,
            "moat_evidence_found": False,
            "raw_evidence": ["未能从本地知识库中检索到明显的护城河或定价权描述。"]
        }))
        return

    evidence = [r.get("text", "") for r in results]

    print(json.dumps({
        "ticker": ticker,
        "moat_evidence_found": True,
        "raw_evidence": evidence
    }))


if __name__ == "__main__":
    main()