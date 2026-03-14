import os
import json
import markdown
import pdfkit

pdfkit_config = pdfkit.configuration(wkhtmltopdf="/home/jianwei/miniconda3/envs/opencode1/bin/wkhtmltopdf")

def main():
    params = json.loads(os.environ.get("SKILL_PARAMS", "{}"))
    md_content = params.get("markdown_content", "")
    task_id = params.get("task_id", "report")
    
    output_dir = "data/output/reports"
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = f"{output_dir}/{task_id}_Final_Report.pdf"
    
    html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; line-height: 1.6; padding: 20px; }}
            h1 {{ color: #1a252f; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            h2 {{ color: #2c3e50; margin-top: 30px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 14px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #f4f6f9; color: #333; font-weight: bold; }}
            blockquote {{ border-left: 4px solid #e74c3c; margin: 0; padding-left: 15px; background: #fdfefe; }}
            img {{ max-width: 100%; height: auto; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    
    try:
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }
        pdfkit.from_string(html_content, pdf_path, options=options, configuration=pdfkit_config)
        
        print(json.dumps({
            "status": "success",
            "pdf_file_path": pdf_path
        }))
    except Exception as e:
        html_path = pdf_path.replace(".pdf", ".html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(json.dumps({
            "status": "degraded_to_html",
            "error": str(e),
            "html_file_path": html_path
        }))

if __name__ == "__main__":
    main()
