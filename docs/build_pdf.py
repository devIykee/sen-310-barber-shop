"""Convert the Markdown report to a PDF, embedding the rendered SVG diagrams."""
from pathlib import Path
import markdown
from weasyprint import HTML

ROOT = Path(__file__).resolve().parent
source = (ROOT / "SEN310_Documentation.md").read_text()
body = markdown.markdown(source, extensions=["extra"])
html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: A4; margin: 18mm; }} body {{ font-family: Arial, sans-serif; font-size: 10.5pt; line-height: 1.45; color:#1f2933; }} h1 {{ color:#2e221b; border-bottom: 2px solid #c48b45; }} h2 {{ color:#493326; margin-top: 26px; }} h3 {{ color:#6b4226; }} img {{ width:100%; max-height: 160mm; object-fit:contain; page-break-inside:avoid; }} p {{ margin: 0 0 10px; }} li {{ margin-bottom:6px; }} </style></head><body>{body}</body></html>'''
HTML(string=html, base_url=str(ROOT)).write_pdf(ROOT / "SEN310_Documentation.pdf")
print(ROOT / "SEN310_Documentation.pdf")
