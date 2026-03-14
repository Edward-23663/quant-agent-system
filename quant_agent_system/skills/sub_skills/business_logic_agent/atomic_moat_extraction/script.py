import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from core.vector_store import VectorStore


def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    ticker = params.get("ticker", "")

    query = f"{ticker} 核心竞争力 护城河 提价 定价权 市占率 垄断 专利 用户粘性"

    try:
        vs = VectorStore()
        results = vs.search(query=query, limit=5, where_clause=f"ticker = '{ticker}'")
    except Exception as e:
        results = []

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