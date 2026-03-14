import os
import json

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    report_type = params.get("report_type", "deep_dive")
    full_md = params.get("full_markdown", "")
    warnings = params.get("conflict_warnings", [])
    
    final_output = ""
    
    warning_block = ""
    if warnings:
        warning_block = "## 🚨 智能体逻辑冲突警告\n" + "\n".join([f"- {w}" for w in warnings]) + "\n\n"
    
    if report_type == "deep_dive":
        final_output = warning_block + full_md
        
    elif report_type == "summary":
        summary_part = full_md.split("## 二、")[0] if "## 二、" in full_md else full_md
        final_output = "# 📄 一页纸投资简报\n\n" + warning_block + summary_part
        
    elif report_type == "risk_only":
        final_output = "# 💣 风险排雷专属报告\n\n" + warning_block
        if "## 二、" in full_md and "## 三、" in full_md:
            fundamental = full_md.split("## 二、")[1].split("## 三、")[0]
            final_output += "## 基本面风险点\n" + fundamental
            
    print(json.dumps({
        "customized_report_markdown": final_output,
        "report_type": report_type
    }))

if __name__ == "__main__":
    main()
