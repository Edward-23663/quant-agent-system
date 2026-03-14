import os
import json

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    source_lists = params.get("source_lists", [])
    
    merged_dict = {}
    for lst in source_lists:
        for item in lst:
            key = item.get("url") or item.get("title")
            if not key:
                continue
            if key not in merged_dict:
                merged_dict[key] = item
            else:
                if item.get("date", "") > merged_dict[key].get("date", ""):
                    merged_dict[key] = item
                    
    unique_list = list(merged_dict.values())
    unique_list.sort(key=lambda x: x.get("date", "1970-01-01"), reverse=True)
    
    print(json.dumps({
        "total_unique_items": len(unique_list),
        "integrated_list": unique_list
    }))

if __name__ == "__main__":
    main()
