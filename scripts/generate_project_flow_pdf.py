from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parents[1]
md_path = ROOT / "documentation" / "PROJECT_FLOW_SUMMARY.md"
pdf_path = ROOT / "documentation" / "PROJECT_FLOW_SUMMARY.pdf"

text = md_path.read_text(encoding="utf-8")
lines = [line.rstrip() for line in text.splitlines()]

styles = getSampleStyleSheet()
style_title = styles["Title"]
style_h2 = styles["Heading2"]
style_body = styles["BodyText"]

story = []
for line in lines:
    if not line:
        story.append(Spacer(1, 8))
        continue

    if line.startswith("# "):
        story.append(Paragraph(line[2:].strip(), style_title))
        story.append(Spacer(1, 10))
    elif line.startswith("## "):
        story.append(Paragraph(line[3:].strip(), style_h2))
        story.append(Spacer(1, 6))
    else:
        escaped = (
            line.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        story.append(Paragraph(escaped, style_body))


doc = SimpleDocTemplate(
    str(pdf_path),
    pagesize=A4,
    rightMargin=36,
    leftMargin=36,
    topMargin=36,
    bottomMargin=36,
)
doc.build(story)

print(f"Generated: {pdf_path}")
