import os
import json
import matplotlib.pyplot as plt
import pandas as pd

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    title = params.get("title", "Financial Chart")
    chart_type = params.get("chart_type", "line")
    data = params.get("data", [])
    task_id = params.get("task_id", "default_task")
    
    if not data:
        print(json.dumps({"error": "No data provided"}))
        return
        
    output_dir = "data/output/charts"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/{task_id}_{title.replace(' ', '_')}.png"
    
    df = pd.DataFrame(data)
    
    plt.figure(figsize=(10, 5))
    plt.rcParams['font.sans-serif'] = ['SimHei'] 
    plt.rcParams['axes.unicode_minus'] = False
    
    if chart_type == "line":
        plt.plot(df['x'], df['y'], marker='o', color='#2c3e50', linewidth=2)
    else:
        plt.bar(df['x'], df['y'], color='#3498db')
        
    plt.title(title, fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig(output_path, dpi=150)
    plt.close()
    
    print(json.dumps({
        "status": "success",
        "image_path": output_path,
        "markdown_image_syntax": f"![{title}](../../{output_path})"
    }))

if __name__ == "__main__":
    main()
