"""Compact one-page PDF report for the High Performance Diagnostic Tool. PACE."""
from __future__ import annotations
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, Image, KeepInFrame)
from . import charts
from .config_loader import BRAND, PILLARS

NAVY = colors.HexColor("#1F3864")
GOLD = colors.HexColor("#BF9000")
GREY = colors.HexColor("#BFBFBF")
GREY_LIGHT = colors.HexColor("#F2F2F2")
RED = colors.HexColor("#C00000")
AMBER = colors.HexColor("#ED7D31")
GREEN = colors.HexColor("#548235")


def _styles():
    ss = getSampleStyleSheet()
    return {
        "h1": ParagraphStyle("H1", parent=ss["Normal"], fontName="Helvetica-Bold",
                             fontSize=15, leading=18, textColor=NAVY, spaceAfter=4),
        "h2": ParagraphStyle("H2", parent=ss["Normal"], fontName="Helvetica-Bold",
                             fontSize=9.5, leading=12, textColor=NAVY, spaceBefore=4, spaceAfter=2),
        "body": ParagraphStyle("B", parent=ss["Normal"], fontName="Helvetica",
                               fontSize=7.5, leading=9.5, alignment=TA_JUSTIFY, spaceAfter=2),
        "cell": ParagraphStyle("C", parent=ss["Normal"], fontName="Helvetica",
                               fontSize=7, leading=8.5, alignment=TA_LEFT),
        "small": ParagraphStyle("S", parent=ss["Normal"], fontName="Helvetica-Oblique",
                                fontSize=6.5, textColor=colors.HexColor("#8C8C8C")),
    }


def _frame(c, doc):
    w, h = landscape(A4)
    c.setFillColor(NAVY); c.rect(0, h - 0.75 * cm, w, 0.75 * cm, stroke=0, fill=1)
    c.setFillColor(GOLD); c.rect(0, h - 0.82 * cm, w, 0.07 * cm, stroke=0, fill=1)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 8)
    c.drawString(1.0 * cm, h - 0.52 * cm, "HIGH PERFORMANCE DIAGNOSTIC REPORT — PACE")
    c.setFont("Helvetica", 6.5)
    c.drawRightString(w - 1.0 * cm, h - 0.52 * cm, "CONFIDENTIAL")
    c.setFillColor(colors.HexColor("#8C8C8C")); c.setFont("Helvetica-Oblique", 6.5)
    c.drawString(1.0 * cm, 0.35 * cm, BRAND)


def build_pdf(analysis, cfg, output_path, prepared_by="OD — Cathay Academy", analysis_date=None):
    if analysis_date is None:
        analysis_date = datetime.now().strftime("%d %B %Y")
    styles = _styles()
    focus = analysis.focus
    pagesize = landscape(A4)
    doc = BaseDocTemplate(output_path, pagesize=pagesize,
                          leftMargin=0.9 * cm, rightMargin=0.9 * cm,
                          topMargin=1.0 * cm, bottomMargin=0.7 * cm)
    frame = Frame(0.9 * cm, 0.7 * cm, pagesize[0] - 1.8 * cm, pagesize[1] - 1.7 * cm)
    doc.addPageTemplates([PageTemplate(id="One", frames=[frame], onPage=_frame)])

    # Compact combined dashboard image
    fig = charts.one_page_dashboard(analysis, figsize=(10.5, 5.4))
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=170, bbox_inches="tight", facecolor="white")
    buf.seek(0)
    import matplotlib.pyplot as plt; plt.close(fig)

    story = []
    # Title line
    story.append(Paragraph(f"PACE Diagnostic — {focus.department}  ·  "
                            f"Overall {focus.overall:.2f}/10  ·  {focus.classification}", styles["h1"]))
    story.append(Paragraph(f"{focus.n_respondents} respondents · Company avg {analysis.company_overall:.2f} · "
                            f"{analysis_date} · Prepared by {prepared_by}", styles["small"]))
    story.append(Spacer(1, 3))

    # Dashboard image (kept compact)
    story.append(Image(buf, width=19.5 * cm, height=10.0 * cm))
    story.append(Spacer(1, 3))

    # Two columns: Polarisation & Variance | Tailored recommendations
    left = [Paragraph("Polarisation &amp; Variance Analysis", styles["h2"])]
    for pol in analysis.polarisation:
        left.append(Paragraph(f"• {pol.statement}", styles["body"]))

    right = [Paragraph("Tailored Actionable Recommendations", styles["h2"])]
    tr_rows = [["Element", "Pri.", "Recommendation"]]
    for t in analysis.tailored_recommendations:
        tr_rows.append([t["Element"], t["Priority"], Paragraph(t["Recommendation"], styles["cell"])])
    tr = Table(tr_rows, colWidths=[1.9 * cm, 1.2 * cm, 6.3 * cm])
    tr_style = [("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.3, GREY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GREY_LIGHT])]
    pri_col = {"Critical": RED, "High": AMBER, "Medium": GREEN, "Low": colors.HexColor("#8C8C8C")}
    for i in range(1, len(tr_rows)):
        pri = tr_rows[i][1]
        if pri in pri_col:
            tr_style.append(("TEXTCOLOR", (1, i), (1, i), pri_col[pri]))
            tr_style.append(("FONTNAME", (1, i), (1, i), "Helvetica-Bold"))
    tr.setStyle(TableStyle(tr_style))
    right.append(tr)

    cols = Table([[KeepInFrame(9.2 * cm, 6 * cm, left),
                   KeepInFrame(9.6 * cm, 6 * cm, right)]],
                 colWidths=[9.4 * cm, 9.8 * cm])
    cols.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                              ("LEFTPADDING", (0, 0), (-1, -1), 2),
                              ("RIGHTPADDING", (0, 0), (-1, -1), 6)]))
    story.append(cols)

    doc.build(story)
    return output_path
