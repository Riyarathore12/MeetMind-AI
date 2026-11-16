import io
import html
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

def report_text(title, data, transcript):
    lines = [title, "MEETMIND AI | Meeting minutes", "", "SUMMARY",
             str(data.get("summary", "")), "", "DECISIONS"]
    lines += ["- " + str(x) for x in data.get("decisions", [])]
    lines += ["", "ACTION ITEMS"]
    for item in data.get("actions", []):
        lines += [f"- {item.get('task', '')} | Owner: {item.get('owner', '')} | Deadline: {item.get('deadline', '')} | Priority: {item.get('priority', '')}",
                  "  Evidence: " + str(item.get("evidence", ""))]
    lines += ["", "OPEN QUESTIONS"] + [str(x) for x in data.get("open_questions", [])]
    lines += ["", "FOLLOW-UP EMAIL", str(data.get("follow_up_email", "")), "", "TRANSCRIPT", transcript]
    return "\n".join(lines)

def generate_pdf(text):
    buffer = io.BytesIO()
    styles = getSampleStyleSheet()
    story = [Paragraph("MeetMind AI", styles["Title"])]
    for line in text.splitlines():
        if line.strip():
            story.append(Paragraph(html.escape(line), styles["BodyText"]))
        else:
            story.append(Spacer(1, 8))
    SimpleDocTemplate(buffer, pagesize=A4).build(story)
    return buffer.getvalue()
