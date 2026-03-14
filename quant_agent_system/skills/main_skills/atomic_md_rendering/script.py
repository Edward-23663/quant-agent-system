import os
import json
from jinja2 import Template

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    template_str = params.get("template_string", "")
    context = params.get("context", {})
    
    try:
        template = Template(template_str)
        rendered_md = template.render(**context)
        print(json.dumps({
            "rendered_markdown": rendered_md
        }))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
