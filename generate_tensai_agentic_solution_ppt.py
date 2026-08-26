"""
Tensai Agentic Solution — Complete 15-slide business + technical deck
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

OUTPUT = r"c:\Users\KulkarS4.EU\Documents\portfolio-web\BOS_BAU\Tensai_Agentic_Solution.pptx"

NAVY   = RGBColor(0x0B, 0x1F, 0x3A)
TEAL   = RGBColor(0x00, 0x96, 0x88)
SLATE  = RGBColor(0x45, 0x55, 0x64)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT  = RGBColor(0xF1, 0xF5, 0xF9)
ACCENT = RGBColor(0x1E, 0x40, 0xAF)
GREEN  = RGBColor(0x05, 0x96, 0x69)
AMBER  = RGBColor(0xD9, 0x77, 0x06)
BORDER = RGBColor(0xE2, 0xE8, 0xF0)
LBLUE  = RGBColor(0xBF, 0xDB, 0xFE)


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def bg(slide, color=LIGHT):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def bar(slide, title, sub=None):
    r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(10), Inches(0.95))
    r.fill.solid(); r.fill.fore_color.rgb = NAVY; r.line.fill.background()
    t = slide.shapes.add_textbox(Inches(0.45), Inches(0.12), Inches(9.1), Inches(0.5))
    p = t.text_frame.paragraphs[0]
    p.text = title; p.font.size = Pt(23); p.font.bold = True; p.font.color.rgb = WHITE
    if sub:
        s = slide.shapes.add_textbox(Inches(0.45), Inches(0.55), Inches(9.1), Inches(0.32))
        sp = s.text_frame.paragraphs[0]
        sp.text = sub; sp.font.size = Pt(10); sp.font.color.rgb = LBLUE


def bullets(slide, items, left=0.48, top=1.12, w=9.05, h=5.95, sz=13, col=SLATE, gap=7):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(w), Inches(h))
    tf = box.text_frame; tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = item if item[:1] in "•→✓" else f"• {item}"
        p.font.size = Pt(sz); p.font.color.rgb = col; p.space_after = Pt(gap)


def cols(slide, lt, li, rt, ri, top=1.12, sz=12):
    for title, items, left in [(lt, li, 0.48), (rt, ri, 5.05)]:
        tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(4.45), Inches(0.32))
        p = tb.text_frame.paragraphs[0]
        p.text = title; p.font.bold = True; p.font.size = Pt(15); p.font.color.rgb = ACCENT
        bullets(slide, items, left=left, top=top + 0.38, w=4.45, h=5.6, sz=sz)


def box(slide, text, l, t, w=1.55, h=0.48, fill=NAVY, fsize=9, bold=True):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = fill; s.line.color.rgb = fill
    tf = s.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = text
    p.font.size = Pt(fsize); p.font.bold = bold; p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER; tf.vertical_anchor = MSO_ANCHOR.MIDDLE


def arrow(slide, l, t, down=False):
    kind = MSO_SHAPE.DOWN_ARROW if down else MSO_SHAPE.RIGHT_ARROW
    w, h = (0.22, 0.26) if down else (0.28, 0.16)
    a = slide.shapes.add_shape(kind, Inches(l), Inches(t), Inches(w), Inches(h))
    a.fill.solid(); a.fill.fore_color.rgb = TEAL; a.line.fill.background()


def kpi_card(slide, label, value, l, t, color=NAVY):
    c = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(2.05), Inches(0.88))
    c.fill.solid(); c.fill.fore_color.rgb = WHITE; c.line.color.rgb = BORDER
    tb = slide.shapes.add_textbox(Inches(l + 0.1), Inches(t + 0.08), Inches(1.85), Inches(0.72))
    tf = tb.text_frame
    p1 = tf.paragraphs[0]; p1.text = label; p1.font.size = Pt(9); p1.font.color.rgb = SLATE
    p2 = tf.add_paragraph(); p2.text = value; p2.font.size = Pt(20); p2.font.bold = True; p2.font.color.rgb = color


def add_bar_chart(slide, l, t, w, h, categories, values, title):
    data = CategoryChartData()
    data.categories = categories
    data.add_series(title, values)
    cf = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(l), Inches(t), Inches(w), Inches(h), data)
    chart = cf.chart
    chart.has_legend = False
    chart.value_axis.has_major_gridlines = True
    if chart.series:
        chart.series[0].format.fill.solid()
        chart.series[0].format.fill.fore_color.rgb = TEAL


def add_pie_chart(slide, l, t, w, h, categories, values, title):
    data = CategoryChartData()
    data.categories = categories
    data.add_series(title, values)
    cf = slide.shapes.add_chart(XL_CHART_TYPE.PIE, Inches(l), Inches(t), Inches(w), Inches(h), data)
    chart = cf.chart
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.BOTTOM
    chart.legend.include_in_layout = False


def arch_diagram(slide):
    layers = [
        (ACCENT, "UI Layer",          "Simple Ops Portal — Incident List | Detail | Approve"),
        (TEAL,   "Agent Layer",       "Triage → Correlate → Recommend → Act → Audit"),
        (NAVY,   "Orchestration",     "Azure Functions | Event Grid | Policy Engine"),
        (RGBColor(0x37,0x47,0x5A), "Integration", "ELK/Kibana | ServiceNow | Azure AKS | Teams"),
        (RGBColor(0x64,0x74,0x8B), "SecureBank", "Banking App | DB | Cache | Safe Telemetry"),
    ]
    y = 1.18
    for color, name, desc in layers:
        box(slide, name, 0.48, y, w=1.85, h=0.44, fill=color, fsize=8)
        tb = slide.shapes.add_textbox(Inches(2.45), Inches(y + 0.04), Inches(7.05), Inches(0.38))
        p = tb.text_frame.paragraphs[0]; p.text = desc; p.font.size = Pt(11); p.font.color.rgb = SLATE
        if y < 4.85:
            arrow(slide, 1.28, y + 0.46, down=True)
        y += 0.72


def flow_diagram(slide, top=1.15):
    steps = ["ELK\nAlert", "Azure\nWebhook", "Agent\nAnalysis", "SNOW\nTicket", "Approve\nFix", "Audit\nLog"]
    for i, s in enumerate(steps):
        box(slide, s, 0.42 + i * 1.52, top, w=1.28, h=0.62, fill=NAVY if i % 2 == 0 else TEAL, fsize=8)
        if i < len(steps) - 1:
            arrow(slide, 1.65 + i * 1.52, top + 0.24)


def offer_table(slide):
    """Visual offer table using shapes"""
    headers = ["What We Offer", "How It Helps", "Phase"]
    rows = [
        ("Auto Incident Triage", "Reads ELK alerts, finds root cause fast", "Phase 1"),
        ("Smart SNOW Tickets", "Creates enriched tickets — no manual copy-paste", "Phase 1"),
        ("Guided Remediation", "One-click approved fix for common failures", "Phase 1"),
        ("Security Response", "Handles login spikes and suspicious access", "Phase 1"),
        ("Simple Ops Portal", "3-screen UI — list, detail, approve", "Phase 1"),
        ("Extensible Platform", "Add new problems & tools without rebuild", "Phase 2"),
    ]
    # header row
    for j, h in enumerate(headers):
        l = 0.48 + j * 3.05
        cell = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(l), Inches(1.15), Inches(2.95), Inches(0.38))
        cell.fill.solid(); cell.fill.fore_color.rgb = NAVY; cell.line.color.rgb = NAVY
        tb = slide.shapes.add_textbox(Inches(l + 0.06), Inches(1.18), Inches(2.82), Inches(0.3))
        p = tb.text_frame.paragraphs[0]; p.text = h; p.font.size = Pt(10); p.font.bold = True
        p.font.color.rgb = WHITE; p.alignment = PP_ALIGN.CENTER
    for i, row in enumerate(rows):
        y = 1.58 + i * 0.52
        for j, val in enumerate(row):
            l = 0.48 + j * 3.05
            fill = WHITE if i % 2 == 0 else LIGHT
            cell = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(l), Inches(y), Inches(2.95), Inches(0.48))
            cell.fill.solid(); cell.fill.fore_color.rgb = fill; cell.line.color.rgb = BORDER
            tb = slide.shapes.add_textbox(Inches(l + 0.06), Inches(y + 0.06), Inches(2.82), Inches(0.36))
            p = tb.text_frame.paragraphs[0]; p.text = val; p.font.size = Pt(9); p.font.color.rgb = SLATE


def main():
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    # ── 1 TITLE ─────────────────────────────────────────────────────
    s = blank(prs); bg(s, NAVY)
    t = s.shapes.add_textbox(Inches(0.6), Inches(1.55), Inches(8.8), Inches(1.0))
    p = t.text_frame.paragraphs[0]
    p.text = "TENSAI AGENTIC SOLUTION"; p.font.size = Pt(40); p.font.bold = True; p.font.color.rgb = WHITE
    sub = s.shapes.add_textbox(Inches(0.6), Inches(2.65), Inches(8.8), Inches(0.65))
    sp = sub.text_frame.paragraphs[0]
    sp.text = "SecureBank AIR — Intelligent Incident Response Platform"
    sp.font.size = Pt(20); sp.font.color.rgb = LBLUE
    tag = s.shapes.add_textbox(Inches(0.6), Inches(3.55), Inches(8.8), Inches(1.6))
    tp = tag.text_frame.paragraphs[0]
    tp.text = (
        "Detect  →  Diagnose  →  Ticket  →  Fix  →  Audit\n"
        "Built on: SecureBank  |  ELK/Kibana  |  ServiceNow  |  Azure\n"
        "Phase 1: 3 critical problems  •  Simple UI  •  Real, feasible, production-ready path"
    )
    tp.font.size = Pt(13); tp.font.color.rgb = RGBColor(0xCB, 0xD5, 0xE1)

    # ── 2 EXECUTIVE SUMMARY ─────────────────────────────────────────
    s = blank(prs); bg(s); bar(s, "1. Executive Summary — What We Offer")
    kpi_card(s, "MTTR Target", "↓ 70%", 0.48, 1.12, GREEN)
    kpi_card(s, "Manual Toil", "↓ 40%", 2.65, 1.12, TEAL)
    kpi_card(s, "Phase 1 Scope", "3 Problems", 4.82, 1.12, ACCENT)
    kpi_card(s, "Go-Live", "~8 Weeks", 6.99, 1.12, AMBER)
    bullets(s, [
        "Tensai Agentic Solution connects your existing ELK observability and ServiceNow ITSM with a smart automation layer on Azure.",
        "When something breaks in SecureBank (transfer failures, login spikes, service down), the system automatically finds the cause, creates a ticket, and lets an engineer approve a fix in one click.",
        "No rip-and-replace — we use what you already have and add intelligence on top.",
        "Phase 1 proves value on 3 real banking scenarios. Phase 2 extends to more problems and systems on the same platform.",
        "Simple 3-screen UI — no complex dashboards. Built for NOC and SRE teams who need speed, not clutter.",
    ], top=2.2, sz=13)

    # ── 3 PROBLEM STATEMENT ─────────────────────────────────────────
    s = blank(prs); bg(s); bar(s, "2. Problem Statement", "Why banks need this — simple pain points")
    cols(s,
        "What Happens Today",
        [
            "ELK/Kibana detects problems but cannot fix them.",
            "Engineers manually search logs, traces, and dashboards.",
            "ServiceNow tickets are created by hand — missing context.",
            "Same issues repeat: DB pool full, API 5xx, login fraud spikes.",
            "MTTR averages 45–90 minutes per incident.",
            "No single audit trail linking detection → action → resolution.",
        ],
        "Business Impact",
        [
            "Transfer/payment downtime = SLA penalties + unhappy customers.",
            "Engineer time wasted on repeat manual work = high OpEx.",
            "Slow security response on login anomalies = fraud risk.",
            "Leadership cannot see automation ROI clearly.",
            "Each new monitoring tool adds cost but not connected value.",
            "Regulators expect proof of every action — manual reports take days.",
        ])

    # ── 4 OUR SOLUTION ──────────────────────────────────────────────
    s = blank(prs); bg(s); bar(s, "3. Our Solution — Tensai Agentic Platform")
    bullets(s, [
        "A lightweight Azure automation layer that sits between ELK (eyes) and ServiceNow (tracking) and adds hands (remediation).",
        "Multi-step agent workflow: receive alert → analyze in ELK → explain root cause → create SNOW ticket → recommend fix → execute after approval → log audit.",
        "Built specifically for SecureBank digital banking — safe telemetry, no customer PII in logs or agent output.",
        "Policy-controlled: low-risk actions can auto-run; high-risk fixes need one-click human approval.",
        "Platform is extensible — Phase 1 solves 3 problems; Phase 2 adds more without rebuilding.",
        "Simple React portal — engineers see incidents, read plain-English diagnosis, click Approve. Done.",
    ], sz=13)

    # ── 5 WHAT WE OFFER (TABLE) ─────────────────────────────────────
    s = blank(prs); bg(s); bar(s, "4. What We Offer — Product & Value Table")
    offer_table(s)
    bullets(s, [
        "Every row is a deliverable in Phase 1 except the extensible platform row (Phase 2 foundation built in Phase 1).",
    ], top=4.75, sz=11)

    # ── 6 PHASE 1 — 3 PROBLEMS ──────────────────────────────────────
    s = blank(prs); bg(s); bar(s, "5. Phase 1 Scope — 3 Problems We Solve First", "Directly mapped from SecureBank ELK alert scenarios")
    problems = [
        ("P1", "Transfer Service\nFailure", "5xx errors +\nDB pool full", "Scale pool,\nrestart pods", NAVY),
        ("P2", "Login / Security\nSpike", "Failed logins\n10x normal", "SNOW SecOps\nticket + alert", TEAL),
        ("P3", "Service\nUnavailable", "Auth/API\ndown", "Restart AKS\npod", ACCENT),
    ]
    for i, (tag, title, trigger, action, color) in enumerate(problems):
        l = 0.55 + i * 3.1
        box(s, tag, l, 1.15, w=0.7, h=0.38, fill=color, fsize=10)
        card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(1.6), Inches(2.85), Inches(2.0))
        card.fill.solid(); card.fill.fore_color.rgb = WHITE; card.line.color.rgb = BORDER
        tb = s.shapes.add_textbox(Inches(l + 0.12), Inches(1.72), Inches(2.6), Inches(1.75))
        tf = tb.text_frame; tf.word_wrap = True
        lines = [title, "", "Trigger:", trigger, "", "Fix:", action]
        for j, line in enumerate(lines):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.text = line; p.font.size = Pt(10 if j > 0 else 12)
            p.font.bold = j in (0, 2, 5); p.font.color.rgb = SLATE if j not in (0,) else color
    bullets(s, [
        "All 3 scenarios already exist in SecureBank ELK reference alerts — we automate the response, not the detection.",
        "Phase 2 adds: latency tuning, change intelligence, capacity ops, compliance reports, more tool adapters.",
    ], top=3.85, sz=12)

    # ── 7 ARCHITECTURE ──────────────────────────────────────────────
    s = blank(prs); bg(s); bar(s, "6. Solution Architecture — How We Achieve It")
    arch_diagram(s)
    bullets(s, ["Each layer is independent — extend agents, add integrations, or upgrade UI without rebuilding."], top=5.35, sz=11)

    # ── 8 HOW IT WORKS ──────────────────────────────────────────────
    s = blank(prs); bg(s); bar(s, "7. How It Works — End-to-End Flow")
    flow_diagram(s, top=1.12)
    cols(s,
        "Step-by-Step (Simple)",
        [
            "1. Kibana rule fires (e.g., transfer 5xx + DB pool high).",
            "2. Webhook hits Azure Function via Event Grid.",
            "3. Agent queries ELK logs/traces → finds root cause.",
            "4. ServiceNow incident auto-created with context + link.",
            "5. Engineer opens portal → reads diagnosis → clicks Approve.",
            "6. Fix runs on Azure AKS → ELK confirms recovery → ticket closed.",
            "7. Audit log saved automatically.",
        ],
        "Example: Transfer Failure",
        [
            "Alert: Transfer API 5xx rate 8%, DB pool 98%.",
            "Agent: 'DB connection pool exhausted.'",
            "SNOW: SEV-2 → Digital Banking SRE group.",
            "Fix: Increase pool 50→80, rolling pod restart.",
            "Result: Transfers restored in ~12 minutes.",
            "Before AIR: ~75 minutes manual effort.",
            "Audit: Full timeline stored in Azure Blob.",
        ], top=1.95, sz=11)

    # ── 9 TECH STACK ─────────────────────────────────────────────────
    s = blank(prs); bg(s); bar(s, "8. Technology Stack — How We Will Build It")
    cols(s,
        "Core Components",
        [
            "SecureBank App — microservices on Azure AKS.",
            "ELK Stack — Elasticsearch, Kibana, APM, Synthetics (existing).",
            "ServiceNow — Incident API, CMDB, assignment groups.",
            "Azure Functions — webhook receiver + agent orchestration.",
            "Azure OpenAI — plain-English root cause summary (optional).",
            "Azure Event Grid — reliable alert routing.",
        ],
        "Supporting Services",
        [
            "Azure API Management — secure API gateway.",
            "Azure Key Vault — secrets and credentials.",
            "Azure Entra ID — SSO and role-based access.",
            "Azure Blob Storage — immutable audit logs.",
            "Microsoft Teams — stakeholder notifications.",
            "React UI on Azure Static Web Apps — 3 simple screens.",
        ])
    # integration visual
    box(s, "SecureBank", 0.55, 5.55, w=1.5, h=0.42, fill=NAVY, fsize=8)
    box(s, "ELK", 2.3, 5.55, w=1.2, h=0.42, fill=ACCENT, fsize=8)
    box(s, "Azure\nFunctions", 3.75, 5.45, w=1.4, h=0.55, fill=TEAL, fsize=8)
    box(s, "ServiceNow", 5.4, 5.55, w=1.5, h=0.42, fill=ACCENT, fsize=8)
    box(s, "Ops Portal", 7.15, 5.55, w=1.5, h=0.42, fill=GREEN, fsize=8)
    for i in range(4):
        arrow(s, 2.05 + i * 1.45, 5.68)

    # ── 10 SIMPLE UI ─────────────────────────────────────────────────
    s = blank(prs); bg(s); bar(s, "9. Simple UI — 3 Screens Only (Phase 1)", "Clean, formal, easy — built for engineers not executives")
    screens = [
        ("① Incident List", "Status | Severity | Service | Time\nFilter: Open / Resolved", ACCENT),
        ("② Incident Detail", "What happened\nRoot cause (plain English)\nRecommended action", TEAL),
        ("③ Approve / Deny", "One-click approve or deny\nFix runs automatically\nAudit saved", GREEN),
    ]
    for i, (title, desc, color) in enumerate(screens):
        l = 0.55 + i * 3.05
        box(s, title, l, 1.12, w=2.75, h=0.55, fill=color, fsize=10)
        card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(1.78), Inches(2.75), Inches(1.55))
        card.fill.solid(); card.fill.fore_color.rgb = WHITE; card.line.color.rgb = BORDER
        tb = s.shapes.add_textbox(Inches(l + 0.1), Inches(1.92), Inches(2.55), Inches(1.3))
        p = tb.text_frame.paragraphs[0]; p.text = desc; p.font.size = Pt(11); p.font.color.rgb = SLATE
        if i < 2:
            arrow(s, l + 2.85, 1.32)
    bullets(s, [
        "Kibana remains the deep-dive analysis tool. Portal is for action and tracking only.",
        "Phase 2 adds: KPI dashboard, playbook editor, multi-system views.",
    ], top=3.55, sz=12)

    # ── 11 KPIs & CHARTS ─────────────────────────────────────────────
    s = blank(prs); bg(s); bar(s, "10. KPIs & Business Impact", "Measurable value — time saved, cost saved, availability gained")
    kpi_card(s, "MTTR", "75 → 15 min", 0.48, 1.1, GREEN)
    kpi_card(s, "Auto-Tickets", "100%", 2.65, 1.1, TEAL)
    kpi_card(s, "Toil Reduction", "40%", 4.82, 1.1, ACCENT)
    kpi_card(s, "Availability", "99.95%+", 6.99, 1.1, NAVY)
    add_bar_chart(s, 0.48, 2.15, 4.2, 2.6, ["Before AIR", "After AIR"], (75, 15), "MTTR (minutes)")
    add_pie_chart(s, 5.0, 2.05, 4.3, 2.75,
                  ["Auto-resolved", "Engineer-approved", "Manual (Phase 2)"], (45, 40, 15), "Incident Handling")
    bullets(s, [
        "5 incidents/week × 45 min saved = ~4 hours/week engineer time recovered.",
        "Faster transfer/payment recovery = fewer SLA penalties and customer complaints.",
        "100% audit coverage from day one — every action logged with timestamp and approver.",
    ], top=5.0, sz=11)

    # ── 12 SECURITY ──────────────────────────────────────────────────
    s = blank(prs); bg(s); bar(s, "11. Security, Compliance & Data Safety")
    cols(s,
        "What We Never Log",
        [
            "Customer names, account numbers, card data.",
            "Passwords, OTPs, actual balances.",
            "Real transaction amounts or payment details.",
        ],
        "How We Stay Safe",
        [
            "Only aggregated counts, masked IDs, latency, status codes.",
            "Azure Entra ID — role-based access (view vs approve vs admin).",
            "Key Vault for all secrets; managed identities for services.",
            "Human approval required for high-risk fixes (pod restart, DB scale).",
            "Immutable audit log — regulator-ready export.",
            "Same secure telemetry rules as SecureBank ELK reference architecture.",
        ])

    # ── 13 IMPLEMENTATION PLAN ───────────────────────────────────────
    s = blank(prs); bg(s); bar(s, "12. Implementation Plan — How We Will Deliver")
    phases = [
        ("Week 1–2", "Deploy SecureBank\non Azure AKS", ACCENT),
        ("Week 3–4", "Connect ELK alerts\nvia webhooks", TEAL),
        ("Week 5–6", "ServiceNow API\n+ 3 playbooks", NAVY),
        ("Week 7–8", "Simple UI +\nEnd-to-end demo", GREEN),
    ]
    for i, (wk, desc, color) in enumerate(phases):
        l = 0.55 + i * 2.25
        box(s, wk, l, 1.12, w=1.0, h=0.4, fill=color, fsize=9)
        card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(1.6), Inches(1.95), Inches(0.95))
        card.fill.solid(); card.fill.fore_color.rgb = WHITE; card.line.color.rgb = BORDER
        tb = s.shapes.add_textbox(Inches(l + 0.08), Inches(1.72), Inches(1.78), Inches(0.75))
        p = tb.text_frame.paragraphs[0]; p.text = desc; p.font.size = Pt(10); p.font.color.rgb = SLATE
        p.alignment = PP_ALIGN.CENTER
        if i < 3:
            arrow(s, 2.35 + i * 2.25, 1.78)
    bullets(s, [
        "Deliverable at Week 8: live demo of all 3 problems — detect → ticket → approve → fix → audit.",
        "Team needed: 1 backend dev, 1 frontend dev, 1 DevOps/SRE (part-time), ELK + SNOW access.",
        "No new monitoring investment — uses existing SecureBank + ELK setup from reference architecture.",
    ], top=2.75, sz=12)

    # ── 14 PHASE 2 ROADMAP ───────────────────────────────────────────
    s = blank(prs); bg(s); bar(s, "13. Phase 2 — Future Enhancements", "Same platform, new playbooks — no rebuild required")
    roadmap_items = [
        ("Now", "3 problems\nELK+SNOW+Azure\nSimple UI", ACCENT),
        ("Next", "Latency alerts\nChange intel\nCapacity ops", TEAL),
        ("Future", "Compliance auto\nMulti-tool adapters\nExecutive KPIs", NAVY),
    ]
    for i, (tag, desc, color) in enumerate(roadmap_items):
        l = 0.55 + i * 3.05
        box(s, tag, l, 1.12, w=0.85, h=0.4, fill=color, fsize=10)
        card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(1.62), Inches(2.75), Inches(1.45))
        card.fill.solid(); card.fill.fore_color.rgb = WHITE; card.line.color.rgb = BORDER
        tb = s.shapes.add_textbox(Inches(l + 0.12), Inches(1.78), Inches(2.5), Inches(1.15))
        p = tb.text_frame.paragraphs[0]; p.text = desc; p.font.size = Pt(12); p.font.color.rgb = SLATE
        if i < 2:
            arrow(s, l + 2.85, 1.28)
    add_pie_chart(s, 0.55, 3.35, 3.8, 2.5,
                  ["Phase 1\n(3 problems)", "Phase 2\n(+5 domains)", "Phase 3\n(+multi-cloud)"],
                  (30, 45, 25), "Platform Growth")
    bullets(s, [
        "Phase 2 adds new problem playbooks and UI screens — core platform code stays the same.",
        "Adapter pattern: plug in PagerDuty, Jira, Splunk, Datadog when needed.",
        "Each new use case = days of config, not months of development.",
    ], left=4.6, top=3.35, w=4.9, h=2.5, sz=11)

    # ── 15 SUMMARY & OUTCOME ─────────────────────────────────────────
    s = blank(prs); bg(s); bar(s, "14. Summary — Everything in One View")
    bullets(s, [
        "WHAT: Tensai Agentic Solution — connects ELK + ServiceNow + Azure to auto-diagnose and fix SecureBank incidents.",
        "WHY: Cut MTTR by 70%, reduce manual toil by 40%, improve availability, full audit trail.",
        "WHO: NOC, SRE, and SecOps teams — simple 3-screen portal, no training needed.",
        "HOW: ELK alert → Azure agent → SNOW ticket → engineer approves → fix runs → audit saved.",
        "WHEN: Phase 1 in ~8 weeks — 3 proven problems, live demo, production-ready path.",
        "NEXT: Phase 2 extends to latency, change, capacity, compliance — same platform, zero rebuild.",
    ], top=1.12, sz=13)
    banner = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.48), Inches(5.5), Inches(9.05), Inches(0.72))
    banner.fill.solid(); banner.fill.fore_color.rgb = NAVY; banner.line.fill.background()
    bt = s.shapes.add_textbox(Inches(0.65), Inches(5.65), Inches(8.7), Inches(0.45))
    bp = bt.text_frame.paragraphs[0]
    bp.text = "Detect  →  Diagnose  →  Ticket  →  Fix  →  Audit   |   Tensai Agentic Solution"
    bp.font.size = Pt(15); bp.font.bold = True; bp.font.color.rgb = WHITE; bp.alignment = PP_ALIGN.CENTER

    prs.save(OUTPUT)
    print(f"Saved: {OUTPUT}  ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
